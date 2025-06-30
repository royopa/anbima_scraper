"""Main ANBIMA scraper class."""

import logging
from datetime import date
from typing import Dict, List, Optional

from ..scrapers.debentures import DebenturesScraper
from ..scrapers.idka import IDKAScraper
from ..scrapers.ima import IMAQuadroResumoScraper, IMACarteirasScraper
from ..scrapers.curves import CurvaJurosFechamentoScraper
from ..scrapers.indicators import IndicatorsScraper

logger = logging.getLogger(__name__)


class ANBIMAScraper:
    """Main class to coordinate all ANBIMA scrapers."""

    def __init__(self):
        """Initialize the ANBIMA scraper."""
        self.scrapers = {
            "indicators": IndicatorsScraper(),
            "idka": IDKAScraper(),
            "ima_carteiras": IMACarteirasScraper(),
            "ima_quadro_resumo": IMAQuadroResumoScraper(),
            "curva_juros_fechamento": CurvaJurosFechamentoScraper(),
            "debentures": DebenturesScraper(),
        }

    def run_all(self, force_update: bool = False) -> Dict[str, bool]:
        """Run all scrapers.

        Args:
            force_update: Force update even if data exists

        Returns:
            Dictionary with scraper results
        """
        logger.info("Starting ANBIMA scraper for all data sources")
        
        results = {}
        
        for name, scraper in self.scrapers.items():
            logger.info(f"Running {name} scraper")
            try:
                success = scraper.run(force_update=force_update)
                results[name] = success
                
                if success:
                    logger.info(f"{name} scraper completed successfully")
                else:
                    logger.error(f"{name} scraper failed")
                    
            except Exception as e:
                logger.error(f"Error running {name} scraper: {e}")
                results[name] = False
        
        # Log summary
        successful = sum(1 for success in results.values() if success)
        total = len(results)
        
        logger.info(f"ANBIMA scraper completed: {successful}/{total} successful")
        
        return results

    def run_scraper(self, scraper_name: str, 
                   force_update: bool = False) -> bool:
        """Run a specific scraper.

        Args:
            scraper_name: Name of the scraper to run
            force_update: Force update even if data exists

        Returns:
            True if successful, False otherwise
        """
        if scraper_name not in self.scrapers:
            logger.error(f"Unknown scraper: {scraper_name}")
            return False
        
        logger.info(f"Running {scraper_name} scraper")
        
        try:
            scraper = self.scrapers[scraper_name]
            success = scraper.run(force_update=force_update)
            
            if success:
                logger.info(f"{scraper_name} scraper completed successfully")
            else:
                logger.error(f"{scraper_name} scraper failed")
            
            return success
            
        except Exception as e:
            logger.error(f"Error running {scraper_name} scraper: {e}")
            return False

    def run_multiple(self, scraper_names: List[str], 
                    force_update: bool = False) -> Dict[str, bool]:
        """Run multiple specific scrapers.

        Args:
            scraper_names: List of scraper names to run
            force_update: Force update even if data exists

        Returns:
            Dictionary with scraper results
        """
        logger.info(f"Running scrapers: {', '.join(scraper_names)}")
        
        results = {}
        
        for name in scraper_names:
            if name not in self.scrapers:
                logger.error(f"Unknown scraper: {name}")
                results[name] = False
                continue
            
            results[name] = self.run_scraper(name, force_update)
        
        return results

    def get_available_scrapers(self) -> List[str]:
        """Get list of available scrapers.

        Returns:
            List of scraper names
        """
        return list(self.scrapers.keys())

    def get_scraper_status(self) -> Dict[str, Optional[date]]:
        """Get status of all scrapers (last available date).

        Returns:
            Dictionary with scraper names and their last available dates
        """
        status = {}
        
        for name, scraper in self.scrapers.items():
            try:
                last_date = scraper.get_last_available_date()
                status[name] = last_date
            except Exception as e:
                logger.error(f"Error getting status for {name}: {e}")
                status[name] = None
        
        return status 