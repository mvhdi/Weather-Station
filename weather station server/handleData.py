#!/usr/bin/python

#**************************************************************
#* Notes: This file contains two classes: DataReader and      *
#* DataOutputter. DataReader is responsible for reading and   *
#* storing raw data from the PIC. Its methods are scheduled in* 
#* main.py by the WeatherCollector and used in convert.py     *
#* by DataConverters that need raw data. DataOutputter is     * 
#* responsible for collecting, formatting, and saving         *
#* converted data. Its methods are also scheduled in main.py. *
#* DataConverters give DataOutputter converted data as they   *
#* finish converting it.                                      *
#**************************************************************

import errors
import Config

import serial																				#see https://pythonhosted.org/pyserial/index.html
import traceback
import sys
import time
import os

from shutil import copyfile
#===========================================================================================================
#												DATAREADER:
#===========================================================================================================
class DataReader:
	"""Essentially a wrapper for the serial port that allows data to be requested by label."""
##CONSTRUCTOR===============================================================================================
	def __init__(self):
		"""
		Constructor for DataReader. Responsible for initializing locations,
		a dictionary keying (string, index) by field label, from picdata.conf.
		If this fails, method will raise SystemExit. Also opens serial connection 
		as configured in Config.py. If connection fails at first, method will 
		continue attempting indefinitely.
		"""
		errors.debug("DataReader initializing...")																					
		self.locations = {}																	#this code reads picdata.conf and turns it into a dictionary,
		index = 0																			#keyed by field label holding a tuple of string name and index in string (from 0):
		current_string = None																#in essence, the dictionary created here asks for the string's label and gives its location.
																							#it will be used to tell the DataReader where to look for data that is requested
		self.expected_strings = {}															#expected_strings keys each string expected to its length
		errors.debug("Attempting to parse picdata.")
		try:																				
			copyfile('picdata.conf', 'picdata.conf.cache')
			with open('picdata.conf.cache', 'r') as picdata:								#open the file containing expected format
				for line in picdata:														#iterate though each line
					line = line.strip('\n')													#clean the line of return characters
					if line != '' and line[0] != "#":										#skip empty lines and comments
						if len(line) >= 4 and line[:4] == "STR:":							#if "STR:" tag is present, register the start of a new string
							index = 0														#start counting index from zero
							current_string = line[4:].strip()								#save string as current string
							errors.debug("Registered string " + current_string)
						else:																#if "STR:" tag is not present, the line must contain the name of a field
							if line in self.locations:
								errors.info("Warning: picdata.conf contains label " + 
									line + " multiple times. Only the last instance will be kept.")
							if current_string is None:
								errors.info("Warning: picdata.conf is improperly formatted, " +
									"contains label without string header.")
							else:
								self.locations[line] = (current_string, index)				#add an entry to the dictionary holding the string it is in and the index in that string
								index +=1													#increment the index for next time
						self.expected_strings[current_string] = index
			errors.debug("Parsed picdata.conf successfully.")

			for label in self.locations:					################################
				print label, self.locations[label], "\n"	################################
			print "self.expected_strings ->", self.expected_strings
				
																							#in the case of errors, send a message and then exit the program:
		except IOError:																		#error in finding or reading file (if thrown, most likely picdata.conf does not exist)
			errors.error("FATAL: DataReader unable to read picdata.conf. " + 
				"TS-4200 will not be able to interpret strings received from PIC until fixed. " + 
				"main.py exiting. Error message: " + 
				traceback.format_exc(Config.TRACEBACK_LIMIT))
			errors.sendEmail()
			errors.debug("Preparing to exit...")
			sys.exit("Unable to read picdata.conf")
		except (IndexError, KeyError):														#error in adding entry or slicing string (very unlikely, this is here just in case)
			errors.error("FATAL: DataReader unable to parse picdata.conf. " + 
				"Error is either in parser or in format of picdata.conf. main.py " +
				"exiting. Error message: " + traceback.format_exc(Config.TRACEBACK_LIMIT))
			errors.sendEmail()
			errors.debug("Preparing to exit...")
			sys.exit("Unable to parse picdata.conf")
		except:																				#unexpected error of some other sort
			errors.error("FATAL: unexpected error in parsing picdata.conf. main.py " +
				"exiting. Error message: " + traceback.format_exc(Config.TRACEBACK_LIMIT))
			errors.sendEmail()
			errors.debug("Preparing to exit...")
			sys.exit("Unable to parse picdata.conf")


		
		self.connectionFailures = 0 
		while True:																			#try to establish connection to serial port:
			try:
				errors.debug("Attempting serial port connection...")
				self.port = serial.Serial(													#create a Serial object to represent the port
					port=Config.PORT_NUM, 
					baudrate=Config.BAUD_RATE, 
					timeout=Config.PORT_TIMEOUT)
				if self.connectionFailures > 1:												#alert to success if connection has failed previously
					errors.sendEmail(message="Serial connection successful, initialization continuing.",
						subject="TS-4200 Serial Connection Successful")
				errors.log.error("Serial connection successful.")
				break																		#exit loop if successful
			except serial.SerialException:													#at two fails, log and send an email
				self.connectionFailures += 1
				if self.connectionFailures==2 or self.connectionFailures%4320 == 0:			#at two fails or every 6 hours, log and send an email
					errors.sendEmail(message="Failed to connect to serial port. " +
						"TS-4200 not functional until further notice. " + 
						"Attempts to connect will continue indefinitely. " +
						"Error message: " + traceback.format_exc(Config.TRACEBACK_LIMIT), 
						subject="TS-4200 Failed to Connect to Serial Port")
				errors.debug("Serial connection failed.")
				time.sleep(5)																#not much point in running the rest of the program without a serial connection, 																					#so try until success																					#initialize various flags to keep track of errors:
		self.consecutiveEmptyStrings = 0													#number of strings consecutively not received from PIC
		self.totalEmptyStrings = 0															#total number of strings not received since start up or last reset
		self.PICStringIDErrorState = False													#whether or not there is an outstanding unrecognized string coming from PIC
		self.PICFormatErrorState = False													#whether or not there is an string of the wrong length coming from PIC
																							#note that the above two will mask other errors of their sort until the first is fixed
																							#(i.e., two unrecognized strings are sent repeatedly but only one is reported at first)
		self.totalBadStrings = 0															#number of received strings since start up or reset for which there was some error
		self.badFormatErrors = []															#hold every field/string requested by DataConverters that was not found

		self.dataStrings = {}																#create empty dictionary to hold data
		open(Config.COMMAND_FILE_PATH, 'a').close()
		self.command_error = False
		errors.debug("DataReader initialization completed.")

