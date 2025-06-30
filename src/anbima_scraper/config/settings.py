"""Configuration settings for ANBIMA scraper."""

from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent.parent.parent.parent

# Data directories
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
LOGS_DIR = BASE_DIR / "logs"

# Create directories if they don't exist
for directory in [DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# ANBIMA URLs
ANBIMA_URLS = {
    "indicators": "https://www.anbima.com.br/informacoes/indicadores/",
    "idka": "http://www.anbima.com.br/informacoes/idka/IDkA-down.asp",
    "ima_carteiras": (
        "https://www.anbima.com.br/pt_br/informar/ima-carteira-teorica.htm"
    ),
    "curva_juros_fechamento": (
        "https://www.anbima.com.br/pt_br/informar/curvas-de-juros-fechamento.htm"
    ),
    "ima_quadro_resumo": (
        "https://www.anbima.com.br/pt_br/informar/ima-resultados-diarios.htm"
    ),
    "debentures": (
        "https://www.anbima.com.br/pt_br/informar/debentures-mercado-secundario.htm"
    ),
}

# File paths
FILE_PATHS = {
    "indicators": PROCESSED_DATA_DIR / "indicators_anbima.csv",
    "idka": PROCESSED_DATA_DIR / "idka_base.csv",
    "ima_carteiras": PROCESSED_DATA_DIR / "ima_carteiras_base.csv",
    "curva_juros_fechamento": PROCESSED_DATA_DIR / "curva_juros_fechamento.csv",
    "ima_quadro_resumo": PROCESSED_DATA_DIR / "ima_quadro_resumo_base.csv",
    "debentures": PROCESSED_DATA_DIR / "debentures_base.csv",
}

# User agents file
USER_AGENTS_FILE = BASE_DIR / "user-agents.txt"

# ANBIMA holidays file
HOLIDAYS_FILE = BASE_DIR / "ANBIMA.txt"

# Request settings
REQUEST_SETTINGS = {
    "timeout": 30,
    "max_retries": 3,
    "retry_delay": 1,
    "headers": {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
    }
}

# Logging configuration
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        },
        "detailed": {
            "format": "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d: %(message)s"
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "standard",
            "stream": "ext://sys.stdout"
        },
        "file": {
            "class": "logging.FileHandler",
            "level": "DEBUG",
            "formatter": "detailed",
            "filename": LOGS_DIR / "anbima_scraper.log",
            "mode": "a",
        },
    },
    "loggers": {
        "anbima_scraper": {
            "level": "DEBUG",
            "handlers": ["console", "file"],
            "propagate": False
        },
    },
    "root": {
        "level": "INFO",
        "handlers": ["console"]
    }
}

# Data processing settings
DATA_SETTINGS = {
    "encoding": "utf-8",
    "csv_separator": ";",
    "date_format": "%Y-%m-%d",
    "datetime_format": "%Y-%m-%d %H:%M:%S",
    "anbima_date_format": "%d/%m/%Y",
}

# Business days settings
BUSINESS_DAYS_SETTINGS = {
    "calendar_name": "ANBIMA",
    "weekdays": ["Sunday", "Saturday"],
    "holidays_file": HOLIDAYS_FILE,
}

# Indicator mappings
INDICATOR_MAPPINGS = {
    "Estimativa SELIC": "selic_estimativa_anbima",
    "Taxa SELIC do BC2": "selic",
    "DI-CETIP3": "cdi",
    "IGP-M (": "igpm",
    "IGP-M1": "igpm_projecao_anbima",
    "IPCA (": "ipca",
    "IPCA1": "ipca_projecao_anbima",
    "Dolar Comercial Compra": "dolar_comercial_compra",
    "Dolar Comercial Venda": "dolar_comercial_venda",
    "Euro Compra": "euro_compra",
    "Euro Venda": "euro_venda",
    "TR2": "tr",
    "TBF2": "tbf",
    "FDS4": "fds",
} 