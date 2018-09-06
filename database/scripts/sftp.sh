

# CEN 8/15/01   (Original author of script)
# updated: Mahdi Mohamed 6/25/18
# this script 
# 1-opens an sftp connection with 
# 2-downloads weather data every five minutes
# 3-inserts it into the weather database
# 4-downloads the monthly file at 12:01 am
# 5-makes a toggle to be read by midnight.pl after the monthly file download.

# This file was written from scratch by Steven Holley, Aug. 2010

# Variables (usernames, passwords, file locations, etc.) are declared in 'sftpInclude.sh' for easy manipulation
source ****

gotmonth=0

echo "Starting up\n\n"

#loop forever
while [ 1==1 ]
do
    #open an sftp connection to the collection system
    #get oneline and 5MinuteToUnix
    echo "connecting...\n"   
    sftp "${sftpuser}@${sftphost}" <<LimitString  #LimitString defines the beginning of a "here document" which contains commands to run in the sftp instance
        get ${rawDataRemote} ${rawDataDest}
		get ${rawArrayDataRemote} ${rawArrayDataDest}
		get ${convertedDataRemote} ${convertedDataDest} 
		get ${onelineDataRemote} ${onelineDataDest} 
		put ${toggle} ${remotetoggle} 
        exit
LimitString
	
	# $? contains the exit status of the last command, so this checks if the sftp connection was made successfully
    if [ $? -ne 0 ]
    then
        echo "File transfers failed. Trying again in 5 minutes\n"
    else
        echo "DB connecting\n"
       
        $mysqlpath --user=$dbuser --password=$dbpass $db<<LimitString
		LOAD DATA LOCAL INFILE '${rawDataLocal}' INTO TABLE ${rawDataTable};
		LOAD DATA LOCAL INFILE '${rawArrayDataLocal}' INTO TABLE ${rawArrayDataTable};
		LOAD DATA LOCAL INFILE '${convertedDataLocal}' INTO TABLE ${convertedDataTable};
		LOAD DATA LOCAL INFILE '${onelineDataLocal}' INTO TABLE ${onelineTable};
        
LimitString
	
	fi
		
	connected=0

	echo "waiting...\n\n"
	sleep 65
	
	hour=`date "+%k"`
	minute=`date "+%M"`
	
	echo "current time is $hour:$minute\n"
	
	#reset gotmonth around 12:12
	if [ $hour -ge 0 ] && [ $minute -ge 12 ]
	then
		gotmonth=0
	fi
	
	#do midnight update starting at 12:01
	
	# get a unix time from yesterday and get the name for yesterday's month file
	let unixtime=`date "+%s"`-22*60*60
	year=`date -r $unixtime "+%Y"`
	month=`date -r $unixtime "+%m"`
	monthfile="${monthpath}${month}-${year}"
	
	# 
	if [ $hour -eq 0 ] && [ $minute -ge 1 ] && [ $minute -lt 12 ] && [ $gotmonth -eq 0 ]
	then
		echo "midnight update in progress...\n"
	
		sftp "${sftpuser}@${sftphost}" <<LimitString 	#LimitString defines the beginning of a "here document" which contains commands to run in the sftp instance
			get ${monthfile} month
			exit
LimitString
	
		if [ $? -eq 0 ]
			then
				gotmonth=1
				$mysqlpath --user=$dbuser --password=$dbpass $db <<LimitString
					load data local infile ${month} into table ${monthTale}
LimitString
			echo 1 > $togdest/mignighttoggle.txt
			ls > $togdest
		fi
	fi
	
done