##GET DATA BY LABEL===============================================================================================
	def get(self, label):
		"""
		Given a label, returns that label's stored data as a string. If no
		such label is found in the given format or if the corresponding data 
		point is not found in received data, registers an error message.
		Errors are stored in a list as the name (label, stringID, or ID+index)
		of the missing location. If a location is already in the list, email 
		will not be resent. These errors are expected to handle cases of
		typos in picdata.conf or data converting code, missing strings, and
		so on. This method does not check type -- calling methods get either
		the raw data exactly as received (as a string) or Config.ERROR_VAL. 
		Be sure NOT to use this method to request the name of a string (eg, B or T).
		"""
		try:
			tup = self.locations[label]														#try to retrieve information about the requested field from self.locations
		except KeyError:																	#if info retrieval throws error, notify...
			if label not in self.badFormatErrors:
				errors.error("NO RAW DATA ERROR: data for '" + label + "' requested, but no such " + 
					"label found. Either label not added to picdata.conf or misspelled " + 
					"somewhere. Error message: " + traceback.format_exc(Config.TRACEBACK_LIMIT) +
					"Assume error continues until otherwise notified.")
				self.badFormatErrors.append(label)											#...and add to list of errors...
			#errors.debug("get called but data for " + label + " not returned.")
			raise DataMissingError(label)													#...and return None, so calling method knows there is no data 
		else:
			try:
				self.badFormatErrors.remove(label)											#if that succeeds, try to remove label from the list of missing data...
				errors.debug("get called on " + label + " successful, removing error flag.")#this little error sub-system is too subtle for comments -- see documentation
			except:
				pass																		#...but don't worry if it wasn't there in the first place

		try:																				#using the information from self.locations, 
			stringID = tup[0]
			index = tup[1]
			data = self.dataStrings[stringID][index]										#try to find data for the requested label
			try:																			#if that succeeds, remove location from list of missing 
				self.badFormatErrors.remove(stringID+str(index))
				errors.debug("get called on " + stringID + str(index)+ " successfully, removing error flag.")
			except:
				pass
			try:																			#if that succeeds, remove stringID from list of missing
				self.badFormatErrors.remove(stringID)
				errors.debug("get called on member of string " + stringID + " successfully, removing error flag.")
			except:
				pass
		except KeyError:																	#handle errors. these will only be called if there is a missing string or
			if stringID not in self.badFormatErrors:										#some other corruption of data betweed the calling of read() and get()
				errors.error("String '" + stringID + "' not found among received data: mismatch " +
				"between picdata.conf and requested data, probably. Error message: " + 
				traceback.format_exc(Config.TRACEBACK_LIMIT) + " Assume error continues until " + 
				"otherwise notified.")
				self.badFormatErrors.append(stringID)
			errors.debug("get called but data for " + label + " not returned.")
			raise DataMissingError(label)	
		except IndexError:																	#this particular case should hardly ever be reached, but is here for completeness.
			if stringID+str(index) not in self.badFormatErrors:
				errors.error("Data field " + stringID +  str(index) + " not found among received data: " +
				"mismatch between picdata.conf and requested data. Error message: " + 
				traceback.format_exc(Config.TRACEBACK_LIMIT) + " Assume error continues until " + 
				"otherwise notified.")
				self.badFormatErrors.append(stringID + str(index))
			errors.debug("get called but data for " + label + " not returned.")
			raise DataMissingError(label)		
		return data 																		#return data as a string. methods calling get() will be responsible for type-checking.

