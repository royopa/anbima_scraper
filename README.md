# ANBIMA Scraper

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)

> **Web scraper moderno e robusto para captura de dados financeiros da ANBIMA (Associação Brasileira das Entidades dos Mercados Financeiro e de Capitais)**

## 📋 Índice

- [Visão Geral](#visão-geral)
- [Funcionalidades](#funcionalidades)
- [Instalação](#instalação)
- [Uso Rápido](#uso-rápido)
- [Documentação Detalhada](#documentação-detalhada)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Contribuição](#contribuição)
- [Licença](#licença)

## 🎯 Visão Geral

O **ANBIMA Scraper** é uma ferramenta Python moderna e robusta para capturar dados financeiros do site da ANBIMA. O projeto foi completamente refatorado aplicando as melhores práticas de desenvolvimento, incluindo:

- ✅ **Arquitetura orientada a objetos** com classes bem estruturadas
- ✅ **Sistema de logging robusto** com diferentes níveis e outputs
- ✅ **Tratamento de erros avançado** com retry automático
- ✅ **Interface de linha de comando (CLI)** intuitiva
- ✅ **Configuração centralizada** e flexível
- ✅ **Type hints** para melhor desenvolvimento
- ✅ **Testes automatizados** (estrutura preparada)
- ✅ **Documentação completa** com docstrings

### 🚀 Principais Melhorias

- **Estrutura modular**: Código organizado em módulos específicos
- **Reutilização**: Classe base `BaseScraper` com funcionalidades comuns
- **Robustez**: Cliente HTTP com retry e rotação de user agents
- **Flexibilidade**: Configuração via arquivos e variáveis de ambiente
- **Monitoramento**: Logs detalhados para troubleshooting
- **Performance**: Download apenas de dados novos

## 📊 Funcionalidades

### 🎯 Scrapers Implementados

| Scraper | Status | Descrição | Dados Capturados |
|---------|--------|-----------|------------------|
| **Indicators** | ✅ Completo | Indicadores financeiros | SELIC, CDI, IPCA, IGP-M, Dólar, Euro, TR, TBF, FDS |
| **IDKA** | ✅ Completo | Índice de Duração Constante ANBIMA | Retornos, volatilidade, taxas de juros |
| **IMA Carteiras** | 🔄 Estrutura | Carteiras teóricas IMA | Composição de carteiras |
| **IMA Quadro Resumo** | 🔄 Estrutura | Quadro resumo IMA | Resultados diários |
| **Curvas de Juros** | 🔄 Estrutura | Curvas de juros fechamento | Curvas zero-cupom |
| **Debêntures** | 🔄 Estrutura | Mercado secundário de debêntures | Taxas médias |

### 🔧 Funcionalidades Avançadas

- **Verificação automática**: Detecta dados existentes e baixa apenas o necessário
- **Processamento seguro**: Limpeza automática de dados inválidos
- **Deduplicação**: Remove registros duplicados automaticamente
- **Ordenação**: Organiza dados por data de referência
- **Validação**: Verifica integridade dos dados baixados
- **Logs estruturados**: Rastreamento completo das operações

## 🛠️ Instalação

### Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

### Instalação Básica

```bash
# Clone o repositório
git clone https://github.com/royopa/anbima_scraper.git
cd anbima_scraper

# Instale as dependências
pip install -r requirements.txt
```

### Instalação em Modo Desenvolvimento

```bash
# Clone o repositório
git clone https://github.com/royopa/anbima_scraper.git
cd anbima_scraper

# Instale em modo desenvolvimento
pip install -e .

# Instale dependências de desenvolvimento
pip install -r requirements.txt
```

### Configuração Inicial

1. **Crie os diretórios necessários** (criados automaticamente):
   ```bash
   mkdir -p data/raw data/processed logs
   ```

2. **Configure arquivos opcionais**:
   - `user-agents.txt`: Lista de user agents para rotação
   - `ANBIMA.txt`: Arquivo de feriados da ANBIMA

## 🚀 Uso Rápido

### Interface de Linha de Comando (CLI)

```bash
# Executar todos os scrapers
python -m anbima_scraper run-all

# Executar apenas indicadores
python -m anbima_scraper run indicators

# Executar múltiplos scrapers
python -m anbima_scraper run indicators idka

# Forçar atualização (mesmo se dados existirem)
python -m anbima_scraper run-all --force

# Verificar status dos scrapers
python -m anbima_scraper status

# Listar scrapers disponíveis
python -m anbima_scraper list
```

### Uso via Python

```python
from anbima_scraper import ANBIMAScraper

# Criar instância do scraper
scraper = ANBIMAScraper()

# Executar todos os scrapers
results = scraper.run_all()

# Executar scraper específico
success = scraper.run_scraper("indicators")

# Verificar status
status = scraper.get_scraper_status()

# Executar múltiplos scrapers
results = scraper.run_multiple(["indicators", "idka"])
```

### Exemplo Completo

```python
#!/usr/bin/env python3
"""
Exemplo completo de uso do ANBIMA Scraper.
"""

from anbima_scraper import ANBIMAScraper

def main():
    # Criar instância
    scraper = ANBIMAScraper()
    
    # Verificar status atual
    print("Status atual:")
    status = scraper.get_scraper_status()
    for name, last_date in status.items():
        date_str = last_date.strftime("%Y-%m-%d") if last_date else "Sem dados"
        print(f"  {name}: {date_str}")
    
    # Executar scrapers
    print("\nExecutando scrapers...")
    results = scraper.run_all()
    
    # Mostrar resultados
    print("\nResultados:")
    for name, success in results.items():
        status = "✓" if success else "✗"
        print(f"{status} {name}")

if __name__ == "__main__":
    main()
```

## 📚 Documentação Detalhada

### Configuração

O projeto usa configuração centralizada em `src/anbima_scraper/config/settings.py`:

```python
# URLs da ANBIMA
ANBIMA_URLS = {
    "indicators": "https://www.anbima.com.br/informacoes/indicadores/",
    "idka": "http://www.anbima.com.br/informacoes/idka/IDkA-down.asp",
    # ... outras URLs
}

# Configurações de requisição
REQUEST_SETTINGS = {
    "timeout": 30,
    "max_retries": 3,
    "retry_delay": 1,
    # ... outras configurações
}
```

### Estrutura de Dados

#### Indicadores ANBIMA
```csv
data_referencia,data_captura,indice,descricao,valor
2023-12-15,2023-12-15,selic,Taxa SELIC do BC2,13.75
2023-12-15,2023-12-15,cdi,DI-CETIP3,13.65
```

#### IDKA
```csv
dt_referencia,no_indexador,no_indice,nu_indice,ret_dia_perc,ret_mes_perc,ret_ano_perc,ret_12_meses_perc,vol_aa_perc,taxa_juros_aa_perc_compra_d1,taxa_juros_aa_perc_venda_d0
2023-12-15,Prefixado,IDkA-P,1234.56,0.12,2.34,15.67,18.90,8.45,13.50,13.60
```

### Logs

O sistema gera logs estruturados em `logs/anbima_scraper.log`:

```
2023-12-15 10:30:15 [INFO] anbima_scraper.core.anbima_scraper: Starting ANBIMA scraper for all data sources
2023-12-15 10:30:16 [INFO] anbima_scraper.scrapers.indicators: Scraping ANBIMA indicators
2023-12-15 10:30:18 [INFO] anbima_scraper.scrapers.indicators: Indicators data updated successfully
```

## 🏗️ Estrutura do Projeto

```
anbima_scraper/
├── src/anbima_scraper/          # Código fonte principal
│   ├── __init__.py              # Exports principais
│   ├── cli.py                   # Interface de linha de comando
│   ├── core/                    # Funcionalidades centrais
│   │   ├── __init__.py
│   │   ├── anbima_scraper.py    # Classe principal
│   │   └── scraper.py           # Classe base
│   ├── scrapers/                # Scrapers específicos
│   │   ├── __init__.py
│   │   ├── indicators.py        # Indicadores ANBIMA
│   │   ├── idka.py             # IDKA
│   │   ├── ima.py              # IMA
│   │   ├── curves.py           # Curvas de juros
│   │   └── debentures.py       # Debêntures
│   ├── utils/                   # Utilitários
│   │   ├── __init__.py
│   │   ├── http_client.py      # Cliente HTTP
│   │   ├── calendar.py         # Utilitários de calendário
│   │   └── data_processor.py   # Processamento de dados
│   └── config/                  # Configurações
│       ├── __init__.py
│       └── settings.py         # Configurações centralizadas
├── data/                        # Dados processados
│   ├── raw/                     # Dados brutos
│   └── processed/               # Dados processados
├── tests/                       # Testes
│   ├── __init__.py
│   └── test_indicators.py      # Testes dos indicadores
├── examples/                    # Exemplos de uso
│   └── basic_usage.py          # Exemplo básico
├── logs/                        # Logs do sistema
├── pyproject.toml              # Configuração do projeto
├── requirements.txt            # Dependências
├── .pre-commit-config.yaml    # Hooks de pre-commit
├── .gitignore                 # Arquivos ignorados
└── README.md                  # Este arquivo
```

### Arquitetura

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   CLI Module    │    │  Python API     │    │  Configuration  │
│                 │    │                 │    │                 │
│  run-all        │    │  ANBIMAScraper  │    │  settings.py    │
│  run            │    │  run_all()      │    │  URLs           │
│  status         │    │  run_scraper()  │    │  Settings       │
│  list           │    │  get_status()   │    │  Logging        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │  Base Scraper   │
                    │                 │
                    │  BaseScraper    │
                    │  - HTTP Client  │
                    │  - Calendar     │
                    │  - Data Proc    │
                    └─────────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Indicators     │    │     IDKA        │    │     Others      │
│                 │    │                 │    │                 │
│  - SELIC        │    │  - Returns      │    │  - IMA          │
│  - CDI          │    │  - Volatility   │    │  - Curves       │
│  - IPCA         │    │  - Rates        │    │  - Debentures   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🧪 Testes

### Executar Testes

```bash
# Executar todos os testes
pytest

# Executar com cobertura
pytest --cov=anbima_scraper

# Executar testes específicos
pytest tests/test_indicators.py

# Executar com verbose
pytest -v
```

### Estrutura de Testes

```python
# Exemplo de teste
def test_map_indicator_selic(scraper):
    """Test SELIC indicator mapping."""
    result = scraper._map_indicator("Taxa SELIC do BC2", "Descrição")
    assert result == "selic"
```

## 🔧 Desenvolvimento

### Configuração do Ambiente

```bash
# Instalar pre-commit hooks
pre-commit install

# Formatar código
black src/ tests/

# Verificar imports
isort src/ tests/

# Verificar tipos
mypy src/

# Verificar linting
flake8 src/ tests/
```

### Adicionando Novos Scrapers

1. **Criar classe do scraper**:
```python
from ..core.scraper import BaseScraper

class NewScraper(BaseScraper):
    def __init__(self):
        super().__init__("new_scraper")
    
    def scrape(self, start_date=None, end_date=None):
        # Implementar lógica do scraper
        pass
```

2. **Adicionar configurações**:
```python
# Em settings.py
ANBIMA_URLS["new_scraper"] = "https://anbima.com.br/new-endpoint"
FILE_PATHS["new_scraper"] = PROCESSED_DATA_DIR / "new_scraper.csv"
```

3. **Registrar no scraper principal**:
```python
# Em anbima_scraper.py
self.scrapers["new_scraper"] = NewScraper()
```

## 📈 Monitoramento e Logs

### Níveis de Log

- **DEBUG**: Informações detalhadas para desenvolvimento
- **INFO**: Informações gerais sobre operações
- **WARNING**: Avisos sobre situações não críticas
- **ERROR**: Erros que impedem operação normal

### Exemplo de Logs

```
2023-12-15 10:30:15 [INFO] anbima_scraper.core.anbima_scraper: Starting ANBIMA scraper for all data sources
2023-12-15 10:30:16 [INFO] anbima_scraper.scrapers.indicators: Scraping ANBIMA indicators
2023-12-15 10:30:17 [DEBUG] anbima_scraper.utils.http_client: Making GET request to: https://www.anbima.com.br/informacoes/indicadores/
2023-12-15 10:30:18 [INFO] anbima_scraper.utils.http_client: Request successful: 200
2023-12-15 10:30:19 [INFO] anbima_scraper.scrapers.indicators: Fetched indicators data: 25 rows
2023-12-15 10:30:20 [INFO] anbima_scraper.scrapers.indicators: Processed indicators data: 25 rows
2023-12-15 10:30:21 [INFO] anbima_scraper.scrapers.indicators: Indicators data updated successfully
```

## 🚨 Troubleshooting

### Problemas Comuns

#### 1. Erro de Conexão
```
Error: Request failed: Connection timeout
```
**Solução**: Verificar conectividade com internet e configurações de proxy.

#### 2. Dados Não Atualizados
```
No new data to download
```
**Solução**: Usar flag `--force` para forçar atualização.

#### 3. Erro de Permissão
```
Permission denied: logs/anbima_scraper.log
```
**Solução**: Verificar permissões do diretório `logs/`.

#### 4. Dependências Ausentes
```
ModuleNotFoundError: No module named 'pandas'
```
**Solução**: Instalar dependências com `pip install -r requirements.txt`.

### Logs de Debug

Para obter mais informações sobre problemas:

```python
import logging
logging.getLogger('anbima_scraper').setLevel(logging.DEBUG)
```

## 🤝 Contribuição

### Como Contribuir

1. **Fork** o projeto
2. **Clone** seu fork
3. **Crie** uma branch para sua feature
4. **Implemente** suas mudanças
5. **Adicione** testes
6. **Execute** os testes
7. **Commit** suas mudanças
8. **Push** para sua branch
9. **Abra** um Pull Request

### Padrões de Código

- Use **Black** para formatação
- Use **isort** para organização de imports
- Use **flake8** para linting
- Use **mypy** para type checking
- Adicione **docstrings** para todas as funções
- Escreva **testes** para novas funcionalidades

### Checklist de Pull Request

- [ ] Código segue padrões de formatação
- [ ] Testes passam
- [ ] Documentação atualizada
- [ ] Logs apropriados adicionados
- [ ] Tratamento de erros implementado

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🙏 Agradecimentos

- **ANBIMA** por disponibilizar os dados financeiros
- **Comunidade Python** pelas ferramentas e bibliotecas
- **Contribuidores** que ajudaram a melhorar o projeto

## 📞 Suporte

- **Issues**: [GitHub Issues](https://github.com/royopa/anbima_scraper/issues)
- **Documentação**: Este README e docstrings no código
- **Email**: royopa@gmail.com

---

**⭐ Se este projeto foi útil para você, considere dar uma estrela no GitHub!** 