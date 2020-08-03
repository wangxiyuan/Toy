#!/usr/bin/python

import csv
from datetime import datetime
import os
import requests
import subprocess
import time


LOG_FILE = "./logserver-web_access.log.1"
OUTPUT_FILE = "./result.csv"


def monitorLog(logFile):
    print("monitor logFile: %s" % LOG_FILE)
    popen = subprocess.Popen(["cat", LOG_FILE], stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
    while True:
        line = popen.stdout.readline().strip()
        if line:
            if '.whl' in line:
                analysisLine(line)


def analysisLine(line):
    request_ip, request_time, file_name,  = getInfo(line)
    location = getLocation(request_ip)
    writeToFile(request_ip, request_time, location, file_name)


def getInfo(line):
    # 208.91.105.88 - - [02/Aug/2020:16:18:20 +0000] "GET /favicon.ico HTTP/1.1" 404 560 "https://logs.openlabtesting.org/logs/periodic-0/github.com/pytorch/pytorch/master/pytorch-arm64-build-daily-master-py36/4e83d26/test_results/torch-1.7.0a0+c5b4f60-cp36-cp36m-linux_aarch64.whl" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36"
    IP, res = line.split(' - - [')
    request_time, res = res.split('] ')
    file_name = res.split("\" ")[1].split('/')[-1]

    return IP, request_time, file_name


def getLocation(request_ip):
    request_url = 'http://ip-api.com/json/%s' % request_ip
    location_response = requests.get(request_url)
    location = json.loads(location_response.text)
    return location['country'] + '/' + location['city']


def writeToFile(request_ip, request_time, location, file_name):
    headers = ['IP', 'Time', 'Location', 'File']
    row = [request_ip, request_time, location, file_name]

    if not os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, 'x')as f:
            f_csv = csv.writer(f)
            f_csv.writerow(headers)

    with open(OUTPUT_FILE, 'a')as f:
        f_csv = csv.writer(f)
        f_csv.writerow(row)


if __name__ == '__main__':
    monitorLog(logFile)
