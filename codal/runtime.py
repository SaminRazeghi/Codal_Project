# %%
import sys
import json
import requests
from base import *
import datetime
import time
import concurrent.futures
import re
from bs4 import BeautifulSoup
import jdatetime
from persiantools.jdatetime import JalaliDateTime, JalaliDate
from persiantools import characters, digits

import pandas as pd
import requests
import subprocess
# sys.path.append(r'/home/mahdi/Desktop/codal_reader')
# %%


def vlidation_report(report: dict):
    title = ommiting_half_space(report['Title'])
    str1 = ommiting_half_space('اطلاعات و صورت‌های مالی میاندوره‌ای')
    str2 = ommiting_half_space('صورت‌های مالی سال مالی منتهی')
    str3 = ommiting_half_space('صورت‌های مالی تلفیقی سال مالی')
    str4 = ommiting_half_space('گزارش فعالیت ماهانه')
    str5 = ommiting_half_space('صورت وضعیت پورتفوی دوره')
    str6 = ommiting_half_space('شرکت')
    if (str1 in title) or (str2 in title) or (str3 in title) or (str4 in title) or (str5 in title):
        return True
    return False


def find_new_reports(last_date: str, last_time: str):
    page_num = 0
    reports_list = []
    while True:
        page_num += 1
        print(page_num)
        # preiodic
        url = f'https://search.codal.ir/api/search/v2/q?&Audited=true&AuditorRef=-1&Category=1&Childs=true&CompanyState=-1&CompanyType=-1&Consolidatable=true&IsNotAudited=false&Length=-1&LetterType=6&Mains=true&NotAudited=true&NotConsolidatable=true&PageNumber={page_num}&Publisher=false&TracingNo=-1&search=true'

        # monthly
        # url = f'https://search.codal.ir/api/search/v2/q?=&Audited=true&AuditorRef=-1&Category=-1&Childs=false&CompanyState=0&CompanyType=1&Consolidatable=true&IsNotAudited=false&Isic=571919&Length=-1&LetterType=58&Mains=true&NotAudited=true&NotConsolidatable=true&PageNumber={page_num}&Publisher=false&Symbol=%D9%88%D8%AA%D8%AC%D8%A7%D8%B1%D8%AA&TracingNo=-1&search=true'

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0) Gecko/20100101 Firefox/97.0'}
        for i in range(10):
            try:
                response_reports = requests.get(
                    url, headers=headers, timeout=10)

                if response_reports.status_code == 200:
                    break
            except Exception as e:
                if i == 9:
                    time.sleep(0.3*i)
                    print(e)
                    raise Exception('cant get any information from codal')

        decoded_response_reports = response_reports.content.decode("utf")
        json_reports = json.loads(decoded_response_reports)
        reports = json_reports['Letters']

        last_publish_date_ls = list(
            map(lambda x: int(convert_fa_numbers(x)), last_date.split('/')))
        last_publish_time_ls = list(
            map(lambda x: int(convert_fa_numbers(x)), last_time.split(':')))
        last_publish_datetime = jdatetime.datetime(last_publish_date_ls[0], last_publish_date_ls[1], last_publish_date_ls[2],
                                                   last_publish_time_ls[0], last_publish_time_ls[1], last_publish_time_ls[2]).togregorian()
        last_publish_timestamp = int(
            time.mktime(last_publish_datetime.timetuple()))

        for report in reports:
            current_publish_datetime_ls = report['PublishDateTime'].split(' ')
            current_publish_date_ls = list(map(lambda x: int(
                convert_fa_numbers(x)), current_publish_datetime_ls[0].split('/')))
            current_publish_time_ls = list(map(lambda x: int(
                convert_fa_numbers(x)), current_publish_datetime_ls[1].split(':')))
            current_publish_datetime = jdatetime.datetime(current_publish_date_ls[0], current_publish_date_ls[1], current_publish_date_ls[2],
                                                          current_publish_time_ls[0], current_publish_time_ls[1], current_publish_time_ls[2]).togregorian()
            current_publish_timestamp = int(
                time.mktime(current_publish_datetime.timetuple()))
            if vlidation_report(report) and 'Attachment' not in report['Url']:
                if current_publish_timestamp == last_publish_timestamp and len(reports_list) > 0:
                    last_date_report, last_time_report = reports_list[0]['publish_datetime'].split(
                    )
                    return (reports_list, last_date_report, last_time_report)
                elif current_publish_timestamp == last_publish_timestamp and len(reports_list) == 0:
                    return (reports_list, last_date, last_time)

                else:
                    reports_list.append({'symbol': convert_str_to_correct_format(report['Symbol']), 'main_company_name': convert_str_to_correct_format(report['CompanyName']),
                                        'title': report['Title'], 'publish_datetime': report['PublishDateTime'],
                                         'publish_timestamp': current_publish_timestamp, 'base_url': 'https://www.codal.ir'+report['Url']})
        time.sleep(2)