##HELPER METHODS===============================================================================================
	def numStrings(self):
		"""Returns the number of PIC strings in the current format."""
		return len(self.expected_strings)

	def numBadStrings(self, reset=False):
		"""Returns the number of bad (empty or misformatted strings) received since 
		last reset or start up. Also resets counters and flags if reset is True."""
		val = self.totalBadStrings															#store value to return
		if reset:																			#if specified, reset all flags and counters
			self.totalBadStrings = 0
			self.totalEmptyStrings = 0
			self.consecutiveEmptyStrings = 0
			self.PICStringIDErrorState = False
			self.PICFormatErrorState = False	
			self.badFormatErrors = []
			self.command_error = False
		return val

	def send(self, cmd):
		"""Sends string cmd to PIC via serial connection."""								#flush input so that input doesn't build up in serial port -- 
		self.port.write(cmd)														#we want only data sent in response to S
		errors.debug("Sent " + cmd + " to PIC.")


	def build_file_for_dash(self):															#overwrites the file for dash with raw data.
		errors.debug("Data reader building file of raw data for dash board...")
		with open('picdata.conf.cache', 'r') as picdata:									#dataoutputter will pick this file up and append converted data to it
			with open('data_for_dash', 'w') as fordash:
				fordash.write(str(time.time()) + '\n')
				for line in picdata:
					line= line.strip()
					if line == "" or line[0] == "#":
						pass
					elif len(line) > 4 and line[:4] == "STR:":
						fordash.write("RAW\t" + line[4:].strip() + '\n')
					else:
						try:
							raw = self.get(line)
						except DataMissingError:
							raw = "not received"
						fordash.write(line + '\t' + raw + '\n')
						#print line + '\t' + raw + '\n'
		errors.debug("Done building raw data file for dash.")


