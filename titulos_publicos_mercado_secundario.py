#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import csv
import os
from datetime import datetime, timedelta

import pandas as pd
import requests
from tqdm import tqdm

import utils


def get_ultima_data_disponivel_base(path_file_base):
    # verifica a última data disponível na base
    with open(path_file_base, 'r') as f:
        for row in reversed(list(csv.reader(f))):
            data = row[0].split(';')[0]
            if data == 'dt_referencia':
                return None
            data = row[0].split(';')[0]
            return datetime.strptime(data, '%Y-%m-%d').date()


def remove_old_files():
    file_list = os.listdir(r"downloads")
    for file_name in file_list:
        if not file_name.endswith('.xls'):
            continue
        today = datetime.now().strftime('%d.%m.%Y')
        data_arquivo = file_name.split('.xls')[-2][-10:]
        if today != data_arquivo:
            os.remove(os.path.join('downloads', file_name))


def download_file(url, dt_referencia, file_name):
    dt_referencia = dt_referencia.strftime('%y%m%d')
    url = url + dt_referencia + '.txt'
    response = requests.get(url, stream=True)
    with open(file_name, "wb") as handle:
        for data in tqdm(response.iter_content()):
            handle.write(data)
    handle.close()


def generate_csv_base(df, path_file_base):
    # organizar o arquivo base por dt_referencia
    df = pd.read_csv(path_file_base, sep=';')
    df = df.sort_values('dt_referencia')
    # set the index
    df.set_index('dt_referencia', inplace=True)
    df.to_csv(path_file_base, sep=';')


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


def main():
    # apaga arquivos antigos
    remove_old_files()
    # verifica a última data disponível na base
    name_file_base = 'ima_quadro_resumo_base.csv'
    path_file_base = os.path.join('bases', name_file_base)

    # ultima data base dispon[ivel
    ultima_data_base = get_ultima_data_disponivel_base(path_file_base)
    print('Última data base disponível:', ultima_data_base)
    if (ultima_data_base is None):
        ultima_data_base = datetime.date(2010, 11, 17)

    # faz o download do csv no site da anbima
    # lft
    url = 'http://www.anbima.com.br/informacoes/merc-sec/arqs/ms'

    # verifica a última data disponível na base
    today = datetime.now().date()
    cal = utils.get_calendar()
    ultima_data_base = cal.offset(today, -5)
    dates_range = list(utils.datetime_range(start=ultima_data_base, end=today))

    path_download = os.path.join(
        'downloads', 'titulos-publicos-merc-secundario')
    if not os.path.exists(path_download):
        os.makedirs(path_download)

    for dt_referencia in reversed(dates_range):
        file_path = os.path.join(
            path_download,
            dt_referencia.strftime('%Y%m%d') + '_ms_titulos-publicos.txt'
        )

        # verifica se o arquivo deve ser baixado
        if not utils.check_download(dt_referencia, file_path):
            continue

        print(file_path)
        # faz o download do arquivo caso ele ainda não tiver sido baixado
        if not os.path.exists(file_path):
            download_file(url, dt_referencia, file_path)

    print("Arquivos baixados com sucesso")


if __name__ == '__main__':
    main()
