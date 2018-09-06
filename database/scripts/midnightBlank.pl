#!/usr/bin/perl


# A script to run at midnight that:
# 1 - calculates daily information for yesterday
# 2 - writes yesterday's daily data to yesterdata
# 3 - writes yesterday last year's daily data to lastyeardata
# 4 - writes yesterday 100 years ago data to 75data
# if it detects that an error occurs, the script will wait 5 minutes, then
# try to do each of these things again. It will try a total of 3 times 
# (including the first time through) before it stops trying.
# A log is kept for each year.
# Before running the updates, the script checks for the toggle sent from ftp.pl
# If it can't find it, this script doesn't run.
# If it can, then it deletes the toggle.

# There is quite a bit of error checking involved. All of the major functions are 
# in unless statements, with a printout to let the user know that there was an
# error, along with setting the toggle to TRUE (1).
# The toggle ($t) is a way of keeping track of the errors.
# Nominally, it should be set to FALSE (0), indicating that no error has occured.
# There is one exception to this: when the program starts. 
# Conceptually, this happens because there IS an error when the program first runs:
# the daily data has not been calculated yet. 
# Technically, it just lets the while loop run through at least once.

# 1 - The daily update section calculates daily information.
# it starts with the most recent date in the daily database, and calculates
# daily information for each day up to and including yesterday.
# it will output the date of each day it tries to calculate.
# if there is no raw data for that day, it will not make a daily file for it,
# and print to the terminal that it will not be doing so.
# If this method is used, there should theoretically be no gaps in daily data,
# but this does not fill in any gaps if there are any (gaps are days with no
# information and with days with information on either side of them).

# To find yesterday's date, I needed to subract 22*60*60 seconds from the current
# unix time, in order to take into account days per month, and all that other
# time funkiness. Notice that it's 22 hours, not 24. Since there is a day once
#  a year that has only 23 hours, it would get two days ago if that day was
# yesterday. With 22, there are no problems, as long as this script runs before
#  22 hours after midnight (I'm giving myself an hour to spare, to be on the safe
#  side).
# The program will not run after 9 PM (2100 hours), because it might get the wrong 
# daily information if it does so at that time.

# 2 - Yesterday's file writes the daily information for yesterday into a file
# called yesterdata (a bit of word play there, I'm afraid. Sorry).
# If finds the most recent day in the database and writes that information to
# the file. Ideally, the most recent day in the database will be yesterday, but
# it might not be. Then it works out how much rainfall there has been up until 
# day so far this year.
	# NOTE: if more data groups are added to the daily file, the while loop
	#		number will have to be increased. Can't do it based on daydata because some data
	#		might be 0 (Ex: daily rainfall), which would count as false.

	# Format of yesterdata


# 3 - Last year's file writes the same information as yesterday's file, but for 
#  a year ago yesterday (to compare with yesterday). It does the same trick of
# finding the most recent day in the database to eliminate the missing-day problem.
# That's the most recent day to yesterday a year ago, mind you.
# I did the same unix time trickiness as in 1 to find yesterday's date, but I
# just subtracted a year to get last year. The reason for this was leap year.
# Subtracting a year's worth of seconds from the unix time would not take that
# into account, and we want the same month and day last year as yesterday.
# The lastyeardata file has the same format as yesterdata, and the NOTEs are
# the same too.

# 4 - 75 year data works the same, but it searches a different table (historical).
	

# daily calculations writen from ftp2.pl by MRL 7/2000
# yesterday file writer writen from yesterdaydb.pl by CEN 7/2001
# yesterday last year file writer writen from lastyear.pl by CEN 7/2001, which
# in turn was writen from the yesterdaydb.pl file.
# 75 year file writer written 8/17/01 by CEN.
# norm file writer written 8/21/01 by CEN

# created by: CEN 7/10/01
# modified by: CEN 8/21/01
# modified by: Mahdi Mohamed 6/21/18
# modified 75-year section slightly as per Colin's instructions - 08Oct01 df

# Modified program setup section for more readability 
#  Added 100 seconds to < @yester_str= localtime(time - ((22*60*60)+100)); >
#  We are still having trouble with daily data not being generated on the 
#  nights after DST/CST change.  Hmmm... there is no 2:00 am..?
#  Running dayfiller10.pl populates the daily database with the missing data.  29Oct02 df






#-------------------------------program setup-------------------------------

system ("clear");
print "\nMidnight Update Program running...\n\n";

use POSIX qw(tzset);
$ENV{TZ} = 'CST+06';
tzset();


