#!/bin/sh
# /etc/init.d/WeatherStation.sh

### BEGIN INIT INFO
# Provides:          WeatherStation.sh
# Required-Start:    $remote_fs $syslog
# Required-Stop:     $remote_fs $syslog
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Example initscript
# Description:       This file should be used to construct scripts to be
#                    placed in /etc/init.d.  This example start a
#                    single forking daemon capable of writing a pid
#                    file.  To get other behavoirs, implemend
#                    do_start(), do_stop() or other functions to
#                    override the defaults in /lib/init/init-d-script.
### END INIT INFO

sudo mount /dev/sda1	#ensure flash drive is mounted
sudo /usr/local/sbin/ts4200ctl --getrtc	#sync system time to hardware time
echo -n "Initializing Weather Station..."
cd /home/wx17/Weather 


sudo python main.py > /dev/null  & 
sleep 1
echo "done"
exit 0
