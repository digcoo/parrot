#!/bin/bash 

#初始化指令
#curday="`date +"%Y%m%d"`"
curday=$(date '+%Y%m%d')

export_stocks="export data --region=stock --file=/home/ubuntu/geode-backup-store/stock_${curday}.gfd --member=server-stock"
export_stocks_day_final="export data --region=stock-day-final --file=/home/ubuntu/geode-backup-store/stock_day_${curday}.gfd --member=server-stock"
export_stocks_week_final="export data --region=stock-week-final --file=/home/ubuntu/geode-backup-store/stock_week_${curday}.gfd --member=server-stock"
export_stocks_month_final="export data --region=stock-month-final --file=/home/ubuntu/geode-backup-store/stock_month_${curday}.gfd --member=server-stock"
export_stocks_time_final="export data --region=stock-time-final --file=/home/ubuntu/geode-backup-store/stock_time_${curday}.gfd --member=server-stock"
export_plate="export data --region=plate --file=/home/ubuntu/geode-backup-store/plate_${curday}.gfd --member=server-stock"
export_plates_day_final="export data --region=plate-day-final --file=/home/ubuntu/geode-backup-store/plate_day_${curday}.gfd --member=server-stock"
export_plates_week_final="export data --region=plate-week-final --file=/home/ubuntu/geode-backup-store/plate_week_${curday}.gfd --member=server-stock"
export_plates_month_final="export data --region=plate-month-final --file=/home/ubuntu/geode-backup-store/plate_month_${curday}.gfd --member=server-stock"


expect <<-export_stocks

#进入本地geode后端系统
spawn gfsh

expect "gfsh>"
    send "connect\r"
    expect "gfsh>"
        send "${export_stocks}\r"

    expect "gfsh>"
        send "${export_stocks_week_final}\r"

    expect "gfsh>"
        send "${export_stocks_month_final}\r"

    set timeout 120

    expect "gfsh>"
        send "${export_plate}\r"

    expect "gfsh>"
        send "${export_plates_day_final}\r"

    expect "gfsh>"
        send "${export_plates_week_final}\r"

    expect "gfsh>"
        send "${export_plates_month_final}\r"

    expect "gfsh>"
        send "${export_stocks_day_final}\r"

    expect "gfsh>"
        send "exit\r"

#    set timeout 300


#interact

expect eof

export_stocks


