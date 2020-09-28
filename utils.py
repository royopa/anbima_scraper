#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import csv
import datetime
import os
import random
from datetime import timedelta

import pandas as pd
import requests
from bizdays import Calendar, load_holidays
from tqdm import tqdm


def load_useragents():
    uas = []
    with open("user-agents.txt", 'rb') as uaf:
        for ua in uaf.readlines():
            if ua:
                uas.append(ua.strip()[0:-1-0])
    random.shuffle(uas)
    return uas


def check_download(dt_referencia, file_name):
    if not isbizday(dt_referencia):
        print(dt_referencia, 'não é dia útil')
        return False
    if os.path.exists(file_name):
        print(file_name, 'arquivo já baixado')
        return False
    return True


def download(url, params, file_name):
    headers = {'User-Agent': random.choice(load_useragents())}
    response = requests.get(url, params=params, stream=True, headers=headers)
    if response.status_code != 200:
        'Nenhum arquivo encontrado nessa url'
        return False
    with open(file_name, "wb") as handle:
        for data in tqdm(response.iter_content()):
            handle.write(data)
    handle.close()


def get_ultima_data_disponivel_base(path_file_base):
    # verifica a última data disponível na base
    with open(path_file_base, 'r') as f:
        for row in reversed(list(csv.reader(f))):
            data = row[0].split(';')[0]
            if data == 'dt_referencia':
                return None
            data = row[0].split(';')[0]
            return datetime.datetime.strptime(data, '%Y-%m-%d').date()


def generate_xlsx_base(df, path_saida):
    # Create a Pandas Excel writer using XlsxWriter as the engine.
    writer = pd.ExcelWriter(path_saida, engine='xlsxwriter')
    # Convert the dataframe to an XlsxWriter Excel object.
    df.to_excel(writer, sheet_name='Sheet1')
    # Close the Pandas Excel writer and output the Excel file.
    writer.save()


def xrange(x):
    return iter(range(x))


def datetime_range(start=None, end=None):
    span = end - start
    for i in xrange(span.days + 1):
        yield start + timedelta(days=i)


def remove_zero_files(folder_name):
    file_list = os.listdir(r"downloads/"+folder_name+"/")
    for file_name in file_list:
        if not file_name.endswith('.csv'):
            continue
        path_file = os.path.join('downloads', folder_name, file_name)
        with open(path_file, 'r', encoding='latin1') as f:
            first_line = f.readline()
            if 'Não há dados disponíveis' in first_line or 'error' in first_line or '<' in first_line:
                os.remove(path_file)


def generate_csv_base(path_file_base):
    # organizar o arquivo base por dt_referencia
    df = pd.read_csv(path_file_base, sep=';')
    df = df.sort_values('dt_referencia')
    # set the index
    df.set_index('dt_referencia', inplace=True)
    df.to_csv(path_file_base, sep=';')


def get_calendar():
    holidays = load_holidays('ANBIMA.txt')
    return Calendar(holidays, ['Sunday', 'Saturday'])


def isbizday(dt_referencia):
    cal = get_calendar()
    return cal.isbizday(dt_referencia)


def get_ultima_data_base(path_file_base):
    ultima_data_base = get_ultima_data_disponivel_base(path_file_base)
    print('Última data base disponível:', ultima_data_base)
    if (ultima_data_base is None):
        return datetime.date(2015, 1, 1)
    return ultima_data_base


def prepare_download_folder(name_download_folder):
    path_download = os.path.join('downloads')
    if not os.path.exists(path_download):
        os.makedirs(path_download)
    path_download = os.path.join('downloads', name_download_folder)
    if not os.path.exists(path_download):
        os.makedirs(path_download)
    return path_download
