# Import our libraries
import logging
import logging.handlers
import re
import subprocess
from influxdb import InfluxDBClient
import os
from os.path import join, dirname
from dotenv import load_dotenv

# Load our Env
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path, verbose=True)

# Setup our logging
logs = logging.getLogger('Speedtest')
logs.setLevel(logging.DEBUG)
handler = logging.handlers.SysLogHandler(address = '/dev/log')
logs.addHandler(handler)

# Start
logs.debug('[SPEEDTEST] START')
logs.debug('[SPEEDTEST] Running Speedtest')

# Run Speedtest
speedtest_command = '/usr/bin/speedtest --accept-license --accept-gdpr --server-id={}'.format(os.environ.get("SERVER_ID"))
response = subprocess.Popen(speedtest_command, shell=True, stdout=subprocess.PIPE).stdout.read().decode('utf-8')

logs.debug('[SPEEDTEST] Speedtest Finished')

# Extract Results
ping = re.search('Latency:\s+(.*?)\s', response, re.MULTILINE)
download = re.search('Download:\s+(.*?)\s', response, re.MULTILINE)
upload =  re.search('Upload:\s+(.*?)\s', response, re.MULTILINE)

ping = ping.group(1)
download = download.group(1)
upload = upload.group(1)

logs.debug('[SPEEDTEST] Ping %f', float(ping))
logs.debug('[SPEEDTEST] Download %f', float(download))
logs.debug('[SPEEDTEST] Upload %f', float(upload))


logs.debug('[SPEEDTEST] SAVING DATA')
speed_data = [
    {
        "measurement" : "internet_speed",
        "tags" : {
            "host": os.environ.get("HOST")
        },
        "fields" : {
            "download": float(download),
            "upload": float(upload),
            "ping": float(ping)
        }
    }
]
client = InfluxDBClient(os.environ.get("DB_URL"), os.environ.get("DB_PORT"), os.environ.get("DB_USERNAME"), os.environ.get("DB_PASSWORD"), os.environ.get("DB_COLLECTION"))

client.write_points(speed_data)
logs.debug('[SPEEDTEST] FINISHED')
