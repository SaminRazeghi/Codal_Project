# %%
from base import *
from runtime import *
import pandas as pd
import requests
from configparser import ConfigParser
import subprocess
from scrapy import cmdline

last_date_report = "۱۴۰۲/۰۵/۰۷"
last_time_report = "۱۰:۲۴:۰۶"


error_sleep_time = 0
sleep_time = 0.25

while True:
    try:
        reports, last_date_report, last_time_report = find_new_reports(
            last_date_report, last_time_report)
        error_sleep_time = 0

    except Exception as e:
        print(e)
        error_sleep_time += 1
        time.sleep(error_sleep_time*sleep_time)
        continue

    if len(reports) > 0:
        reports = prepare_reports(reports)
        # print(reports[0])

        base_urls = []  # Empty list to store base_url values

        for item in reports:
            base_url = item['base_url']
            base_urls.append(base_url)  # Append base_url to base_urls list
            # Append main_company_name to company_names list
            print("base_url:", base_url)

    print(base_urls)
    break


spider_path = "/Users/saminrazeghi/Documents/Samin/Interview/Hermes_Capital/Project/codal/Scrappy/codaltable/codaltable"
run_spider(spider_path, base_urls)


# %%

# %%