def report_completer(report, index):
    print(f'start {index}')
    try:
        ommited_title = ommiting_half_space(report['title'])
        report['is_correction'] = 1 if ommiting_half_space(
            'اصلاحیه') in ommited_title else 0
        report['is_combined'] = 1 if ommiting_half_space(
            'تلفیقی') in ommited_title else 0
        report['is_audited'] = 1 if ommiting_half_space(
            'حسابرسی شده') in ommited_title else 0
        report['is_fiscal_year'] = 1 if ommiting_half_space(
            'سال مالی') in ommited_title else 0
        report['report_type'] = 'monthly' if (ommiting_half_space('گزارش فعالیت ماهانه') in ommited_title or
                                              ommiting_half_space('وضعیت پورتفوی') in ommited_title) else 'periodic'
        report['is_sub_company'] = 1 if ommiting_half_space(
            'شرکت') in ommited_title else 0
        extract_information_from_response(report)

        try:
            report['current_fiscal_year_standard'] = report['current_fiscal_year_jalali'].to_gregorian()
            report['current_fiscal_year_jalali'] = str(
                report['current_fiscal_year_jalali'])
        except:
            report['current_fiscal_year_standard'] = None

        try:
            report['end_to_jalali'] = JalaliDate(
                *map(int, report['end_to_jalali'].split('/')))
        except ValueError:
            ls_end_to_jalali = report['end_to_jalali'].split('/')
            report['end_to_jalali'] = JalaliDate(int(ls_end_to_jalali[0]),
                                                 int(ls_end_to_jalali[1]),
                                                 int(ls_end_to_jalali[2])-1)
        report['end_to_standard'] = report['end_to_jalali'].to_gregorian()

        report['end_to_jalali'] = str(report['end_to_jalali'])
        print(f'done {index}')

        return (False, index)
    except Exception as e:
        print(e)
        if 'freq_of_errors' in list(report.keys()):
            df = pd.DataFrame({'symbol': report['symbol'], 'main_company_name': report['main_company_name'],
                               'title': report['title'], 'publish_datetime': report['publish_datetime'],
                               'publish_timestamp': report['publish_timestamp'], 'base_url': report['base_url'], 'freq_of_errors': report['freq_of_errors']+1}, index=[0])
        else:
            df = pd.DataFrame({'symbol': report['symbol'], 'main_company_name': report['main_company_name'],
                               'title': report['title'], 'publish_datetime': report['publish_datetime'],
                               'publish_timestamp': report['publish_timestamp'], 'base_url': report['base_url'], 'freq_of_errors': 1}, index=[0])
        return (True, index)


