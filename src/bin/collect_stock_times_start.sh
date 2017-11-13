#!/bin/sh

project_dir=/home/ubuntu/git_project/parrot

cd $project_dir/src/

nohup python CollectStockTimeSchedule.py & >> spider.log

exit 0