##READ DATA FROM SERIAL PORT====================================================================================
	def read(self, header, header_1, toggle):
		"""
		Reads strings of raw data from serial port and checks them for
		errors before saving them in a dictionary. The strings that make
		it through this method are guaranteed to have the right ID and 
		length, but any given piece of data could conceivably be missing ("").
		Checking that data exist is the job of get().
		"""
		raw_data_list = header
		raw_array_data_list = header_1
		string_list = []
		self.dataStrings = {}																#clearing data
		errors.debug("read() called, getting data...")
		strings = []			
		print str(self.numStrings()) + " from read() in DataReader"						#ENTER LOOP
		self.port.write("SS")
		string_B = self.port.readline(size=None, eol='\r')
		time.sleep(1.1)
		string_B = 	string_B.split('\t')
		string_list.append(string_B)
		self.port.write("QQ")
		self.port.write("11")
		time.sleep(7)
		string_1 = self.port.readline(size=None, eol='\r')
		time.sleep(1.1)
		string_1 = 	string_1.split('\t')
		string_list.append(string_1)
		self.port.write("22")
		string_2 = self.port.readline(size=None, eol='\r')
		time.sleep(1.1)
		string_2 = 	string_2.split('\t')
		string_list.append(string_2)
		self.port.write("33")
		string_3 = self.port.readline(size=None, eol='\r')
		time.sleep(1.1)
		string_3 = 	string_3.split('\t')
		string_list.append(string_3)
		self.port.write("44")
		string_4 = self.port.readline(size=None, eol='\r')
		time.sleep(1.1)
		string_4 = 	string_4.split('\t')
		string_list.append(string_4)
		for i in range (len(string_list)):
			string = string_list[i]
			badstring = 1																
			if string == "":																#if data read is empty...
				self.totalEmptyStrings += 1													#increment the relevant counters, and
				self.consecutiveEmptyStrings +=1
				errors.debug("Received empty string from PIC.")
				with open("pic_status", 'w') as pic_status:
					pic_status.write("0")
				if self.consecutiveEmptyStrings == Config.MISSED_CONSECUTIVE_STRING_WARNING:#send a warning if necessary
					downtime = int((self.consecutiveEmptyStrings/3)/self.numStrings())
					errors.error("PIC has been unresponsive for " + str(downtime) + " minutes.")
			else:																			#if string is not empty...
				with open("pic_status", 'w') as pic_status:
					pic_status.write("1")
				if self.consecutiveEmptyStrings > Config.MISSED_CONSECUTIVE_STRING_WARNING:	#send a notification that PIC is responsive, if necessary
					errors.error("Received string from PIC after " + 
						str(self.consecutiveEmptyStrings) + " consecutive missed strings.")
				self.consecutiveEmptyStrings = 0											#reset consecutiveEmptyStrings counter												#make the string into a list to better manipulate it
			stringID = string[0]														#save the ID (the first item in the list)
			string = string[1:]															#BUILD DATA STRING and check for missing data:												#put each datum into a list														
			print "self.expected_strings", self.expected_strings						#remove the ID from the string
			if stringID not in self.expected_strings:									#if the ID is not recognized...
				if not self.PICStringIDErrorState:										#notify as appropriate
					errors.error("Received unexpected string from PIC starting with " + stringID + 
						". Assume error continues until intervention. Data will be lost " +
						"if strings of the expected format are not received.")
				else: 
					errors.debug("Received bad string from PIC starting with " + stringID + ".")
				self.PICStringIDErrorState = True										#and raise error flag
			else:																		#if ID is recognized...
				errors.debug("String of ID " + stringID + " found.")
				expectedLength = self.expected_strings[stringID]
				if len(string) != expectedLength:										#check if it is the expected length
					if not self.PICFormatErrorState:									#if not, notify as appropriate
						errors.info("Received bad string from PIC: " + str(len(string)) + 
							" fields instead of " + str(expectedLength) + " fields in string " + stringID +
							". Assume error continues until intervention. Data will be lost " +
							"if strings of the expected format are not received. Any strings not " + 
							"conforming to expected format can not be processed.")
					else:
						errors.debug("Received bad string from PIC: " + str(len(string)) + 
							" fields instead of " + str(expectedLength) + " fields.")
					self.PICFormatErrorState = True										#and raise error flag
				else:																	#if it is the expected length, then accept it
					errors.debug("String accepted.")
					self.dataStrings[stringID] = string 								#add it to dictionary of data
					badstring = 0														#mark it as a good string

			self.totalBadStrings += badstring
		string_B = string_B[1:]
		string_1 = string_1[1:]
		string_2 = string_2[1:]
		string_3 = string_3[1:]
		string_4 = string_4[1:]
		len_string_1 = len(string_1)
		len_string_B = len(string_B)
		len_string_2 = len(string_2)
		len_string_3 = len(string_3)
		len_string_4 = len(string_4)
		exp_len_string_1 = self.expected_strings['1']
		exp_len_string_B = self.expected_strings['B']
		exp_len_string_2 = self.expected_strings['2']
		exp_len_string_3 = self.expected_strings['3']
		exp_len_string_4 = self.expected_strings['4']
		if (len_string_1 == 0):
			for i in range (exp_len_string_1):
				string_1.append(str(Config.ERROR_VAL))
		if (len_string_B == 0):
			for i in range (exp_len_string_B):
				string_B.append(str(Config.ERROR_VAL))
		if (len_string_2 == 0):
			for i in range (exp_len_string_2):
				string_2.append(str(Config.ERROR_VAL))
		if (len_string_3 == 0):
			for i in range (exp_len_string_3):
				string_3.append(str(Config.ERROR_VAL))
		if (len_string_4 == 0):
			for i in range (exp_len_string_4):
				string_4.append(str(Config.ERROR_VAL))
		for item in string_1:
			raw_data_list.append(item.strip())	
		for item in string_B:
			raw_data_list.append(item.strip())	
		for item in string_2:
			raw_array_data_list.append(item.strip())	
		for item in string_3:
			raw_array_data_list.append(item.strip())	
		for item in string_4:
			raw_array_data_list.append(item.strip())												#add to counter if string was not good																					#and repeat
		raw_data_string = "\t".join(raw_data_list) + '\n'
		raw_array_data_string = "\t".join(raw_array_data_list) + '\n'
		if (not os.path.exists(Config.CUR_BACKUP_PATH)):
			os.makedirs(Config.CUR_BACKUP_PATH)
		if os.path.ismount(Config.FLASH_BACKUP_DIREC_PATH):
			try:
				errors.debug("Attempting to write rawdata backup")
				with open(Config.RAW_DATA_BACKUP_PATH, 'a') as raw_data_backup:							#actually write data to file
					raw_data_backup.write(raw_data_string)
				errors.debug("...write successful.")
				self.to_unix_error = False
			except:
				errors.debug("Copy failed.")
			raw_data_backup.close()
			try:
				errors.debug("Attempting to write raw array data backup")
				with open(Config.RAW_ARRAY_DATA_BACKUP_PATH, 'a') as raw_array_data_backup:							#actually write data to file
					raw_array_data_backup.write(raw_array_data_string)
				errors.debug("...write successful.")
				self.to_unix_error = False
			except:
				errors.debug("Copy failed.")
		raw_array_data_backup.close()
		if (toggle == 1):													
			try:
				errors.debug("Attempting to write rawdata")
				with open(Config.RAW_DATA_FILE_PATH, 'w') as raw_data:							#actually write data to file
					raw_data.write(raw_data_string)
				errors.debug("...write successful.")
				self.to_unix_error = False
			except:
				errors.debug("Copy failed.")
			raw_data.close()
			try:
				errors.debug("Attempting to write raw array data")
				with open(Config.RAW_ARRAY_DATA_FILE_PATH, 'w') as raw_array_data:							#actually write data to file
					raw_array_data.write(raw_array_data_string)
				errors.debug("...write successful.")
				self.to_unix_error = False
			except:
				errors.debug("Copy failed.")
			raw_array_data.close()
		if (toggle == 0):													
			try:
				errors.debug("Attempting to write rawdata")
				with open(Config.RAW_DATA_FILE_PATH, 'a') as raw_data:							#actually write data to file
					raw_data.write(raw_data_string)
				errors.debug("...write successful.")
				self.to_unix_error = False
			except:
				errors.debug("Copy failed.")
			raw_data.close()
			try:
				errors.debug("Attempting to write raw array data")
				with open(Config.RAW_ARRAY_DATA_FILE_PATH, 'a') as raw_array_data:							#actually write data to file
					raw_array_data.write(raw_array_data_string)
				errors.debug("...write successful.")
				self.to_unix_error = False
			except:
				errors.debug("Copy failed.")
			raw_array_data.close()																				#EXIT LOOP																																					
		for stringID in self.expected_strings:												#check that each expected string was received
			if stringID not in self.dataStrings:											#if a string wasn't read,
				if stringID not in self.badFormatErrors:									#and isn't already broken,
					errors.error("Did not receive full string " + stringID + " from PIC. " +#send an alert
						"Assume error continues until otherwise notified. No data from " + 
						stringID + " available.")
					self.badFormatErrors.append(stringID)									#and add it to the list of broken strings
				else:
					errors.debug("Did not find string " + stringID + " again.")
			else:																			#if a string was read, make sure it isn't in the list of broken strings
				try:
					self.badFormatErrors.remove(stringID)									#alert that it is working again
					errors.error("Received previously missing string " + stringID + 
						". Assume problem solved until notified otherwise.")
				except:
					pass
		errors.debug("Done reading and storing data.")


