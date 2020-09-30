#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import csv
import os
from datetime import datetime

import pandas as pd

import utils


def download_file(url, dt_referencia, file_name):
    # verifica se o arquivo deve ser baixado
    if not utils.check_download(dt_referencia, file_name):
        return False
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
    utils.download(url, params, file_name)


def import_files(folder_name, path_file_base, ultima_data_base):
    file_list = os.listdir(r"downloads/"+folder_name+"/")
    for file_name in file_list:

        if not file_name.endswith('.csv'):
            continue

        path_file = os.path.join('downloads', folder_name, file_name)

        with open(path_file, 'r', encoding='latin1') as f:
            first_line = f.readline()
            if 'QUADRO-RESUMO' in first_line:
                print('extrair', path_file)
                df = pd.read_csv(path_file, sep=';', skiprows=1,
                                 encoding='latin1', header=0)
                df['Data de Referência'] = pd.to_datetime(
                    df['Data de Referência'],
                    format='%d/%m/%Y',
                    errors='ignore'
                )

                # seleciona apenas os registros com data de referencia maior
                # que a data base
                selecao = df['Data de Referência'] > pd.to_datetime(
                    ultima_data_base)
                df = df[selecao]

                if len(df) == 0:
                    print('Nenhum registro a ser importado', path_file)
                    os.remove(path_file)
                    continue

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
                    writer = csv.DictWriter(
                        baseFile, fieldnames=fieldnames, delimiter=';', quoting=csv.QUOTE_NONNUMERIC)
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
                os.remove(path_file)


def main():
    path_file_base = os.path.join('bases', 'ima_quadro_resumo_base.csv')
    # verifica a última data disponível na base
    ultima_data_base = utils.get_ultima_data_base(path_file_base)
    # faz o download do csv no site da anbima
    url = 'http://www.anbima.com.br/informacoes/ima/IMA-geral-down.asp'
    name_download_folder = 'quadro-resumo'
    path_download = utils.prepare_download_folder(name_download_folder)

    # verifica a última data disponível na base
    today = datetime.now().date()
    cal = utils.get_calendar()
    ultima_data_base = cal.offset(today, -6)
    dates_range = list(utils.datetime_range(start=ultima_data_base, end=today))

    for dt_referencia in reversed(dates_range):
        file_name = os.path.join(path_download, dt_referencia.strftime(
            '%Y%m%d') + '_ima_quadro_resumo.csv')
        download_file(url, dt_referencia, file_name)

    utils.remove_zero_files(name_download_folder)
    import_files(name_download_folder, path_file_base, ultima_data_base)
    # organizar o arquivo base por dt_referencia
    utils.generate_csv_base(path_file_base)
    print("Arquivos baixados com sucesso e importados para a base de dados")


if __name__ == '__main__':
    main()
