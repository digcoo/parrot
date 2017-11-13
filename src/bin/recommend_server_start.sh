#!/bin/sh

project_dir=/home/ubuntu/git_project/parrot

cd $project_dir/src/

nohup python RecommendWebServer.py & >> reg.log

exit 0
