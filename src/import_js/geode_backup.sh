#!/bin/sh

#初始化指令
curday='date +%Y%m%d'

#进入本地geode后端系统
gfsh
#连接本地数据库
connect

export_stocks='export data --region=stock --file=/home/ubuntu/geode-backup-store/stock_'$curday'.gfd --member=server-stock'


$export_stocks