##SEND COMMANDS TO PIC======================================================================================
	def send_commands(self):
		"""
		Reads files holding all commands for the PIC and sends them.
		Command file should be formatted as <cmd><tab><source>, with
		one command per line.
		"""
		errors.debug("Preparing to send commands to PIC.")
		try:
			with open(Config.COMMAND_FILE_PATH, 'r') as command_file:
				for line in command_file:
					command = line.split('\t')
					errors.debug(str(command))
					if len(command) > 2:
						self.port.write(command[0].strip())
						if command[1].strip() == "DASH":
							errors.info("TS-4200 sent command " + command[0] + " from source " + command[1].strip() + " to PIC via serial.")
						else:
							errors.debug("Sent command " + command[0] + " from source " + command[1].strip())
		except:
			if not self.command_error:
				self.command_error = True
				errors.error("Error in reading and sending commands. Error message: " + 
					traceback.format_exc(Config.TRACEBACK_LIMIT))
		else:
			open(Config.COMMAND_FILE_PATH, 'w').close()

##TESTING===================================================================================================


class DataMissingError(Exception):
	def __init__(self, label):
		self.value = "DataReader does not have raw data for " + label + "."
	def __str__(self):
		return repr(self.value)

class NoSuchLabelError(Exception):
	def __init__(self, label):
		self.value = "DataReader does not have record of any label " + label + "."
	def __str__(self):
		return repr(self.value)

