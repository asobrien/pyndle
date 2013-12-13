#!/bin/bash

# A shell script to control FCGI processes required for web.py usage
# Modified from From: http://ole.im/blog/2011/oct/03/webpy-nginx

# NOTE: ALL PROJECTS MAIN FILE MUST BE NAMED "main.py" FOR THIS TO WORK WITHOUT MOD.

# FIXME: Restart command may not work, but reload does.

projects=(
# /path/to/site                          fcgi_port (different for each site)
  /home/pyndle/ebook_server/src   9009   # pyndle.bearonis.com
)

# Start the services
start(){

  for (( i=0; i<${#projects[@]}; i++ ))
  do
    spawn-fcgi -d ${projects[$i]} -f ${projects[$i]}/main.py -a 127.0.0.1 -p ${projects[$i+1]}
    i=$i+1
  done
}

# Stop the services
stop(){
  for (( i=0; i<${#projects[@]}; i++ ))
  do
    CPID=$(pgrep -f "python ${projects[$i]}/main.py") # current process id
    if [ "$CPID" != "" ]
      then
      kill $CPID
    fi
    i=$i+1
  done
}

# Main program
case "$1" in
  start)
    start
    echo "Started services"
    ;;
  stop)
    stop
    echo "Stopped services"
    ;;
  restart|reload)
    stop
    start
    echo "Restarted services"
    ;;
  *)
    echo "Usage: $0 {start|stop|restart|reload}"
    exit 1
esac
exit 0