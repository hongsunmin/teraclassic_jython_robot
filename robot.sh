#!/bin/bash

#https://gist.github.com/tinogomes/447191/f751239eb48e3341b18a79b11995cee7978ee77b

PID=./robot.pid
LOG=./robot_process.log

ANDROID_HOME="$HOME/Library/Android/sdk"
ADB=$ANDROID_HOME/platform-tools/adb
CMD=$ANDROID_HOME/tools/bin/monkeyrunner

status() {
	echo
	echo "=============== Status ============="

	if [ -f $PID ]
	then
		echo
		echo "Pid file: $( cat $PID ) [$PID]"
		echo
		ps -ef | grep -v grep | grep $( cat $PID )
	else
		echo
		echo "No Pid file"
	fi
}

start() {
	if [ -f $PID ]
	then
		echo
		echo "Already started. PID: [$( cat $PID )]"
	else
		echo "=============== Start =============="

		export JAVA_HOME=`/usr/libexec/java_home -v 1.8`
		if nohup $CMD test.py >> $LOG 2>&1 &
		then
			echo $! > $PID
			echo "Done."
			echo "$(date '+%Y-%m-%d %X'): START" >>$LOG
		else
			echo "Error..."
			/bin/rm $PID
		fi
	fi
}

kill_cmd() {
	SIGNAL=""; MSG="Killing "
	while true
	do
		LIST=`ps -ef | grep -v grep | grep $CMD | awk '{print $2}'`
        if [ "$LIST" ]
        then
            echo; echo "$MSG $LIST" ; echo
            echo $LIST | xargs kill $SIGNAL
            sleep 2
            SIGNAL="-9" ; MSG="Killing $SIGNAL"
            if [ -f $PID ]
            then
                /bin/rm $PID
            fi
        else
           echo; echo "All killed..." ; echo
           break
        fi
    done
}

stop() {
	echo "=============== Stop ==============="

	if [ -f $PID ]
	then
		var=$($ADB shell ps | grep monkey | awk '{print $2}')
		if [ ! -z "$var" ]
		then
			echo $var
			$ADB shell kill -9 $var
		fi
		if kill $( cat $PID )
		then
			echo "Done."
			echo "$(date '+%Y-%m-%d %X'): STOP" >>$LOG
		fi
		/bin/rm $PID
		kill_cmd
	else
		echo "No pid file. Already stopped?"
	fi
}

case "$1" in
	'start')
		start
		;;
	'stop')
		stop
		;;
	'restart')
		stop ; echo "Sleeping..."; sleep 1 ;
		start
		;;
	'status')
		status
		;;
	*)
		echo
		echo "Usage: $0 { start | stop | restart | status }"
		echo
		exit 1
		;;
esac

exit 0