#===========================================================================================================
#												DATAOUTPUTTER:
#===========================================================================================================
class DataOutputter:
	"""Handles outputting data."""
##CONSTRUCTOR===============================================================================================
	def __init__(self):
		"""Parses outdata.conf into a list, makes a document holding
		format of data to dashboard, and initializes error flags."""
		self.format = []																	#this list holds labels of outgoing data in order
		try:
			open("dashformat.txt", 'w').close()												#clear dashformat.txt
			with open("dashformat.txt", 'a') as dashformat:									#open dashformat.txt
				with open("outdata.conf", 'r') as outdata:									#open outdata.conf
					for line in outdata:													#iterate through each line
						if line == '\n' or line[0] == "#":									#ignore empty lines or lines that start with '#'
							pass
						elif line[:4] == "STR:":
							dashformat.write(line)
						else:																#append what's left to self.format and dashformat.txt
							self.format.append(line.strip('\n'))
							dashformat.write(line)		
																							#in the case of errors, send a message and then exit the program:
		except IOError:																		#error in finding or reading file (if thrown, most likely outdata.conf does not exist)
			errors.error("FATAL: DataOutputter unable to read outdata.conf. " + 
				"TS-4200 will not be able to output data until fixed. " + 
				"main.py exiting. Error message: " + 
				traceback.format_exc(Config.TRACEBACK_LIMIT))
			errors.sendEmail()
			errors.debug("Preparing to exit...")
			sys.exit("Unable to read outdata.conf")

		except:																				#unexpected error of some other sort
			errors.error("FATAL: unexpected error in parsing outdata.conf. main.py " +
				"exiting. Error message: " + traceback.format_exc(Config.TRACEBACK_LIMIT))
			errors.sendEmail()
			errors.debug("Preparing to exit...")
			sys.exit("Unable to parse outdata.conf")

		self.data = {}																		#a dictionary keying label to converted data
		self.unrecognized_labels = []														#initialize error flags/lists:
		self.missing_data = []
		self.to_unix_error = False
		self.temp_backup_error = False
		self.flash_file_error = False
		self.flash_drive_error = False
		self.for_dash_error = False
		open("temp_unix_backup", 'w').close()												#initialize backup file


##RECEIVE CONVERTED DATA====================================================================================
	def receive(self, label, data):
		"""
		Pass data (in any format) for field <label> to this outputter. Called by
		DataConverters once they have finished converting data.
		Outputter will store the data and ultimately format/save it.
		"""
		if label in self.format:															#if label is recognized, save its data
			self.data[label] = data
			if label == "rain_drip_code":
				print "Received rain_drip_code"
		elif label not in self.unrecognized_labels:											#if not, and label not already registered as unrecognized, send an error and add it
			errors.error("Unrecognized label " + label + " passed to DataOutputter. " +		#to the list of unrecognized labels
				"Be sure outdata.conf is updated to include all outgoing data fields " +
				"referenced in code. Error will persist until fixed. Possible causes: " + label + 
				" not added to outdata.conf, misspelled somewhere, or removed from outdata.conf " +
				"but not code.") 
			self.unrecognized_labels.append(label)

##GET CONVERTED DATA========================================================================================
	def get_converted(self, label):
		"""Recover converted data from outputter. Used for second-level conversions."""
		return self.data[label]

