import pandas as pd
import requests
import time
from datetime import datetime
import os 

def get_total_power(page):

    start_tag = b"<td align=center>Current Power</td><td align=center>"
    end_tag = b"</td></tr></center><center><tr><td align=center>Generation Of Current Day</td>"

    start = page.find(start_tag) + len(start_tag)
    end = page.find(end_tag)

    return page[start:end]

def get_days_generation(page):

    start_tag = b"<td align=center>Generation Of Current Day</td><td align=center>"
    end_tag = b"</td></tr></center><center><tr><td align=center>Last connection to website</td>"

    start = page.find(start_tag) + len(start_tag)
    end = page.find(end_tag)

    return page[start:end]

def get_lifetime_generation(page):

    start_tag = b"</tr></center><center><tr><td align=center>Lifetime generation</td><td align=center>"
    end_tag = b"</td></tr></center><center><tr><td align=center>Current Power</td>"

    start = page.find(start_tag) + len(start_tag)
    end = page.find(end_tag)

    return page[start:end]

def get_current_time():
    now = datetime.now()
    return now.strftime("%d/%m/%Y %H:%M:%S")

def read_config(path="data-puller.conf"):
    conf = {}

    f = open("data-puller.conf", "r")

    for line in f:
        field,data = line.split("=")
        conf[field] = data.strip("\n")

    conf["data_types"] = conf["data_types"].split(",")

    return conf

def check_connection_up(hostname):
   
    while True:

        response = os.system("ping -c 1 " + hostname + "> /dev/null")

        if response == 0:
            print(f"{hostname} is up!")
            return 0
        else:
            print(f"{hostname} is down, waiting 5 minutes")
            time.sleep(300)


conf = read_config()

ip = conf["ip"]
homepageurl = "http://{}/cgi-bin/home".format(ip)
rtdpageurl = "http://{}/cgi-bin/parameters".format(ip)


print("waiting for connection")
check_connection_up(ip)
print("connected")

while True:

    try:
        page = requests.get(homepageurl).content
        data = []

        if "total_power" in conf["data_types"]:
            data.append(str(get_total_power(page)))
        if "days_generation" in conf["data_types"]:
            data.append(str(get_days_generation(page)))
        if "lifetime_generation" in conf["data_types"]:
            data.append(str(get_lifetime_generation(page)))
        if "date_time" in conf["data_types"]:
            data.append(str(get_current_time()))
        data.append(time.time())
    
        df = pd.DataFrame(columns=[conf["data_types"]])
        df.loc[0] = data
        df.to_csv(conf["csv_filename"],mode='a',header=False)
        print("wrote to csv at {}".format(get_current_time()))
        time.sleep(int(conf["write_every_sec"]))

    except KeyboardInterrupt:
        exit()
    except:
        print("error'ed out, host is probably down")
        check_connection_up(ip)

