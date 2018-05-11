#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import requests
import time
import csv
import datetime
import os
import pandas as pd
import pyexcel_xls
from tqdm import tqdm
from datetime import timedelta
from bizdays import Calendar
from bizdays import load_holidays


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


def download_file(url, dt_referencia, file_name):
    dt_referencia = dt_referencia.strftime('%d/%m/%Y')
    params = {
        'Titulo_1': 'quadro-resumo',
        'Consulta_1': 'Ambos',
        'Dt_Ref': dt_referencia,
        'DataIni': dt_referencia,
        'DataFim': dt_referencia,
        'Indice': 'quadro-resumo',
        'Consulta': 'Ambos',
        'saida': 'csv',
        'Idioma': 'PT'
    }

    response = requests.get(url, params=params, stream=True)
    with open(file_name, "wb") as handle:
        for data in tqdm(response.iter_content()):
            handle.write(data)
    handle.close()


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
            if 'Não há dados disponíveis para' in first_line or 'error' in first_line or '<' in first_line:
                os.remove(path_file)


def import_files(folder_name, path_file_base):
    file_list = os.listdir(r"downloads/"+folder_name+"/")
    for file_name in file_list:
        if not file_name.endswith('.csv'):
            continue
        path_file = os.path.join('downloads', folder_name, file_name)
        with open(path_file, 'r', encoding='latin1') as f:
            first_line = f.readline()
            if 'QUADRO-RESUMO' in first_line:
                print('extrair', path_file)
                df = pd.read_csv(path_file, sep=';', skiprows=1, encoding='latin1', header=0)
                df['Data de Referência'] = pd.to_datetime(df['Data de Referência'], format='%d/%m/%Y', errors='ignore')

                # importa para o csv base
                with open(path_file_base, 'a', newline='') as baseFile:
                    fieldnames = [
                        'dt_referencia',
                        'no_indice',
                        'nu_indice',
                        'var_diaria_perc',
                        'var_mensal_perc',
                        'var_anual_perc',
                        'var_ult_12_meses_perc',
                        'var_ult_24_meses_perc',
                        'peso_perc',
                        'duration_du',
                        'carteira_mercado_reais_mil',
                        'nu_operacoes',
                        'qt_negociada_1000_tit',
                        'vr_negociado_reais_mil',
                        'pmr',
                        'convexidade',
                        'yield',
                        'redemption_yield'
                    ]
                    writer = csv.DictWriter(baseFile, fieldnames=fieldnames, delimiter=';', quoting=csv.QUOTE_NONNUMERIC)
                    # insere cada registro na database
                    for index, row in df.iterrows():
                        row_inserted = {
                            'dt_referencia': row['Data de Referência'].date(),
                            'no_indice': row['Índice'],
                            'nu_indice': row['Número Índice'],
                            'var_diaria_perc': row['Variação Diária (%)'],
                            'var_mensal_perc': row['Variação Mensal (%)'],
                            'var_anual_perc': row['Variação Anual (%)'],
                            'var_ult_12_meses_perc': row['Variação Últimos 12 Meses (%)'],
                            'var_ult_24_meses_perc': row['Variação Últimos 24 Meses (%)'],
                            'peso_perc': row['Peso (%)'],
                            'duration_du': row['Duration (d.u.)'],
                            'carteira_mercado_reais_mil': row['Carteira a Mercado (R$ mil)'],
                            'nu_operacoes': row['Número de Operações *'],
                            'qt_negociada_1000_tit': row['Quant. Negociada (1.000 títulos) *'],
                            'vr_negociado_reais_mil': row['Valor Negociado (R$ mil) *'],
                            'pmr': row['PMR'],
                            'convexidade': row['Convexidade'],
                            'yield': row['Yield'],
                            'redemption_yield': row['Redemption Yield']
                        }
                        writer.writerow(row_inserted)


def generate_csv_base(path_file_base):
    # organizar o arquivo base por dt_referencia
    df = pd.read_csv(path_file_base, sep=';')
    df = df.sort_values('dt_referencia')
    # set the index
    df.set_index('dt_referencia', inplace=True)
    df.to_csv(path_file_base, sep=';')


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
        ultima_data_base = datetime.date(2010, 1, 1)

    # faz o download do csv no site da anbima
    url = 'http://www.anbima.com.br/informacoes/ima/IMA-geral-down.asp'
    today = datetime.datetime.now().date()
    path_download = os.path.join('downloads', 'quadro-resumo')
    if not os.path.exists(path_download):
        os.makedirs(path_download)

    holidays = load_holidays('ANBIMA.txt')
    cal = Calendar(holidays, ['Sunday', 'Saturday'])

    for dt_referencia in reversed(list(datetime_range(start=ultima_data_base, end=today))):
        if not cal.isbizday(dt_referencia):
            continue
        # quadro geral
        file_name = os.path.join(path_download, dt_referencia.strftime('%Y%m%d') + '_ima_quadro_resumo.csv')
        print(file_name)
        # faz o download do arquivo caso ele ainda não tiver sido baixado
        if not os.path.exists(file_name):
            download_file(url, dt_referencia, file_name)

    remove_zero_files('quadro-resumo')
    import_files('quadro-resumo', path_file_base)

    # organizar o arquivo base por dt_referencia
    generate_csv_base(path_file_base)
    print("Arquivos baixados com sucesso e importados para a base de dados")


if __name__ == '__main__':
    main()