#!/usr/bin/python

#**************************************************************
#* Notes: Holds functions for error logging and notification. *
#* These functions are called by various other parts of the   *
#* program when they need to send an email or log an error.   *
#**************************************************************

import time
import email
import email.Message
import os
import logging
import logging.handlers
import Config
import traceback
import smtplib
import socket
import signal
import multiprocessing


##LOGGING HELPER METHODS==============================================================================================
																				#each of these methods takes a message of the specified urgency level
def debug(msg):																	#and sends email or logs them depending on the configuration in Config.py
	"""Logs and emails debugging messages"""
	log.debug(msg)																#messages of level debug are used for tracking the operation of the program
	if Config.DEBUG_EMAILS:														#enabling debug generates a detailed, timestamped record of the program's operation
		queueEmail(msg)

def info(msg):																	#messages of level info are for warnings of mild importance:
	"""Logs and emails info messages"""											#checks of remaining space, memory use, and so on
	log.info(msg)
	if Config.INFO_EMAILS:
		queueEmail(msg)

def error(msg):																	#messages of level error are warnings of failures to accomplish some functionality
	"""Logs and emails error messages"""										#if something breaks, error messages will not be resent every cycle
	log.error(msg)																#an error message will, however, usually be sent when a broken thing unbreaks
	if Config.ERROR_EMAILS:
		queueEmail(msg)

##QUEUE EMAIL MESSAGE================================================================================================
																				#the approach taken here is to add errors to a file when they arise 
																				#and them send them all at once in digest form, every 20 seconds
def queueEmail(msg):															#this function adds the given message to file holding content of next email
	"""
	Adds msg to the file holding messages to be sent. During normal
	running, the queued messages will be sent at once every 20 seconds.
	"""
	try:
		with open(Config.EMAIL_FILE_PATH, 'a') as emailFile:					#open file
			emailFile.write(str(time.asctime()) + ": " + msg + '\n')			#append message to file
	except:
		log.error("Failed to write msg to email file. msg: "  + msg +			#if open or write fails, log error (do not email it)
			". Error message: " + traceback.format_exc(Config.TRACEBACK_LIMIT))

##SEND EMAIL ALERTS=============================================================================================================

def connect_and_send(msg, n):													#this function is only called by sendEmail (below)
	"""
	Connects to smtp server and sends string msg.
	Is run as a separate process to avoid blocking.
	n is a dummy argument, but necessary due to quirk in 
	multiprocessing lib, which calls tuple((msg)) and splits string 
	into a tuple of chars which it then passes to this function: not useful.
	"""
	try:
		debug("Attempting connection to mail server...")
		mailServer = smtplib.SMTP(Config.MAIL_SERVER_DOMAIN, 					#connect to mail server
									port=Config.MAIL_SERVER_PORT)
		debug("Mail server connection successful. Attempting send...")
		unsent = mailServer.sendmail(Config.EMAIL_SENDER,						#send message. sendmail returns a dict holding any errors (saved in "unsent") 
									Config.EMAIL_RECIPIENTS,
									msg)
		debug("Message sent successfully.")
	except:																		#respond to errors
		error("Failed to connect to mail server and send message. " +
			"Error message: " + traceback.format_exc(Config.TRACEBACK_LIMIT))
	try:																		#close connection to server...
		mailServer.quit()
		debug("Closing mail server.")
	except:																		#...but don't worry if server was never open
		pass
																																									

