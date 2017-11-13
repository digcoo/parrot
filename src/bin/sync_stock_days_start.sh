#!/bin/sh

project_dir=/home/ubuntu/git_project/parrot

cd $project_dir/src/

nohup python SyncStockDaySchedule.py & >> sync.log

exit 0
