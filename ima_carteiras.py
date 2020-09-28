#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import csv
import datetime
import os
import time
from datetime import timedelta

import pandas as pd
import pyexcel_xls
import requests
from tqdm import tqdm


def get_ultima_data_disponivel_base(path_file_base):
    # verifica a última data disponível na base
    with open(path_file_base, 'r') as f:
        for row in reversed(list(csv.reader(f))):
            data = row[0].split(';')[0]
            if data == 'dt_referencia':
                return None
            data = row[0].split(';')[0]
            return datetime.datetime.strptime(data, '%Y-%m-%d').date()


def remove_old_files():
    file_list = os.listdir(r"downloads")
    for file_name in file_list:
        if not file_name.endswith('.xls'):
            continue
        today = datetime.datetime.now().strftime('%d.%m.%Y')
        data_arquivo = file_name.split('.xls')[-2][-10:]
        if today != data_arquivo:
            os.remove(os.path.join('downloads', file_name))


def download_file_carteira(url, dt_referencia, file_name, indice):
    dt_referencia = dt_referencia.strftime('%d/%m/%Y')
    params = {
        'Titulo_1': 'indice',
        'Indice': 'indice',
        'Consulta_1': 'Ambos',
        'Dt_Ref': dt_referencia,
        'DataIni': dt_referencia,
        'DataFim': dt_referencia,
        'Consulta': 'Ambos',
        'saida': 'csv',
        'Idioma': 'PT'
    }

    response = requests.get(url, params=params, stream=True)
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

    carteiras = [
        'irf-m',
        'irf-m 1',
        'irf-m 1+',
        'ima-b',
        'ima-b 5',
        'ima-b 5+',
        'ima-c',
        'ima-s',
        'ima-geral',
        'ima-geral ex-c'
    ]

    # faz o download do csv no site da anbima
    url = 'http://www.anbima.com.br/informacoes/ima/ima-carteira-down.asp'
    today = datetime.datetime.now().date()
    for dt_referencia in reversed(list(datetime_range(start=ultima_data_base, end=today))):
        for carteira in carteiras:
            path_download = os.path.join('downloads', carteira)
            if not os.path.exists(path_download):
                os.makedirs(path_download)

            file_name = os.path.join(
                path_download,
                dt_referencia.strftime('%Y%m%d') + '_' + carteira + '.csv'
            )
            print(file_name)
            # faz o download do arquivo caso ele ainda não tiver sido baixado
            if not os.path.exists(file_name):
                download_file_carteira(url, dt_referencia, file_name, carteira)

    print("Arquivos baixados com sucesso e importados para a base de dados")


if __name__ == '__main__':
    main()
