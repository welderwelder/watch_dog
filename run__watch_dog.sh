#!/bin/bash

chk_run=`ps x | grep 'python -B watch_dog.py' | grep -v "grep"`	
                                                        
if test -z "$chk_run";then
  cd ~/Documents/watch_dog
  #dt=$(date +%y-%m-%d_%H:%M:%S) 		
  #cp log/mbot_ign_run.log log/run__watch_dog_$dt.log
  #echo 'empty, mbot is NOT running'
  python -B watch_dog.py >> log/run__watch_dog.log 2>&1   
			# "-B" avoids creating "pyc"(import side effect)
#else
#  echo $chk_run
fi