def extract_information_from_response(report):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0) Gecko/20100101 Firefox/97.0'}
    for i in range(10):
        try:
            response = requests.get(
                report['base_url'], headers=headers, timeout=10)
            if response.status_code == 200:
                break
        except Exception as e:
            if i == 9:
                time.sleep(0.3*i)
                print(e)
                raise Exception('cant get any information from codal')
    content = response.content.decode('utf-8')

    if len(extract_exist_sheet_ids(content)) != 0:
        report['sheet_ids_dic'] = extract_exist_sheet_ids(content)
    else:
        raise Exception('sheet ids dic is emty')

    if report['is_fiscal_year']:
        report['period'] = 12
    else:
        period_item = ommiting_half_space(report['title']).split(
            ommiting_half_space('دوره'))[-1].strip()
        period = ''
        for j in period_item:
            if j.isdigit():
                period += j
            else:
                break
        report['period'] = int(digits.fa_to_en(period))
    report['end_to_jalali'] = extract_end_to_date_jalali(content)
    report['current_fiscal_year_jalali'] = extract_current_fiscal_year_jalali(
        content)
    if report['is_sub_company']:
        report['sub_company_name'] = convert_str_to_correct_format(
            extract_sub_company_name(content))
    else:
        report['sub_company_name'] = 'main_company'


def prepare_reports(reports: list):
    ignore_indices = []
    print('num of new reports', len(reports))
    i = 0

    error_index = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executer:
        results = [executer.submit(report_completer, report, index)
                   for index, report in enumerate(reports)]
        for r in concurrent.futures.as_completed(results):
            print('---- result ----', r.result())
            if r.result()[0] == True:
                error_index.append(r.result()[1])
    reports = [report for report in reports if reports.index(
        report) not in error_index]
    if len(reports) > 0:
        df = pd.DataFrame(reports)
        df['sheet_ids_dic'] = df['sheet_ids_dic'].map(
            lambda x: convert_sheet_ids_dic_to_str(x))

        for report in reports:
            del report['title']
    return reports


def extract_exist_sheet_ids(response):
    soup = BeautifulSoup(response, 'html.parser')
    dic = {}
    for element in soup.find('select', {'name': 'ctl00$ddlTable'}).findAll('option'):
        dic[element['value']] = convert_str_to_correct_format(
            element.text.split('\n')[0])
    return dic


def extract_current_fiscal_year_jalali(response):
    soup = BeautifulSoup(response, 'html.parser')
    current_fiscal_year_jalali = soup.find(
        'span', {'id': 'ctl00_lblYearEndToDate'}).text
    if len(current_fiscal_year_jalali) != 0:
        try:
            current_fiscal_year_jalali = JalaliDate(
                *map(int, current_fiscal_year_jalali.split('/')))
        except ValueError:
            ls_end_to_jalali = current_fiscal_year_jalali.split('/')
            current_fiscal_year_jalali = JalaliDate(int(ls_end_to_jalali[0]),
                                                    int(ls_end_to_jalali[1]),
                                                    int(ls_end_to_jalali[2])-1)
    else:
        current_fiscal_year_jalali = None
    return current_fiscal_year_jalali


def extract_sub_company_name(response):
    soup = BeautifulSoup(response, 'html.parser')
    return soup.find('span', {'id': 'ctl00_txbCompanyName'}).text


def extract_end_to_date_jalali(response):
    '''

    '''
    soup = BeautifulSoup(response, 'html.parser')
    return soup.find('span', {'id': 'ctl00_lblPeriodEndToDate'}).text


def prepare_sheet_ids_dic(reports):
    for report in reports:
        mapper_sheet_ids(report)
        report['sheet_ids_dic'] = {
            key: value for key, value in report['sheet_ids_dic'].items() if isEnglish(value)}

# Calls spider in terminal


def run_spider(spider_path, base_urls):
    spider_name = 'Ctable'
    modified_urls = gen_url(base_urls)
    url_arguments = ' '.join(modified_urls)
    # Construct the full command

    command = f'cd "{spider_path}" && scrapy crawl {spider_name} -a url_list="{url_arguments}"'
    # Execute the command using subprocess
    subprocess.call(command, shell=True)

# adds "&sheetId=1" to the end of URLs


def gen_url(base_urls):
    modified_urls = []
    for url in base_urls:
        modified_url = url + "&sheetId=1"
        modified_urls.append(modified_url)
    print(modified_urls)
    return modified_urls
