#!/bin/bash

BASE=`pwd`
LOG="$BASE/robot_monitor.log"
SLEEP_TIME=60

echo "=======================================" >> $LOG
echo "robot monitor start" >> $LOG
echo "=======================================" >> $LOG

while [ 1 ]
do
	check=`ps -ef | grep -v grep | grep monkeyrunner | wc -l`
	date=$(date "+%Y-%m-%d %H:%M:%S")
	if [ $check == 0 ]; then
	        "$BASE/robot.sh" restart

	        check=`ps -ef | grep -v grep | grep monkeyrunner | wc -l`
	        if [ $check == 0 ]; then
	                echo "$date process restart failed!" >> $LOG
	        else
	                echo "$date process restart success!" >> $LOG
	        fi
	else
	        echo "$date process alive" >> $LOG
	fi

	sleep $SLEEP_TIME
done