def sendEmail(message = "", subject = "TS-4200: Error Messages"):				#this function handles the sending of an email
	"""																			
	Two usage cases:
		If no message is specified, sends all pending emails.
		If message is specified, sends message.
	Times out after 5 seconds and handles all errors.
	"""																			
	if message != "":															#if a message was specified, store it as msgStr
		msgStr = message
	else:																		#if no message specified, prepare to email whole pending file	
		debug("sendEmail called. Preparing to send a cycle's worth of messages.")
		msgStr = ""																#initialize empty message
		try:
			with open(Config.EMAIL_FILE_PATH, 'r') as emailFile:
				msgStr = emailFile.read()										#read all messages from file
			debug("Email file read successfully.")								#store them as msgStr
		except IOError:															#catch and report failure to read
			error("Unable to read email file. Error message: " +
				traceback.format_exc(Config.TRACEBACK_LIMIT))
		if msgStr == "":														#if failure or no messages, exit
			debug("Empty message string, exiting sendEmail().")
			return

	msg = email.Message.Message()												#create empty message object (see https://docs.python.org/2/library/email.message.html for docs)
	msg.set_payload(msgStr)														#set message body
	msg['subject'] = subject													#set message subject
	msg = msg.as_string()														#get message as string

	try:																		#delegate another process to send the message using connect_and_send (above)
		send = multiprocessing.Process(target=connect_and_send, args=(msg, 1))	#this is a workaround to stop the function from eating 40s when there is no network connection
		send.start()															#start the process (see https://docs.python.org/2/library/multiprocessing.html)
		send.join(Config.MAIL_SERVER_TIMEOUT)									#wait for it to finish or 5 seconds, whichever comes first
		if send.is_alive():														#if the process is still going, end it. the SMTP constructor is a cranky beast
			send.terminate()													#which often doesn't end immediately if there's no network connection, 
																				#so the process may continue for another 30s or so.
																				#this should not be a problem, since two extra processes at a time should not clog up the works.
																				#but if things change, and these start to hang indefinitely (highly unlikely), this 
																				#could be a failure point.
																				#note that python signal and threading libraries are no more able to timeout the constructor than 
																				#multiprocessing, which I only chose because it's more transparent and easier to debug from outside
																				#TLDR: if the board is concerningly short on memory, look here first.

		exitcode = send.exitcode												#store exit code of process (see http://pymotw.com/2/multiprocessing/basics.html#process-exit-status)
		debug("Process is_alive: " + str(send.is_alive()))												
		if exitcode == 0:														#ie, if process exited successfully and on its own
			debug("Connect_and_send successful, exit code 0.")
			if message == "":													#if email file was sent, clear it.
				debug("Clearing email file.")
				open(Config.EMAIL_FILE_PATH, 'w').close()
		else:																	#if process did not exit successfully, alert to error
			debug("Exit code for connect_and_send: " + str(exitcode))
			error("Email sending timed out. Email not sent. " +
				"Probably no network connection.")
	except:
		error("Error in multiprocessing connect_and_send: " + 					#catch any unforeseen multiprocessing errors
			traceback.format_exc(Config.TRACEBACK_LIMIT))				




##INITIALIZE NOTIFICATION SYSTEMS======================================================================================
																				#this code is called when main.py imports errors.py, to set up logging and so on
																				#note that it will be called with every import (ie, 3 times), but the redundancy will not matter
log = logging.getLogger("log")													#initialize logger
log.setLevel(Config.LOG_LEVEL)													#tell logger what levels to pay attention to
handler = logging.handlers.RotatingFileHandler(									#enable log rotation
				Config.LOG_FILE_PATH, 											#see Config.py for logging config variables
				maxBytes=Config.LOG_SIZE, 
				backupCount=Config.LOG_COUNT)
log.addHandler(handler)
format = logging.Formatter(Config.LOG_FORMAT)									#format log (see Config.py to edit)
handler.setFormatter(format)

if __name__ == '__main__':								
	sendEmail(subject="TS-4200: Error Messages Unsent Before Crashing")			#send any left-over error messages.

open(Config.EMAIL_FILE_PATH, 'rw').close()										#clear pending email file

##TESTING==============================================================================================================
																				#this function tests the functionality of errors.py in such a way that the user will receive 
																				#confirmation that all features are working..
																				#see documentation for further instructions.
def test():
	print "preparing test..."
	queueEmail("Confirm: timestamp to the left is the time at which you ran errors.py.")
	sendEmail(subject="Testing notification systems (1/2)", message="""
		First usage case of sendEmail() functional; expect to receive one more email.\
		This message should contain ONLY these two sentences.
		""")
	error("Confirm that you have the following message severity labels enabled in Config.py:")
	error("messages of level ERROR")
	info("messages of level INFO")
	debug("messages of level DEBUG (note: not recommended for normal operation!)")
	queueEmail("Check in log file to confirm messages logged match up with levels enabled in Config.py.")
	queueEmail("If you receive this line, both queueEmail() and the second usage case of sendEmail() are functional.")
	queueEmail("If possible, remove internet now from TS-4200 and restore in 2 minutes.")
	sendEmail(subject="Testing notification systems (2/2)")
	sendEmail(subject="ERROR WITH SENDEMAIL(): should not send email file when it is empty.")
	queueEmail("Internet restored.")
	time.sleep(30)
	for i in range(8):
		sendEmail()
		time.sleep(20)
	print "testing complete"

if __name__ == '__main__':
	test()