##SAVE DATA TO FILES========================================================================================
	def save(self, header, toggle):
		"""
		Formats all received converted data and saves it to the 
		appropriate configuration of files. Clears all data so outputter
		is available to receive a new batch.
		"""
		data_list = header													#BUILD DATA STRING and check for missing data:
		for label in self.format:														#for each expected piece of data
			try:
				data = str(self.data[label])												#request it from self.data
			except KeyError:																#if it is not found, send an alert
				if label not in self.missing_data:											#note that this alert applies only to data not sent at all -- data noted as missing earlier will
					errors.error("DataOutputter missing data for label " + label + 			#have been replaced by an error value and so will not throw this error.
						". Probable cause: no data converter passes data to outputter." +	#this error should just catch coding mistakes (such as a piece of expected data not being passed to
						" Problem will continue until fixed.")								#the outputter for whatever reason)
					self.missing_data.append(label)
				data = str(Config.ERROR_VAL)												#...and replace it with the error value
			data_list.append(data)															#put each datum into a list
		data_string = "\t".join(data_list) + '\n'											#turn the list into a string
		self.data = {}
		if (not os.path.exists(Config.CUR_BACKUP_PATH)):
			os.makedirs(Config.CUR_BACKUP_PATH)																			#clear data
		
		try:
			errors.debug("Attempting to write oneline")
			with open(Config.ONE_LINE_FILE_PATH, 'w') as one_line:							#actually write data to file
				one_line.write(data_string)
			errors.debug("...write successful.")
			self.to_unix_error = False
		except:
			errors.debug("Copy failed.")
		if (toggle == 1):																		#WRITE TO 2UNIX:
			try:																				#this try block copies over backed up data to 2UNIX in case of interference or failure
				errors.debug("Copying temp_backup over to 2UNIX...")							#this is a plan C, very unlikely to be needed.
				with open("temp_unix_backup", 'r') as backup:									
					missing_data = backup.read()
				with open(Config.TO_UNIX_FILE_PATH, 'w') as to_unix:
					to_unix.write(missing_data)
				open("temp_unix_backup", "w").close()
			except:
				errors.debug("Copy failed.")

			try:
				errors.debug("Attempting to write to 2UNIX...")
				with open(Config.TO_UNIX_FILE_PATH, 'w') as to_unix:							#actually write data to file
					to_unix.write(data_string)
				errors.debug("...write successful.")
				self.to_unix_error = False
			except IOError:
				time.sleep(.1)																	#if it fails, wait and try again
				errors.debug("...write failed, trying again.")
				try:
					with open(Config.TO_UNIX_FILE_PATH, 'w') as to_unix:						#try to write again
						to_unix.write(data_string)
						errors.debug("Second write successful.")
						self.to_unix_error = False
				except IOError:																	#if that fails, put data in a backup
					errors.debug("Second write failed.")
					if not self.to_unix_error:
						errors.error("Unable to write to file for database. Storing unsent data in a temporary backup.")
						self.to_unix_error = True
					try:
						with open("temp_unix_backup", 'w') as backup:
							backup.write(data_string)
						errors.debug("Wrote data to backup.")
						self.temp_backup_error = False
					except:																		#if the backup fails, not much more that can be done
						if not self.temp_backup_error:
							errors.error("Write to temporary backup failed. Data will not be written to 2UNIX.")
							self.temp_backup_error = True
					else:
						errors.debug("Write to 2UNIX failed again.")
		if (toggle == 0):																		#WRITE TO 2UNIX:
			try:																				#this try block copies over backed up data to 2UNIX in case of interference or failure
				errors.debug("Copying temp_backup over to 2UNIX...")							#this is a plan C, very unlikely to be needed.
				with open("temp_unix_backup", 'r') as backup:									
					missing_data = backup.read()
				with open(Config.TO_UNIX_FILE_PATH, 'a') as to_unix:
					to_unix.write(missing_data)
				open("temp_unix_backup", "w").close()
			except:
				errors.debug("Copy failed.")

			try:
				errors.debug("Attempting to write to 2UNIX...")
				with open(Config.TO_UNIX_FILE_PATH, 'a') as to_unix:							#actually write data to file
					to_unix.write(data_string)
				errors.debug("...write successful.")
				self.to_unix_error = False
			except IOError:
				time.sleep(.1)																	#if it fails, wait and try again
				errors.debug("...write failed, trying again.")
				try:
					with open(Config.TO_UNIX_FILE_PATH, 'a') as to_unix:						#try to write again
						to_unix.write(data_string)
						errors.debug("Second write successful.")
						self.to_unix_error = False
				except IOError:																	#if that fails, put data in a backup
					errors.debug("Second write failed.")
					if not self.to_unix_error:
						errors.error("Unable to write to file for database. Storing unsent data in a temporary backup.")
						self.to_unix_error = True
					try:
						with open("temp_unix_backup", 'a') as backup:
							backup.write(data_string)
						errors.debug("Wrote data to backup.")
						self.temp_backup_error = False
					except:																		#if the backup fails, not much more that can be done
						if not self.temp_backup_error:
							errors.error("Write to temporary backup failed. Data will not be written to 2UNIX.")
							self.temp_backup_error = True
					else:
						errors.debug("Write to 2UNIX failed again.")


																						#COPY FROM LOCAL TO FLASH DRIVE BACKUP (in case of flash drive coming back online)
		if os.path.ismount(Config.FLASH_BACKUP_DIREC_PATH) and not self.flash_file_error:	#checking whether drive is mounted so that code does not save to local file at same path						
			try:
				errors.debug("Copying local backup to flash.")								#try copying local backup to flash drive. if no data in local backup, just append nothing
				with open(Config.LOCAL_BACKUP_FILE_PATH, 'r') as local:						#open and read data from local backup
					forFlash = local.read()
				with open(Config.TO_UNIX_BACKUP_PATH, 'a') as flash:			#append data to flash backup
					flash.write(forFlash)
				open(Config.LOCAL_BACKUP_FILE_PATH, 'w').close()							#clear local backup if successful
				self.flash_file_error = False
			except:
				if not self.flash_file_error:
					errors.info("Copy from local to flash failed, but flash drive mounted. " + 
					 "Beware discontinuity in data starting around current time. " +
					 "Error message: " + traceback.format_exc(Config.TRACEBACK_LIMIT))
				os.system("sudo umount /dev/sda1")											#unmount flash drive 
				self.flash_file_error = True
		else:
			errors.debug("Flash unmounted, copy from local to flash not attempted.")

																						#BACKUP DATA ON FLASH DRIVE
		if os.path.ismount(Config.FLASH_BACKUP_DIREC_PATH):									#if flash drive is mounted:
			try:																			#try writing data to backup on flash drive
				with open(Config.TO_UNIX_BACKUP_PATH, 'a') as flash:			#open file and write data
					flash.write(data_string)
					if self.flash_drive_error:												#if it didn't work last time, alert that it is working
						errors.error("Write to flash drive successful -- flash backup online.")
						self.flash_drive_error = False
					else:
						errors.debug("Data written to flash drive successfully.")
			except:																			#if failure, alert as appropriate and write data to local backup instead
				if not self.flash_drive_error:
					errors.error("Flash drive mounted, but unable to write to flash backup. " +
						"Error message: " + traceback.format_exc(Config.TRACEBACK_LIMIT))
				self.flash_drive_error = True
		else:
			if not self.flash_drive_error:
				errors.error("Flash drive unmounted. TS-4200 unable to write to backup file on flash drive. " +
				"Data diverted to local filesystem backup until notified otherwise.")
			else:
				errors.debug("Flash drive still unmounted, diverting data to local backup.")
			self.flash_drive_error = True

																						#IF FLASH DRIVE UNMOUNTED, WRITE TEMPORARILY TO LOCAL BACKUP
			try:	
				with open(Config.LOCAL_BACKUP_FILE_PATH, 'a') as local:						#open and write data to local backup
					local.write(data_string)
			except:
				errors.error("BACKING UP FAILED: unable to write to either flash " + 
					"or local backup. Error message: " + 
					traceback.format_exc(Config.TRACEBACK_LIMIT))

		self.data_list = data_list
