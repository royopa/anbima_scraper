"""Curves scrapers for ANBIMA data."""

import logging
from datetime import date
from typing import Optional

from ..core.scraper import BaseScraper

logger = logging.getLogger(__name__)


class CurvesScraper(BaseScraper):
    """Base scraper for curves data."""

    def __init__(self, name: str):
        """Initialize the curves scraper.

        Args:
            name: Scraper name
        """
        super().__init__(name)

    def scrape(self, start_date: Optional[date] = None, 
               end_date: Optional[date] = None) -> bool:
        """Scrape curves data.

        Args:
            start_date: Start date (not implemented yet)
            end_date: End date (not implemented yet)

        Returns:
            True if successful, False otherwise
        """
        logger.warning(f"{self.name} scraper not implemented yet")
        return False


class CurvaJurosFechamentoScraper(CurvesScraper):
    """Scraper for Curva de Juros Fechamento."""

    def __init__(self):
        """Initialize the Curva de Juros Fechamento scraper."""
        super().__init__("curva_juros_fechamento") 