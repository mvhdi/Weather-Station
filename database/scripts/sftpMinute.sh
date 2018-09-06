
# original author: CEN 8/15/01
# updated: Mahdi Mohamed 6/23/18
# this script 
# 1-maintains an ftp connection with a ftp host
# 2-downloads weather data every five minutes
# 3-inserts it into the weather database
# 4-downloads the monthly file at 12:01 am
# 5-makes a toggle to be read by midnight.pl after the monthly file download.


source sftpInclude.sh

gotmonth=0

echo "Starting up\n\n"

#loop forever
while [ 1==1 ]
do

	for i in 1 2 3 4 5
	do
		#open an sftp connection to the collection system
		#get oneline and 5MinuteToUnix
		echo "connecting...\n"
		sftp $sftpuser@$sftphost <<LimitString 
			! echo "sftp connection open"
			get $fiveminute $filedest
			get $shortfile $onelinedest
			put $localtoggle $remotetoggle
			exit
LimitString

		echo $?
		if [ $? -ne 0 ]
		then
			echo "File transfers failed. Trying again in 5 minutes\n"
		else
			echo "DB connecting\n"
			$mysqlpath --user=$dbuser --password=$dbpass $db <<LimitString
			load data local infile '$filedest' into table $table
LimitString
	
		fi
	
		sleep 60
	end
		
	hour=`date "+%k"`
	minute=`date "+%M"`
	
	echo "current time is $hour:$minute\n"
	
	#reset gotmonth around 12:12
	if [ $hour -ge 0 ] && [ $minute -ge 12 ]
	then
		gotmonth=0
	fi
	
	#do midnight update starting at 12:01
	
	let unixtime=`date "+%s"`-22*60*60
	year=`date -r $unixtime "+%Y"`
	month=`date -r $unixtime "+%m"`
	monthfile="$monthpath$month-$year"
	
	
	if [ $hour -eq 0 ] && [ $minute -ge 1 ] && [ $minute -lt 12 ] && [ $gotmonth -eq 0 ]
	then
		echo "midnight update in progress...\n"
	
		sftp $sftpuser@$sftphost <<LimitString
			! echo "getting monthfile\n"
			get $monthfile month
			! gotmonth=1
			exit
LimitString
	
		if [ $? -eq 0 ]
			then
				$mysqlpath --user=$dbuser --password=$dbpass $db <<LimitString
					load data infile '$monthfile' into table $table
LimitString
		fi
	fi
	ls > $togdest
done