# time stuff

	@time_str = localtime(time);
	

	$minute = $time_str[1];
		if ( $minute < 10 ){ $minute = "0$minute" };
	$second = $time_str[0];
		if ( $second < 10 ){ $second = "0$second" };
	$hour = $time_str[2];
	$realyear = ( $time_str[5] + 1900 );
	$realmonth = ($time_str[4] +1);
	$realday = ($time_str[3]);
	if ( $realmonth < 10 ){ $mysqlrealmonth = "0$realmonth" }
		else{ $mysqlrealmonth = "$realmonth" };
	if ( $realday< 10 ){ $mysqlrealday = "0$realday" }
		else{ $mysqlrealday = "$realday" };
		
	@yester_str= localtime(time - ((22*60*60)+100));	
	$yesterday = $yester_str[3];
	$yestermonth = ($yester_str[4] +1);
	$yesteryear = ( $yester_str[5] + 1900 );	
	if ( $yesterday < 10 ){ $mysqlyesterday = "0$yesterday" }
		else{ $mysqlyesterday = "$yesterday" };
	if ( $yestermonth < 10 ){ $mysqlyestermonth = "0$yestermonth" }
		else{ $mysqlyestermonth = "$yestermonth" };
		

# check if the program is running before 21 hours after midnight.
	if ($hour >= 21 ){ die "Cannot run program now, it is too late in the day.\n"; }	
		



# load Database module
use DBI;


# database globals			
$db = "****";				
$dbuser = "****";						
$dbpass = "****";			
$table="****";
$dtable="****";
$htable="";
$ntable="";

# this is part of the directory setting thing. It will either be wx2 or weather
$where = "weather";


# destinations
$yesterdest = "****";		
$yeardest = "****";
$seventyfivedest = "****";
$normdest = "****";
$logdest = "****";	
$toggledest = "****";


# make an array that holds the names of all the categories in "****" data, for error output purposes:
@store = ( "Date", "high temperature", "low temperature", "average temperature for the day", 
	"high barometer", "low barometer", "peak wind gust", "daily rainfall (for the whole day)",
	"high humidity", "low humidity");
@hstore = ("Date","high temp","low temp","dry bulb","wet bulb","dewpoint","humidity",
	"dewpoint rec","humidity rec","barometer", "attached thermometer","correction tmep",
	"correction inst","correction elev","correct pressure","wind direction","wind speed",
	"peak gust direction","peak gust speed","wind movement 8 hours", "wind movement 24 hours",
	"anemometer","percipitation","snowfall","cloud upper","upper cloud direction",
	"cloud lower", "lower cloud direction","weather character","remarks","observer");
	


# set toggle to 1 (on) so that it runs through the loop the first time through
$t = 1;


# increment to zero
# the loop has run zero times so far.
$x=0;


# open log file
open(LOG, ">> $logdest" );

# note runtime in log
	print LOG "$mysqlrealmonth/$mysqlrealday $hour:$minute:$second\n";
	
	
# check if ftp.pl did the midnight update
# if not->quit.

	unless ( open (MIDNIGHTTOGGLE, "$toggledest") )
	{
		print LOG "\tDid not find ftp toggle. Program did not run.\n\n";
		die "Midnight toggle not found. \nsftp.sh is probably not working correctly. Midnight.pl will not run today.\n\n";
	}

	close (MIDNIGHTTOGGLE);
	
# delete the toggle
	system ( "rm $toggledest" );

# connect to the database
unless( $dbh = DBI->connect("DBI:mysql:database=$db;host=localhost","$dbuser",
		"$dbpass",{'RaiseError' => 1})){$rc = $dbh->disconnect; print "DB connection failed.\n"; print LOG "\tDB connection failed.\n"; $t =1;}
		
#---------------------------end of program setup----------------------------







#****************************---------------*******************************
#****************************|START OF LOOP|*******************************
#****************************---------------*******************************

