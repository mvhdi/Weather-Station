#!/usr/bin/python

#**************************************************************
#* Notes: Schedules and executes various tasks.               *
#**************************************************************

import Config
import errors
from handleData import DataReader, DataOutputter
import convert
import DataConverters

import sched
import os
import signal
import time

#===================================================================================================================
#											WEATHERSCHEDULER CLASS DEFINITION
#===================================================================================================================
# The WeatherScheduler class serves only to order and schedule the functionality defined elsewhere. It
# uses python's sched module to space tasks, running a 20 second loop indefinitely. It receives the end
# signal and handles it. It also does space/RAM checks daily, and other small tasks.

class WeatherScheduler:

##INITIALIZE WEATHER SCHEDULER======================================================================================
	def __init__(self):
		"""
		Constructor for WeatherScheduler. Responsible for initializing
		instances of DataReader and DataOutputter and setting these to
		be used by DataConverters. Also initializes a scheduler from
		python's sched module.
		"""
		self.startup_time = time.time()														#get the current time
		t = "unknown"
		try:
			with open(Config.ONELINE_PATH, 'r') as last_time:
				t = float(last_time.read().split('\t')[0])									#get the last time logged 
		except:
			t = "unknown"

		try:
			downtime = int((self.startup_time - t)/60)										#calculate and alert how long Freya has been down
			errors.info("main.py restarting after " + str(downtime) + " minutes' downtime.")
		except TypeError:
			pass

		errors.debug("WeatherScheduler initializing.")
		self.reader = DataReader()															#initialize a DataReader to handle raw data 
		self.outputter = DataOutputter()													#initialize a DataOutputter to handle converted data
																							#see handleData for details on these
		DataConverters.DataConverter.set_in_out(											#tell all DataConverters to use the objects just created
									reader=self.reader, 
									outputter=self.outputter)			
		self.scheduler = sched.scheduler(time.time, time.sleep)								#create a scheduler to handle the main loop's timing

		self.cycles = 0																		#this counter will be used to tell daily_checks when to run
		self.sched_warning_sent = False 													#remember if a falling-behind-schedule warning has already been sent
		self.endToggle = False 																#this is set to true when a signal is received, and allows the
																							#program to exit gracefully at the end of a cycle
		signal.signal(signal.SIGUSR1, self.end) 											#initialize a signal handler to catch SIGUSR1 and call self.end()
		errors.debug("Set signal handler for SIGUSR1 to " + str(signal.getsignal(signal.SIGUSR1)))
		self.maybe_end()

##RUN WEATHERSCHEDULER===============================================================================================
	def run(self):
		"""
		This function waits until safe to get data from PIC, then runs
		the main loop forever, calling other functions as scheduled.
		"""
		still_to_wait = int(Config.WAIT_AT_STARTUP - (time.time() - self.startup_time))		#calculate how much longer to wait
		errors.debug("Waiting " + str(still_to_wait) + " seconds for PIC...")

		for i in range(int(still_to_wait/20)):												#wait, but periodically check if end signal has been received
			for j in range(19):
				time.sleep(1)
			self.maybe_end()

		errors.debug("Entering main loop.")
		self.last_cycle_started = time.time()
		while True:
			errors.debug("____________NEW CYCLE____________")
			errors.sendEmail()
			self.note_running()
			os.environ['TZ'] = 'CST+6'
			time.tzset()
			local_time = time.localtime()
			unix_time = str(time.time())
			year = str(local_time.tm_year)
			month = str(local_time.tm_mon)
			day = str(local_time.tm_mday)
			hour = str(local_time.tm_hour)
			minute = str(local_time.tm_min)
			second = str(local_time.tm_sec)
			clk_source = Config.NULL_VAL
			stardate = Config.NULL_VAL
			future = Config.NULL_VAL
			header = [unix_time, year, month, day, hour, minute, second, clk_source, stardate, future]
			header_1 = [unix_time, year, month, day, hour, minute, second, clk_source, stardate, future]
			header_2 = [unix_time, year, month, day, hour, minute, second, clk_source, stardate, future]
			toggleFile = open(Config.TOGGLE_FILE_PATH, 'r')
			toggle = toggleFile.readline()
			if toggle == '': 
				toggle = 0
			toggleFile.close()
			self.reader.read(header, header_1, int(toggle))
			convert.process_all()
			self.outputter.save(header_2, int(toggle))
			toggleFile = open(Config.TOGGLE_FILE_PATH, 'r')
			last_toggle = int(toggleFile.readline())
			toggleFile.close()
			toggleFile = open(Config.TOGGLE_FILE_PATH, 'w')
			if (last_toggle == 1 and int(toggle) == 0):
				toggleFile.write('1')
			else:
				toggleFile.write('0')
			toggleFile.close()  
			self.reader.send_commands()
			self.daily_checks()	
			self.finish_cycle()
			self.scheduler.run()

