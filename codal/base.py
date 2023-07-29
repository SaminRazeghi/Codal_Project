# %%
import requests
import re
import pandas as pd
import json
from persiantools.digits import fa_to_en
import sys
sys.path.append(r'/home/mahdi/Desktop/codal_reader')


def mapper_sheet_ids(report):
    if len(report['sheet_ids_dic']) == 1 and report['report_type'] == 'monthly':
        if (list(report['sheet_ids_dic'].keys()))[0] == '1000000':
            report['sheet_ids_dic']['1000000'] = 'production_sale'

        elif (list(report['sheet_ids_dic'].keys()))[0] == '1000008':
            report['sheet_ids_dic']['1000008'] = 'livestock_monthly'

        elif (list(report['sheet_ids_dic'].keys()))[0] == '1000001':
            report['sheet_ids_dic']['1000001'] = 'construction_monthly'

        elif (list(report['sheet_ids_dic'].keys()))[0] == '1000003':
            report['sheet_ids_dic']['1000003'] = 'bank_monthly'

        elif (list(report['sheet_ids_dic'].keys()))[0] == '1000004':
            report['sheet_ids_dic']['1000004'] = 'leasing_monthly'

        elif (list(report['sheet_ids_dic'].keys()))[0] == '1000005':
            report['sheet_ids_dic']['1000005'] = 'service_monthly'

        elif (list(report['sheet_ids_dic'].keys()))[0] == '1000006':
            report['sheet_ids_dic']['1000006'] = 'insurance_monthly'

        elif (list(report['sheet_ids_dic'].keys()))[0] == '1000009':
            report['sheet_ids_dic']['1000009'] = 'capital_supply_monthly'

    elif len(report['sheet_ids_dic']) > 1 and report['report_type'] == 'monthly':
        for key, value in report['sheet_ids_dic'].items():
            value = ommiting_half_space(value)
            if ommiting_half_space('خلاصه') in value and ommiting_half_space('صنعت') in value:
                report['sheet_ids_dic'][key] = 'tafkik_industry'

            elif ommiting_half_space('پورتفو') in value and ommiting_half_space('بورس') in value\
                    and ommiting_half_space('خارج') not in value:
                report['sheet_ids_dic'][key] = 'bors_portfo'

            elif ommiting_half_space('پورتفو') in value and ommiting_half_space('بورس') in value\
                    and ommiting_half_space('خارج') in value:
                report['sheet_ids_dic'][key] = 'kharej_bors_portfo'

            elif ommiting_half_space('ریز') in value and ommiting_half_space('تحصیل') in value:
                report['sheet_ids_dic'][key] = 'riz_moamelat_tahsil'

            elif ommiting_half_space('ریز') in value and ommiting_half_space('واگذار') in value:
                report['sheet_ids_dic'][key] = 'riz_moamelat_vagozari'

            elif ommiting_half_space('درآمد') in value and ommiting_half_space('سهام') in value:
                report['sheet_ids_dic'][key] = 'share_income'

    elif report['report_type'] == 'periodic':
        for key, value in report['sheet_ids_dic'].items():
            value = ommiting_half_space(value)

            if ommiting_half_space('سود') in value and ommiting_half_space('زیان') in value\
                    and ommiting_half_space('تلفیقی') not in value and ommiting_half_space('جامع') not in value:
                report['sheet_ids_dic'][key] = 'profit_loss'

            elif ((ommiting_half_space('ترازنامه') in value) or
                  (ommiting_half_space('وضعیت') in value and ommiting_half_space('مالی') in value))\
                    and ommiting_half_space('تلفیقی') not in value:
                report['sheet_ids_dic'][key] = 'balance_sheet'

            elif ommiting_half_space('جریان') in value and ommiting_half_space('نقد') in value\
                    and ommiting_half_space('تلفیقی') not in value:
                report['sheet_ids_dic'][key] = 'cash_flow'

            elif ommiting_half_space('سود') in value and ommiting_half_space('زیان') in value\
                    and ommiting_half_space('تلفیقی') in value and ommiting_half_space('جامع') not in value:
                report['sheet_ids_dic'][key] = 'combined_profit_loss'

            elif ((ommiting_half_space('ترازنامه') in value) or
                  (ommiting_half_space('وضعیت') in value and ommiting_half_space('مالی') in value))\
                    and ommiting_half_space('تلفیقی') in value:
                report['sheet_ids_dic'][key] = 'combined_balance_sheet'

            elif ommiting_half_space('جریان') in value and ommiting_half_space('نقد') in value\
                    and ommiting_half_space('تلفیقی') in value:
                report['sheet_ids_dic'][key] = 'combined_cash_flow'

            elif ommiting_half_space('خالص') in value and ommiting_half_space('دارایی') in value\
                    and ommiting_half_space('گردش') not in value:
                report['sheet_ids_dic'][key] = 'net_asset'

            elif ommiting_half_space('گردش') in value and ommiting_half_space('دارایی') in value:
                report['sheet_ids_dic'][key] = 'net_asset_turnover'