# do if there is toggle and increment is less than 3.
while( $t eq 1 && $x < 3)
{


#-------------------------------loop maintenance-------------------------------


	# set toggle to zero 
	# no errors have occured this time through the loop yet.
	$t = 0;

#----------------------------end of loop maintenance---------------------------

	
	
	



#--------------------------Start of daily update section------------------------

		print "----------------------------\nupdating daily information\n";

        
        # find out the last day entered into the database
        # the day after this will be the start date
        # This lets us calculate daily info if we miss a day.
			unless(		$sth = $dbh->prepare("SELECT max(date) from $dtable")	)
				{print "can't find last day entered\n";print LOG "\tDaily Info: can't find last day entered\n"; $t=1;}
			$sth->execute();
			@day1=$sth->fetchrow_array();
			$sth->finish;
 
		# convert the start date to Unix_Timestamp
			unless(		$sth = $dbh->prepare("SELECT unix_timestamp('$day1[0] 00:00:00')")	)
				{print "can't make unix time stamp\n";print LOG "\tDaily Info: can't make unix time stamp\n"; $t =1;}
			$sth->execute();
			@sec1=$sth->fetchrow_array();
			$sth->finish;
		

		# convert the end date to the number of days since the year zero
		# (end date is yesterday)
			unless( 	 $sth = $dbh->prepare("SELECT unix_timestamp('$yesteryear-$mysqlyestermonth-$mysqlyesterday 00:00:00')")		)
				{print "can't make unix time stamp\n"; print LOG "\tDaily Info: can't make unix time stamp\n"; $t =1;}
			$sth->execute();
			@sec2=$sth->fetchrow_array();
			$sth->finish;

		print "updating daily info from @day1[0] to $yesteryear-$mysqlyestermonth-$mysqlyesterday\n";
		
		

			if (@day1[0] eq "$yesteryear-$mysqlyestermonth-$mysqlyesterday"){
				print "No daily data needs to be calculated\n";
				print LOG "\tNo daily data needs to be calculated\n";
			}else{
				print "Calculating Daily Data for:\n";
				print LOG "\tCalculating Daily Data for:\n";
				}
				

		# calculate the daily information for the specified days
		# if we missed a day yesterday, it will calculate that too.
		# this works recursively, so it will always bring daily up to date.
		# it won't fill in gaps in the daily data, but theoretically, gaps
		# should not be able to be made.
		

			for ($i=$sec1[0]+86400;$i<=$sec2[0];$i=$i+86400){
				$j=$i+86400;
		
		#find the max and min data for each day in the converted database
				unless(	$sth = $dbh->prepare("select max(\`15\`),min(\`15\`),avg(\`15\`) from $table where \`1\` >=$i and \`1\` < $j") 	)
					{print "can't get some daily data\n"; print LOG "\tcan't get some daily data\n"; $t=1;}
				$sth->execute();
				unless( 	@daily=$sth->fetchrow_array()    	)
					{print "can't get some daily data\n"; print LOG "\tcan't get some daily data\n"; $t=1;}
				$sth->finish;

				# calc what day we're currently looking at.
				$sth = $dbh->prepare("select from_unixtime($i,'%Y-%m-%d')");
				$sth->execute();
				@day=$sth->fetchrow_array();
				$sth->finish;
				

				print $day[0];
				print LOG "\t",$day[0];
				
				# check if daily information is all empty
				if (@daily[1] eq "" &&
					@daily[2] eq "" &&
					@daily[3] eq "" &&
					@daily[4] eq "" &&
					@daily[5] eq "" &&
					@daily[6] eq "" &&
					@daily[7] eq "" &&
					@daily[8] eq "" 
				){print "\tNo Raw Data! Daily data will not be made.\n"; print LOG"\tNo Raw Data! Daily data will not be made.\n";}
				else{print "\n";print LOG "\n";}
				
			
				# put daily data into daily database table
				if ($daily[0] || $daily[1]){	
					unless( $dbh->do("insert into daily values($daily[0],1,1,1,1,1,1,1,1,1)"))
                    {print "can't write in new daily data\n";print LOG "\tcan't write in new daily data\n"; $t =1;}
				}
			
		
			}# end of for loop

		print "daily information updated\n----------------------------\n";
		

	
#-------------------------end of daily update section---------------------------
	
	
	
	
	
	
	
	
	if($t == 0){print "No problems so far\n";}else{print "There was a problem\n\n"; print LOG "\tThere was a problem\n";}
	
	




	
	
#------------------------Start of yesterday's file section----------------------

		print "----------------------------\nWriting yesterdata file \n";


		# find newest date:
			unless(	$sth = $dbh->prepare("SELECT max(\`1\`) from $dtable")	)
				{print "can't calculate last date\n";print LOG "\tYesterdata: can't calculate last date\n";$t=1;}
			$sth->execute();
			
			
		# load newest date into array
			unless(	@day = $sth->fetchrow_array()	)
				{print "can't get last date\n";$t=1;}
			$sth->finish;
		# @day now is the date of the last daily table entry
			
			
		# get all the data using @day:
			unless(	$sth = $dbh->prepare("SELECT * from $dtable where \`1\` = \"@day\"")	)
				{print "can't calculate daydata\n"; print LOG "\tYesterdata: can't calculate daydata\n"; $t=1;}
			$sth->execute();
		# load newest date into array
			unless ( @daydata = $sth->fetchrow_array() )
				{print "couldn't get daydata\n";print LOG "\tYesterdata: couldn't get daydata\n"; $t =1;}
			$sth->finish;
			
			
			
			if($t == 1){print "couldn't access DB correctly\n";print LOG "\tYesterdata: couldn't access DB correctly\n";}
				else{print "Database accessed. \n";}
		
			print "creating new yesterdata file... \n";
		
		# open new file:
			unless( open(DAT, "> $yesterdest"))
				{ print "can't make yesterdata file\n";	print LOG "\tcan't make yesterdata file\n";}
		
		
			
		# translate date into better format
			$date = @daydata[0];	
			
			# get year
				$year = $date;
				$year =~ s/\W.*//; 			# remove month and day parts
		
			# get month
				$month = $date;
				$month =~ s/$year-//; 		# remove year part
				$month =~ s/\W.*//; 		# remove day part
		
			
			# get day
				$day = $date;
				$day =~ s/$year-$month-//; 	# remove year and month parts
		
			# add zero to month and day fields to make them numbers rather than strings.
				$month += 0;
				$day += 0;
				
				
		print "writing to yesterdata...\n";
			
		# write date into file
			unless( print DAT @daydata[0], "\t")
				{print "can't write date in yesterdata\n"; print LOG "\tcan't write date in yesterdata\n";$t = 1;}
			unless( print DAT $year,"\t")
				{print "can't write year in yesterdata\n";print LOG "\tcan't write year in yesterdata\n"; $t = 1;}
			unless( print DAT $month,"\t")	
				{print "can't write month in yesterdata\n";print LOG "\tcan't write month in yesterdata\n"; $t = 1;}
			unless( print DAT $day, "\t")	
				{print "can't write day in yesterdata\n";print LOG "\tcan't write day in yesterdata\n"; $t = 1;}
				

		
		# yearly rainfall calculations:
		
			unless($sth = $dbh->prepare("select sum(rain) from $dtable where \`1\` >=\"$year-01-01\""))
				{print "couldn't calculate yearly rain data\n";print LOG "\tcouldn't calculate yearly rain for yesterdata\n"; $t =1;}
			$sth->execute();
			
			unless($rainy = $sth->fetchrow_array())
				{print "couldn't get yearly rain data\n";print LOG "\tcouldn't get yearly rain for yesterdata\n"; $t =1;}
			$sth->finish;
		# $rainy is the total rainfall since the start of the year
		
		
		unless( print DAT $rainy)
			{print "can't write yearly rain to yesterdata\n";print LOG "\tcan't write yearly rain to yesterdata\n"; $t =1;}
			
			
			
		print DAT "\t";			#tab deliniated
			
			
		# monthly rainfall calculations:
		
			unless($sth = $dbh->prepare("select sum(rain) from $dtable where date>=\"$year-$month-01\""))
				{print "couldn't calculate monthly rain for yesterdata\n"; print LOG "\tcouldn't calculate monthly rain for yesterdata\n"; $t =1;}
			$sth->execute();
			
			unless($rainy = $sth->fetchrow_array())
				{print "couldn't get monthly rain for yesterdata\n";print LOG "\tcouldn't get monthly rain for yesterdata\n"; $t =1;}
			$sth->finish;
		# $rainy is the total rainfall since the start of the month
		
		
		unless( print DAT $rainy)
			{print "can't write monthly rain to yesterdata\n"; print LOG "\tcan't write monthly rain to yesterdata\n"; $t =1;}			

	# NOTE - The monthly rain seems a little low.		
	
		
			
		# write daydata into file:
			$i = 1;
			while ( $i < 10 ){
				# check for NULL
				if(@daydata[$i] eq ""){			# if the slot is null
					@daydata[$i] = 999999;			# then put 999999 in the slot
				}
				
				
				# puts daydata into file yesterdata, tab deliniated
				
				unless( print DAT "\t", @daydata[$i] )
					{print "can't write ",@store[$i]," in yesterdata\n";
					print LOG "\tcan't write ",@store[$i]," in yesterdata\n"; $t =1;}
			
				$i += 1;
			}
		
		

	
			

		
		
		# close file
			unless( close(DAT) )
				{print "can't close file\n this is Not Good\n";$t=1;}
			
			
		print "yesterdata written. \n----------------------------\n";
		
#------------------------End of yesterday's file section----------------------
			
			
			
			
			
			
			
	# check for problems		
	if($t == 0){print "No problems so far\n"; print LOG "\tYesterdata file made\n";}
	else{print "There was a problem\n\n";print LOG "\tThere was a problem\n";}
	
			
			
			
			
			
			
			
			
#-----------------------Start of last year's file section---------------------

print "----------------------------\nWriting lastyeardata \n";


	# calculate the date of yesterday (may not be the last thing entered into database)
	
	$lastyearyesterday = ( $yesteryear - 1 );
	
	# storethe date of yesterday last year(may not be the last thing entered into database) into $date in MySQL format
		$date = "$lastyearyesterday-$mysqlyestermonth-$mysqlyesterday";
		
	# get the date of the nearest day in the database to yesterday last year using $date:
		unless( $sth = $dbh->prepare("SELECT max(date) from $dtable where date <= \"$date\"") )
			{print "can't get date from database\n";print LOG "\tLast Year: can't get date from database\n";$t =1;}
		$sth->execute();
		unless( $date = $sth->fetchrow_array() )
			{print "can't get date from database\n"; print LOG "\tLast Year: can't get date from database\n"; $t =1;}
		$sth->finish;
		
	
	
	
	# pull out data from database, into array
		unless(	$sth = $dbh->prepare("SELECT * from $dtable where date = \"$date\""))
			{print "can't calculate data from DB\n";print LOG "\tLast Year: can't calculate data from DB\n"; $t =1;}
		$sth->execute();
	# load newest data into array
		unless(	@daydata = $sth->fetchrow_array())
			{print "can't get data from DB\n";print LOG "Last Year: can't get data from DB\n"; $t =1;}
		$sth->finish;
		unless ($t eq 1){print "database accessed. \n";}
	
	
	# at this point, we have info from a day. The day is (hopefully) yesterday last year.
	# if that day doesn't exist in the database, then the data was have is from the latest
	# day that exists in the database before yesterday last year.
	
	
	
	
	# translate date into better format (for the day we're using).
		$date = @daydata[0];	
		
		# get year
			$year = $date;
			$year =~ s/\W.*//; 			# remove month and day parts
	
		# get month
			$month = $date;
			$month =~ s/$year-//; 		# remove year part
			$month =~ s/\W.*//; 		# remove day part
		
		# get day
			$day = $date;
			$day =~ s/$year-$month-//; 	# remove year and month parts
			
			
	
	print "creating new lastyeardata file\n";
	
	
	# open new file:
		unless( open(DAT, "> $yeardest"))
			{ print "can't make new lastyeardata file\n";print LOG "\tcan't make new lastyeardata file\n";	$t =1;}
	
	
		# add zero to month and day fields to make them numbers rather than strings.
			$month += 0;
			$day += 0;
		
		
		print "writing to lastyear file... \n";
		
	# write date into file
		unless( print DAT $date, "\t")	
			{print "can't write date in lastyeardata\n"; print LOG "\tcan't write date in lastyeardata\n"; $t =1;}
		unless( print DAT $year, "\t")	
			{print "can't write year in lastyeardata\n"; print LOG "\tcan't write year in lastyeardata\n"; $t =1;}
		unless( print DAT $month, "\t")	
			{print "can't write month in lastyeardata\n"; print LOG "\tcan't write month in lastyeardata\n"; $t =1;}
		unless( print DAT $day, "\t")	
			{print "can't write to day in lastyeardata\n"; print LOG "\tcan't write to day in lastyeardata\n"; $t =1;}
		
	
	

	
	
	# yearly rainfall calculations:
	
		unless (	$sth = $dbh->prepare("select sum(rain) from $dtable where date>=\"$year-01-01\" and date<=\"$date\";")	)
			{print "can't caulculate yearly rain data\n";print LOG "\tcan't caulculate yearly rain lastyeardata\n"; $t =1;}
		$sth->execute();
		
		unless( $rainy = $sth->fetchrow_array())
			{print "can't get yearly rain data\n";print LOG "\tcan't get yearly rain lastyeardata\n"; $t= 1;}
		$sth->finish;
		
	# $rainy is the total rainfall since the start of the year
	

	# put $rainy into lastyeardata file
	unless( print DAT $rainy){print "can't write yearly rain to lastyeardata\n";
		print LOG "\tcan't write yearly rain to lastyeardata\n"; $t = 1;}
	
	
	
	
	print DAT "\t"; 		#tab delineated.
	
	
	# monthly rainfall calculations:
	
		unless (	$sth = $dbh->prepare("select sum(rain) from $dtable where date>=\"$year-$month-01\" and date<=\"$date\";")	)
			{print "can't caulculate monthly rain data\n"; print LOG "\t can't caulculate monthly rain data\n";$t =1;}
		$sth->execute();
		
		unless( $rainy = $sth->fetchrow_array())
			{print "can't get monthly rain data\n"; print LOG "\tcan't get monthly rain data\n"; $t= 1;}
		$sth->finish;
		
	# $rainy is the total rainfall since the start of the month
	

	# put $rainy into lastyeardata file
	unless( print DAT $rainy){print "can't write monthly rain to lastyeardata\n";
		print LOG "\tcan't write monthly rain to lastyeardata\n"; $t = 1;}	
	
		
	# write daydata into file:
		$i = 1;
		while ( $i < 10 ){
			# check for NULL
			if(@daydata[$i] eq ""){			# if the slot is null
				@daydata[$i] = 999999;			# then put 999999 in the slot
			}
			
			# make string numbers into actual numbers
			@daydata[$i] += 0;	
			
			# puts daydata into file lastyeardata, tab deliniated
			unless( print DAT "\t", @daydata[$i] )
				{print "can't write ",@store[$i]," to lastyeardata\n"; print LOG "\tcan't write ",@store[$i]," to lastyeardata\n"; $t =1;}
	
		
			$i += 1;		
		}
	
	
	
	
	
	
	
	
	
	# close file
		unless( close(DAT) ){print "can't close file\nthis is Not Good\n"; $t =1;}
	
	print "lastyeardata written. \n----------------------------\n";
	
	



#------------------------End of last year's file section----------------------








	# check for problems		
	if($t == 0){print "No problems so far\n";print LOG "\tLastyeardata file made\n";}
	else{print "There was a problem\n\n";print LOG "\tThere was a problem\n";}









#------------------------Start of 75 file section---------------------

#!/usr/bin/perl

	print "----------------------------\nWriting 75data file \n";

	$year = ( $realyear - 75 );
	$month = $realmonth;
	$day = ( $realday );


	# store date into $date in MySQL format
		$date = "$year-$month-$day";
		
	# get the date of the nearest day in the database to yesterday 75 years ago using $date:
		unless( $sth = $dbh->prepare("SELECT max(date) from $htable where date <= \"$date\"") )
			{print "can't get date from database\n";print LOG "\t75: can't get date from database\n";$t =1;}
		$sth->execute();
		unless( $date = $sth->fetchrow_array() )
			{print "can't get date from database\n"; print LOG "\t75: can't get date from database\n"; $t =1;}
		$sth->finish;
		
	
	
	
	# pull out data from database, into array
		unless(	$sth = $dbh->prepare("SELECT * from $htable where date = \"$date\""))
			{print "can't calculate data from DB\n";print LOG "\t75: can't calculate data from DB\n"; $t =1;}
		$sth->execute();
	# load newest data into array
		unless(	@daydata = $sth->fetchrow_array())
			{print "can't get data from DB\n";print LOG "75: can't get data from DB\n"; $t =1;}
		$sth->finish;
		unless ($t eq 1){print "database accessed. \n";}
	
	
	# at this point, we have info from a day. The day is (hopefully) 100 years ago yesterday .
	# if that day doesn't exist in the database, then the data was have is from the latest
	# day that exists in the database before yesterday last year.
	
	
	
	
	# translate date into better format (for the day we're using).
		$date = @daydata[0];	
		
		# get year
			$year = $date;
			$year =~ s/\W.*//; 			# remove month and day parts
	
		# get month
			$month = $date;
			$month =~ s/$year-//; 		# remove year part
			$month =~ s/\W.*//; 		# remove day part
		
		# get day
			$day = $date;
			$day =~ s/$year-$month-//; 	# remove year and month parts
			
			

			
	
	print "creating new 75data file\n";
	
	
	# open new file:
		unless( open(DAT, "> $seventyfivedest"))
			{ print "can't make new 75data file\n";print LOG "\tcan't make new 75data file\n";	$t =1;}
	
	
		# add zero to month and day fields to make them numbers rather than strings.
			$month += 0;
			$day += 0;
			
		$date1 = "$year-$month-$day";
		
		
		print "writing to 75 year file... \n";
		
	# write date into file
		unless( print DAT $date, "\t")	
			{print "can't write date in 75data\n"; print LOG "\tcan't write date in 75data\n"; $t =1;}
		unless( print DAT $year, "\t")	
			{print "can't write year in 75data\n"; print LOG "\tcan't write year in 75data\n"; $t =1;}
		unless( print DAT $month, "\t")	
			{print "can't write month in 75data\n"; print LOG "\tcan't write month in 75data\n"; $t =1;}
		unless( print DAT $day, "\t")	
			{print "can't write to day in 75data\n"; print LOG "\tcan't write to day in 75data\n"; $t =1;}


	
	
		
	# write daydata into file:
		$i = 1;
		while ( $i < 31 ){
			if ( ($i eq 5) || ($i eq 6) || ($i eq 14) || ($i eq 15) || ($i eq 26)  )
			{
				# check for NULL
				if(@daydata[$i] eq ""){			# if the slot is null
					@daydata[$i] = 999999;			# then put 999999 in the slot
				}
				
				# make string numbers into actual numbers, except wind direction
				unless ($i eq "15"){@daydata[$i] += 0;}
			
				# puts daydata into file 75data, tab deliniated
				unless( print DAT @daydata[$i], "\t")
					{print "can't write ",@store[$i]," to 75data\n"; print LOG "\tcan't write ",@hstore[$i]," to 75data\n"; $t =1;}
			}
			
			$i += 1;		
		}
		
		
		
	#need to go to the next day to get high/low temp and precipitation/snowfall.
	
	$year = ( $realyear - 75 );
	$month = $realmonth;
	$day = ( $realday);
	
	# store date into $date in MySQL format
		$date = "$year-$month-$day";
		
	# get the date of the nearest day in the database to today a 75 ago using $date:
		unless( $sth = $dbh->prepare("SELECT max(date) from $htable where date <= \"$date 23:59:59\"") )
			{print "can't get second date from database\n";print LOG "\t75: can't get second date from database\n";$t =1;}
		$sth->execute();
		unless( $date = $sth->fetchrow_array() )
			{print "can't get second date from database\n"; print LOG "\t75: can't get second date from database\n"; $t =1;}
		$sth->finish;
		
	
	
	
	# pull out data from database, into array
		unless(	$sth = $dbh->prepare("SELECT * from $htable where date = \"$date\""))
			{print "can't calculate second data from DB\n";print LOG "\t75: can't calculate second data from DB\n"; $t =1;}
		$sth->execute();
	# load newest data into array
		unless(	@daydata = $sth->fetchrow_array())
			{print "can't get second data from DB\n";print LOG "75: can't get second data from DB\n"; $t =1;}
		$sth->finish;
		unless ($t eq 1){print "database accessed. \n";}
		
	# translate date into better format (for the day we're using).
		$date = @daydata[0];	
		
		# get year
			$year = $date;
			$year =~ s/\W.*//; 			# remove month and day parts
	
		# get month
			$month = $date;
			$month =~ s/$year-//; 		# remove year part
			$month =~ s/\W.*//; 		# remove day part
		
		# get day
			$day = $date;
			$day =~ s/$year-$month-//; 	# remove year and month parts	

		# add zero to month and day fields to make them numbers rather than strings.
			$month += 0;
			$day += 0;
			
		$date = "$year-$month-$day";
		$date2 = $date;	

	# write date into file
		unless( print DAT $date, "\t")	
			{print "can't write date in 75data\n"; print LOG "\tcan't write date in 75data\n"; $t =1;}
			
	
	# yearly rainfall calculations:
	
		unless (	$sth = $dbh->prepare("select sum(precipitation) from $htable where date>=\"$year-01-01\" and date<=\"$date 23:59:59\";")	)
			{print "can't calculate yearly rain data\n";print LOG "\tcan't calculate yearly rain in 75data\n"; $t =1;}
		$sth->execute();
		
		unless( $rainy = $sth->fetchrow_array())
			{print "can't get yearly rain data\n";print LOG "\tcan't get yearly rain in 75data\n"; $t= 1;}
		$sth->finish;
		
	# $rainy is the total rainfall since the start of the year
	

	# put $rainy into 75data file
	unless( print DAT $rainy){print "can't write yearly rain to 75data\n";
		print LOG "\tcan't write yearly rain to 75data\n"; $t = 1;}
	
	
	print DAT "\t"; 		#tab delineated
	
	
	# monthly rainfall calculations:
	
		unless (	$sth = $dbh->prepare("select sum(precipitation) from $htable where date>=\"$year-$month-01\" and date<=\"$date 23:59:59\";")	)
			{print "can't calculate monthly rain data\n"; print LOG "\t can't calculate monthly rain in 75data\n";$t =1;}
		$sth->execute();
		
		unless( $rainy = $sth->fetchrow_array())
			{print "can't get monthly rain data\n"; print LOG "\tcan't get monthly rain in 75data\n"; $t= 1;}
		$sth->finish;
		
	# $rainy is the total rainfall since the start of the month

	# put $rainy into 75data file
	unless( print DAT $rainy){print "can't write monthly rain to 75data\n";
		print LOG "\tcan't write monthly rain to 75data\n"; $t = 1;}

	#date lineup calculations
		unless( $sth = $dbh->prepare("select to_days(\"$date1\"),to_days(\"$date2\")") )
			{print "can't get lineup from database\n";print LOG "\t75: can't get lineup from database\n";$t =1;}
		$sth->execute();
		unless( @lineup = $sth->fetchrow_array() )
			{print "can't get lineup from database\n"; print LOG "\t75: can't get lineup from database\n"; $t =1;}
		$sth->finish;

	print DAT "\t", ( @lineup[1]-@lineup[0] ), "\t";

	# write new daydata into file:
		$i = 1;
		while ( $i < 31 ){
			if ( ($i eq 1) || ($i eq 2) || ($i eq 22) || ($i eq 23)  )
			{
				# check for NULL
				if(@daydata[$i] eq ""){			# if the slot is null
					@daydata[$i] = 999999;			# then put 999999 in the slot
				}
				
				# make string numbers into actual numbers
				@daydata[$i] += 0;
			
				# puts daydata into file 75data, tab deliniated
				unless( print DAT @daydata[$i], "\t")
					{print "can't write ",@store[$i]," to 75data\n"; print LOG "\tcan't write ",@hstore[$i]," to 75data\n"; $t =1;}
			}
			
			$i += 1;		
		}		
		
	# close file
		unless( close(DAT) ){print "can't close file\nthis is Not Good\n"; $t =1;}
	
	print "75data written. \n----------------------------\n";
	
	



#---------------------------End of 75 file section--------------------------






	# check for problems		
	if($t == 0){print "No problems so far\n";print LOG "\t75data file made\n";}
	else{print "There was a problem\n\n";print LOG "\tThere was a problem\n";}




#--------------------------Start of norm file section-----------------------

	print "----------------------------\nWriting normdata file \n";
	
	
# records eventually will need to be changeable

	# get all the data using yesterday's date:
		unless(	$sth = $dbh->prepare("SELECT * from $ntable 
			where month(date) = $yestermonth and dayofmonth(date) = $yesterday")	)
			{print "can't calculate daydata\n"; print LOG "\tNorms: can't calculate daydata\n"; $t=1;}
		$sth->execute();
		
	# load newest date into array
		unless ( @daydata = $sth->fetchrow_array() )
			{print "couldn't get daydata\n";print LOG "\tNorms: couldn't get daydata\n"; $t =1;}
		$sth->finish;
		
		unless ($t eq 1){print "database accessed\n";}
		print "creating new normdata file\n";
		
	# open new file:
		unless( open(DAT, "> $normdest"))
			{ print "can't make normdata file\n";	print LOG "\tcan't make normdata file\n";}

		unless ($t eq 1){print "writing to file\n";}
	# translate date into better format (for the day we're using).
		$date = @daydata[0];	
		# get month
			$month = $date;
			$month =~ s/0000-//; 		# remove year part
			$month =~ s/\W.*//; 		# remove day part
		# get day
			$day = $date;
			$day =~ s/0000-$month-//; 	# remove year and month parts	
		# add zero to month and day fields to make them numbers rather than strings.
			$month += 0;
			$day += 0;	
				
	#write date to file
		print DAT $month,"\t",$day;
		
		# write daydata into file:
			$i = 1;
			while ( $i < 12 ){
				# check for NULL
				if((@daydata[$i] eq "") || (@daydata[$i] eq "8888")){	# if the slot is null
					@daydata[$i] = 999999;						# then put 999999 in the slot
				}
				
				
				# puts daydata into file yesterdata, tab deliniated
				
				# make string numbers into actual numbers
					unless (( $i eq 5) || ( $i eq 7) || ( $i eq 9) || ( $i eq 11) ){@daydata[$i] += 0;}
				
				unless( print DAT "\t", @daydata[$i] )
					{print "can't write ",@store[$i]," in normdata\n";
					print LOG "\tcan't write ",@store[$i]," in normdata\n"; $t =1;}
			
				$i += 1;
			}

	# close file
		unless( close(DAT) ){print "can't close file\nthis is Not Good\n"; $t =1;}	
	print "normdata written. \n----------------------------\n";

#--------------------------End of norm file section-------------------------





	# check for problems		
	if($t == 0){print "No problems so far\n";print LOG "\tnormdata file made\n";}
	else{print "There was a problem\n\n";print LOG "\tThere was a problem\n";}





#-------------------------------loop maintenance-------------------------------

	# increment counter
	$x += 1;
	
	# wait five minutes if there was an error

	if ($t == 1){	print "waiting five minutes to try again...\n"; select(undef, undef, undef,300 );}
	
	
#----------------------------end of loop maintenance---------------------------
	
	
	
	
	
	
	
	
}
#*****************************-------------*********************************
#*****************************|END OF LOOP|*********************************
#*****************************-------------*********************************


#--------------------------closing the program stuff---------------------------

# disconnect from database.
	unless (	$rc = $dbh->disconnect	){die "couldn't close database\n";}


print "----------------------------\n\n";


# final result
	if ($t == 1){
		print "\tALERT! ALERT! ALERT!\n
		AN ERROR OCCURED!!!\n
		This program was unable to calculate something. See above for error logs. \n";
		print LOG "\tALERT! ALERT! ALERT!\t
		AN ERROR OCCURED!!!\n
		\tThis program was unable to calculate something. See above for error logs. \n";
	}
	else{
		print "Midnight Update Successful\n\n";
		print LOG "\n";
	}
