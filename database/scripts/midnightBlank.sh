# Mahdi Mohamed 6/25/18

source ****

clear 
echo "\nMidnight Update Program running...\n\n";

# set time zone to CST+06 and print out the date
TZ='American/CST+06'
export TZ
date
# time stuff
year=`date +%Y`
month=`date +%m`
day=`date +%d`
hour=`date "+%k"`
minute=`date "+%M"`
	
echo "$year $month $day $hour $minute"
	
# get a unix time from yesterday and get the name for yesterday's month file
let unixtime=`date "+%s"`-22*60*60
yyear=`date -r $unixtime "+%Y"`
ymonth=`date -r $unixtime "+%m"`
	
#yday=`date -r $unixtime "+%d"` test if it is really yesterday
monthfile="${monthpath}${month}-${year}"
	
echo "$yyear $ymonth $yday"
	
#check hour, if it is after 21 pm, then print error message and exit
if [ $hour -ge 21 ]
then
	echo "Cannot run program now, it is too late in the day.\n"
	exit
fi
	
	
# set toggle to 1 (on) so that it runs through the loop the first time through
t=1;


# increment to zero
# the loop has run zero times so far.
x=0;

# open log file and append curernt time at the end of the file
logInformation=`date`

cat >> ${logdest} << EOF
  ${logInformation}
EOF

# check if sftp.sh did the midnight update
# if not->quit.
	
if [ -f ${toggledest} ] 
then
   echo "File $FILE exists."
else
   echo "File $FILE does not exist."
  
fi

# delete the toggle
#rm ${toggledest}


RESULT=`mysql -u$dbuser -p$dbpass -e "SHOW DATABASES" | grep -Fo $db`
if [ "$RESULT" == "${db}" ] 
then
    echo "Database exist"
else
    echo "Database does not exist"
	t=1
	logError='database connection failed'
	echo ${logError} >> ${logdest}
fi

#---------------------------end of program setup----------------------------







#****************************---------------*******************************
#****************************|START OF LOOP|*******************************
#****************************---------------*******************************

# do if there is toggle and increment is less than 3.
while [ "${t}" -eq 1 ] && [ "${x}" -lt 3 ];do
	
#-------------------------------loop maintenance-------------------------------t=0
	# set toggle to zero 
	# no errors have occured this time through the loop yet.
	
	echo "??"
	t=0
#----------------------------end of loop maintenance---------------------------

	
	
	



#--------------------------Start of daily update section------------------------
	echo "----------------------------\nupdating daily information\n";
	# find out the last day entered into the database
    # the day after this will be the start date
    # This lets us calculate daily info if we miss a day.
    
	#the script is straight forward
	response=$(echo "select isnull(\`1\`) from converteddata" | mysql -u $dbuser -p$dbpass $db)
	#check whether a response is received and do what you need, not 
	
	#loop through this for every line of values you have.



	echo ${response} 
	#check whether a response is received and do what you need, not 
	


done




		
		
	


	

	