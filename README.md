[![Build Status](https://travis-ci.org/royopa/anbima-scraper.svg?branch=master)](https://travis-ci.org/royopa/anbima-scraper)

ANBIMA scraper
--------------

ANBIMA scraper é um projeto para captura de dados do site da ANBIMA ().

## Instalar dependências do projeto

Para instalar as dependências do projeto utilize o comando abaixo:

```sh
> cd anbima-scraper
> pip install -r requirements.txt
```

ou caso vocë utilize o pipenv, utilize o comando abaixo e ative o virtualenv:

```sh
> cd anbima-scraper
> pipenv install
> pipenv shell
```

## Utilizando os programas

### IDkA - Índice de Duração Constante ANBIMA

#### Fazer o download e atualizar a base de dados

Para fazer o download dos preços e atualizar a [base de dados](https://github.com/royopa/anbima-scraper/blob/master/bases/) basta executar o programa [main.py](https://github.com/royopa/anbima-scraper/blob/master/idka.py) com o comando abaixo:

```sh
> python idka.py
```