##DO DAILY TASKS====================================================================================================
	def daily_checks(self):
		"""
		Checks that various parts of the system are healthy: the PIC 
		is not missing strings repeatedly, the board has enough space
		and memory to run properly. Also resets all error flags. Runs
		only every 4320 cycles (24 hours @ 20s/cycle).
		"""
		self.build_file_for_dash()															#put together data for GUI
		errors.debug("daily_checks called.")
		os.system("sudo ts4200ctl --redledoff")												#turn off LED
		self.cycles +=1
		if self.cycles != 1:																#i.e., run only every 24 hours' worth of cycles
			errors.debug("daily_checks exiting without checking.")
			return

		errors.debug("Performing daily checks.")
		self.cycles = 0																		#reset counter
																							#the following 2 checks use the statvfs utility. see statvfs man pages.
																						#check space remaining on local filesystem:
		localStats = os.statvfs(Config.TO_UNIX_FILE_PATH)									#get statvfs data about local filesystem
		freeBytes = localStats.f_frsize * localStats.f_bavail								#free bytes = fragment size * number of fragments available to us
		if freeBytes < Config.FREE_BYTES_WARNING:											#check that this number is acceptable. if not, send an alert.
			errors.error("TS-4200 has " + str(freeBytes/1000000) + " MB remaining. " +
				"This is a serious and unforeseen error. Immediate corrective action " +
				"recommended to determine what is filling up the local filesystem.")

																						#check space remaining on flash drive
		if os.path.ismount(Config.FLASH_BACKUP_DIREC_PATH):									#only try if flash drive is mounted
			usbStats = os.statvfs(Config.FLASH_BACKUP_DIREC_PATH)							#same as previous, except passing statvfs the USB mount point
			freeBytes = usbStats.f_frsize * usbStats.f_bavail
			if freeBytes < Config.FREE_BYTES_WARNING:
				errors.error("Flash drive has " + str(freeBytes/1000000) + " MB remaining. " +
					"Freya will fill this at a rate of about 15MB/week. Replace flash drive.")
 
																						#check RAM usage
		with open("/proc/meminfo", 'r') as meminfo:											#open /proc/meminfo, a special file holding info about RAM usage
			meminfo.readline()																#extract statistics from successive lines of /proc/meminfo
			freemem = int(meminfo.readline().split()[1])									#unused memory is best estimated as "free memory" plus buffered and
			buffermem = int(meminfo.readline().split()[1])									#cached memory, since these are available to be overwritten if a
			cachemem = int(meminfo.readline().split()[1])									#process requires them.
			unusedmem = freemem + buffermem + cachemem
		if unusedmem < Config.UNUSED_MEMORY_WARNING:										#send warning if memory usage is too high
			errors.error("TS-4200 has only " + str(unusedmem) + " kB of " +
				"unused RAM. Speed and performance may be impacted, corrective action recommended.")

		PIC_bad_strings = self.reader.numBadStrings(reset=True)								#get number of bad strings and reset all flags in reader
		if PIC_bad_strings >= Config.TOTAL_BAD_STRING_WARNING:								#send an error if there are too many bad strings
			errors.info("TS-4200 has logged " + str(PIC_bad_strings) + " bad strings " + 
				"(unrecognized ID, wrong length, or unreceived) in last 24 hours. Probable " +
				"mismatch between PIC format and expected format. Be sure that picdata.conf " +
				"is updated to fit what the PIC is sending. Warnings should have been sent " +
				"when problems first happened -- check these for more information on what " +
				"might be going wrong.")
		else:
			errors.debug("Only " + str(PIC_bad_strings) + " bad strings for the day. No warning sent.")

		convert.reset_all_flags()															#resets all data converter error flags
		self.outputter.reset()																#resets outputter's error flags
		self.sched_warning_sent = False 													#reset schedule error flag
		open("text_for_dash", 'w').close()													#stop text_for_dash from ballooning

##MAKE FILES FOR DASH================================================================================================
	def build_file_for_dash(self):
		"""Tells reader and outputter to each add their data to file for GUI"""															
		self.reader.build_file_for_dash()													#call method of DataReader
		self.outputter.build_file_for_dash()												#call method of DataOutputter

	def note_running(self):
		"""Leave a timestamp in a file so GUI knows Freya is running"""
		with open("board_is_running", 'w') as b:											#write the current time to a file
			b.write(str(time.time()))
		errors.debug("Updated timestamp for dash.")

##END GRACEFULLY====================================================================================================
	def maybe_end(self):																	#checks if end signal has been received, and ends program if it has
		if self.endToggle:																	#this toggle is set by the signal handler below
			errors.info("Received end signal, terminating main.py. " +						#if ending, send email
						"Use startup.sh to restart.")										
			errors.sendEmail(subject="TS-4200 Stopping Operations")
			errors.debug("main.py exiting.")
			raise SystemExit 																#exit python
		os.system("sudo ts4200ctl --redledon")												#turn on LED
		self.note_running()																	#leave a timestamp for dash

	def finish_cycle(self):
		"""Called at the end of a cycle to wrap up"""
		self.maybe_end()																	#see above
		time_to_sleep = self.last_cycle_started + 29.9787 - time.time()						#calculate time to sleep. 19.9787 is 20s minus the average 
																							#time it takes to queue the next cycle
		if time_to_sleep < Config.BEHIND_SCHEDULE_WARNING:									#if behind schedule, send an alert and don't sleep
			if not self.sched_warning_sent:
				errors.info("main.py is falling behind schedule. Last cycle ended " + str(time_to_sleep)[1:] + " seconds late. Corrective action recommended.")
				self.sched_warning_sent = True
			else:
				errors.debug("Not sleeping before next cycle, already behind " +str(time_to_sleep)[1:]+ " seconds.")
		elif time_to_sleep < 0:
			errors.debug("Not sleeping before next cycle, already behind " +str(time_to_sleep)[1:]+ " seconds.")
		else:
			errors.debug("Seconds to next cycle: " + str(time_to_sleep))					#sleep until time for next cycle
			time.sleep(time_to_sleep)
		self.last_cycle_started = time.time()

	def end(self, signum, frame):															#this method catches the SIGUSR1 signal sent by end.sh and
		errors.debug("Received SIGUSR1.")													#sets endToggle to true. endToggle will be checked periodically, and
		self.endToggle = True																#if it is true the program ends (see above).


##MAIN CODE===========================================================================================================

def main():
	fred = WeatherScheduler()
	fred.run()

if __name__ == '__main__':
	main()
