"""
ANBIMA Scraper - Web scraper para captura de dados financeiros da ANBIMA.

Este pacote fornece ferramentas para capturar dados financeiros do site da ANBIMA,
incluindo índices, indicadores, curvas de juros e outros dados de mercado.
"""

__version__ = "2.0.0"
__author__ = "Original Author"
__email__ = "royopa@gmail.com"

from .core.scraper import ANBIMAScraper
from .scrapers.idka import IDKAScraper
from .scrapers.indicators import IndicatorsScraper
from .scrapers.ima import IMAScraper
from .scrapers.curves import CurvesScraper
from .scrapers.debentures import DebenturesScraper

__all__ = [
    "ANBIMAScraper",
    "IDKAScraper", 
    "IndicatorsScraper",
    "IMAScraper",
    "CurvesScraper",
    "DebenturesScraper",
] 