def convert_str_to_correct_format(string):
    string = string.strip()
    string = re.sub(' +', ' ', string)
    string = convert_ar_characters(string)
    return string


def ommiting_half_space(string_):
    string_ = convert_ar_characters(string_)
    string_ = string_.replace("\u200c", "")
    string_ = string_.replace(' ', '')
    string_ = string_.replace('\xa0', '')
    return string_


def convert_ar_characters(input_str):
    """
    Converts Arabic chars to related Persian unicode char
    :param input_str: String contains Arabic chars
    :return: New str with converted arabic chars
    """
    mapping = {
        'ك': 'ک',
        'دِ': 'د',
        'بِ': 'ب',
        'زِ': 'ز',
        'ذِ': 'ذ',
        'شِ': 'ش',
        'سِ': 'س',
        'ى': 'ی',
        'ي': 'ی'
    }
    return _multiple_replace(mapping, input_str)


def convert_fa_numbers(input_str):
    """
    This function convert Persian numbers to English numbers.

    Keyword arguments:
    input_str -- It should be string
    Returns: English numbers
    """
    mapping = {
        '۰': '0',
        '۱': '1',
        '۲': '2',
        '۳': '3',
        '۴': '4',
        '۵': '5',
        '۶': '6',
        '۷': '7',
        '۸': '8',
        '۹': '9',
        '.': '.',
    }
    return _multiple_replace(mapping, input_str)


def convert_en_numbers(input_str):
    mapping = {
        '0': '۰',
        '1': '۱',
        '2': '۲',
        '3': '۳',
        '4': '۴',
        '5': '۵',
        '6': '۶',
        '7': '۷',
        '8': '۸',
        '9': '۹',
        '.': '.',
    }
    return _multiple_replace(mapping, input_str)


def _multiple_replace(mapping, text):
    """
    Internal function for replace all mapping keys for a input string
    :param mapping: replacing mapping keys
    :param text: user input string
    :return: New string with converted mapping keys to values
    """
    pattern = "|".join(map(re.escape, mapping.keys()))
    return re.sub(pattern, lambda m: mapping[m.group()], str(text))


def convert_sheet_ids_dic_to_str(dic):
    sheet_ids_str = ''
    for key, value in dic.items():
        sheet_ids_str += f'{key}:{value}\n'
    return sheet_ids_str[:-1]


def isEnglish(s):
    try:
        s.encode(encoding='utf-8').decode('ascii')
    except UnicodeDecodeError:
        return False
    else:
        return True


def convert_fa_number_to_en(data_frame):
    for i in range(data_frame.shape[0]):
        for j in range(data_frame.shape[1]):
            try:
                data_frame.iloc[i, j] = fa_to_en(data_frame.iloc[i, j])
            except Exception as e:
                pass
    return pd.DataFrame(data_frame)


def find_error_line():
    exception_type, exception_object, exception_traceback = sys.exc_info()
    line_number = exception_traceback.tb_lineno
    return str(line_number)


def readable_tedad(n):
    human_readable = ''
    n = abs(float(n))
    if n >= 1e6 and n <= 1e9:
        round_number = n/1e6
        human_readable = '{:,.0f}{}'.format(round_number,   ' میلیون ')
    elif n > 1e9:
        round_number = n/1e9

        human_readable = '{:,.0f}{}'.format(round_number, ' میلیارد ')
    else:
        human_readable = '{:,.0f}'.format(n)
    return convert_en_numbers(human_readable)


def readable(n):
    human_readable = ''
    n = abs(float(n))
    if n >= 1e7 and n <= 1e10:
        round_number = n/1e7
        human_readable = '{:,.0f}{}'.format(round_number,   ' میلیون تومان ')
    elif n > 1e10:
        round_number = n/1e10

        human_readable = '{:,.2f}{}'.format(round_number, ' میلیارد تومان ')
    else:
        round_number = n/10
        human_readable = '{:,.1f}{}'.format(round_number, 'تومان')
    return convert_en_numbers(human_readable)


def range_char(start, stop):
    return list(chr(n) for n in range(ord(start), ord(stop) + 1))