##DAILY RESET===============================================================================================
	def reset(self):
		"""Resets error flags and lists so notifications will be resent."""
		self.unrecognized_labels = []
		self.missing_data = []
		self.to_unix_error = False
		self.temp_backup_error = False
		self.flash_file_error = False
		self.flash_drive_error = False

##BUILD FILE FOR DASH=======================================================================================
	def build_file_for_dash(self):
		index = 1																		#WRITE DATA FOR	DASHBOARD:
		errors.debug("Building converted data file for dash.")
		try:																			#this file will be read using pysftp by the dashboard application whenever it loads
			with open("data_for_dash", 'a') as fordash:									#open format file and data file
				with open("dashformat.txt", 'r') as dashformat:
					for line in dashformat:												#for each line in format file
						if line[:4] == "STR:":											#if the line is a string tag, copy it over	
							fordash.write("CVT\t" + line[4:].strip() + '\n')
						else:															#if it's a label, copy it over with data appended
							fordash.write(line.strip() +'\t' + self.data_list[index] + '\n')
							index += 1
		except IndexError:
			if not self.for_dash_error:
				errors.error("Error in parsing dashformat.txt; file may have been " +
					"corrupted. Dashboard may not display data properly or correctly." + 
					" Error message: " + traceback.format_exc(Config.TRACEBACK_LIMIT))
			else:
				errors.debug("Error in writing data_for_dash again, don't trust dashboard.")
			self.for_dash_error = True

		self.data_list = []

if __name__ == '__main__':
	george = DataOutputter()
	for i in range(20):
		errors.debug("===============NEW CYCLE==============")
		george.receive("mux_current", i)
		george.save()
		errors.sendEmail()
		time.sleep(15)
	george.reset()
	for i in range(20):
		errors.debug("===============NEW CYCLE==============")
		george.receive("mux_current", i)
		george.save()
		errors.sendEmail()
		time.sleep(15)
