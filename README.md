[![Build Status](https://travis-ci.org/royopa/anbima-scraper.svg?branch=master)](https://travis-ci.org/royopa/anbima-scraper)

ANBIMA scraper
--------------

ANBIMA scraper é um projeto para captura de dados do site da [ANBIMA](https://www.anbima.com.br/).

## Instalar dependências do projeto

Para instalar as dependências do projeto utilize o comando abaixo:

```sh
> cd anbima_scraper
> pip install -r requirements.txt
```

Ou caso vocë utilize o pipenv, utilize o comando abaixo e ative o virtualenv:

```sh
> cd anbima_scraper
> pipenv install
> pipenv shell
```

## Utilizando os programas

#### Fazer o download e atualizar a base de dados

Para fazer o download dos preços e atualizar as [bases de dados](https://github.com/royopa/anbima-scraper/blob/master/bases/) basta executar os programas com os comandos abaixo:

### IDkA - Índice de Duração Constante ANBIMA
Fonte: https://www.anbima.com.br/pt_br/informar/consulta-idka.htm
```sh
> python idka.py
```

### Mercado Secundário de Debêntures - Taxas Médias

```sh
> python debentures_mercado_secundario.py
```

### Carteiras IMA
Fonte: https://www.anbima.com.br/pt_br/informar/ima-carteira-teorica.htm

```sh
> python ima_carteiras.py
```

### IMA Quadro Resumo
Fonte: https://www.anbima.com.br/pt_br/informar/ima-resultados-diarios.htm


```sh
> python ima_quadro_resumo.py
```

## TO DO

### Indicadores ANBIMA

SELIC, CDI, IGP-M, IPCA, Dólar, Euro, TR, TBF, FDS

https://www.anbima.com.br/informacoes/indicadores/
https://www.anbima.com.br/informacoes/indicadores/arqs/indicadores.xls


### Curva de Juros - Intradia
Fonte: https://www.anbima.com.br/pt_br/informar/curva-de-juros-intradia.htm

Disponibiliza as curvas de juros zero-cupom soberanas, prefixada e IPCA, extraídas a partir da coleta de spreads de compra e venda realizada pela Associação às 12h, a partir de 27/03/2017. Até 24/03/2017, as curvas consideravam os spreads coletados de 12h30.


### Curvas de Juros - Fechamento
https://www.anbima.com.br/pt_br/informar/curvas-de-juros-fechamento.htm


### Sistema Curvas de Crédito
Estão disponíveis para consulta os valores da curva de crédito referentes aos últimos 5 dias úteis. 
https://www.anbima.com.br/pt_br/informar/sistema-curvas-de-credito.htm

### Consulta - IDA - Índice de Debêntures ANBIMA
https://www.anbima.com.br/pt_br/informar/consulta-ida.htm



### IHFA - Índice de Hedge Funds ANBIMA
Fonte: https://www.anbima.com.br/pt_br/informar/consulta-ihfa.htm

