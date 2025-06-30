"""Base scraper class for ANBIMA data."""

import logging
from abc import ABC, abstractmethod
from datetime import date
from pathlib import Path
from typing import Dict, List, Optional, Union

import pandas as pd

from ..config.settings import FILE_PATHS
from ..utils.calendar import ANBIMACalendar, format_date_for_anbima
from ..utils.data_processor import DataProcessor
from ..utils.http_client import ANBIMAHTTPClient

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """Base class for all ANBIMA scrapers."""

    def __init__(self, name: str):
        """Initialize the scraper.

        Args:
            name: Scraper name
        """
        self.name = name
        self.calendar = ANBIMACalendar()
        self.data_processor = DataProcessor()
        self.http_client = ANBIMAHTTPClient()
        
        # Get output file path
        self.output_file = FILE_PATHS.get(name)
        if not self.output_file:
            raise ValueError(f"No output file configured for scraper: {name}")

    @abstractmethod
    def scrape(self, start_date: Optional[date] = None, 
               end_date: Optional[date] = None) -> bool:
        """Scrape data for the given date range.

        Args:
            start_date: Start date for scraping
            end_date: End date for scraping

        Returns:
            True if successful, False otherwise
        """
        pass

    def get_last_available_date(self) -> Optional[date]:
        """Get last available date from existing data.

        Returns:
            Last available date or None if no data exists
        """
        return self.data_processor.get_last_date_from_csv(self.output_file)

    def get_download_dates(self, days_back: int = 6) -> List[date]:
        """Get list of dates to download.

        Args:
            days_back: Number of business days to go back

        Returns:
            List of dates to download
        """
        last_date = self.get_last_available_date()
        return self.calendar.get_date_range_for_download(last_date, days_back)

    def should_download_date(self, dt: date, file_path: Path) -> bool:
        """Check if date should be downloaded.

        Args:
            dt: Date to check
            file_path: File path to check

        Returns:
            True if should download, False otherwise
        """
        if not self.calendar.is_business_day(dt):
            logger.info(f"{dt} is not a business day")
            return False
        
        if file_path.exists():
            logger.info(f"File already exists: {file_path}")
            return False
        
        return True

    def clean_and_save_data(self, df: pd.DataFrame) -> bool:
        """Clean and save data to output file.

        Args:
            df: DataFrame to save

        Returns:
            True if successful, False otherwise
        """
        if df.empty:
            logger.warning("No data to save")
            return False

        # Clean data
        df = self.data_processor.clean_dataframe(df)
        
        # Remove duplicates
        df = self.data_processor.remove_duplicates(df)
        
        # Sort by date
        df = self.data_processor.sort_by_date(df)
        
        # Save to file
        return self.data_processor.save_csv_safe(df, self.output_file)

    def append_data(self, df: pd.DataFrame) -> bool:
        """Append data to existing file.

        Args:
            df: DataFrame to append

        Returns:
            True if successful, False otherwise
        """
        if df.empty:
            logger.warning("No data to append")
            return False

        # Clean data
        df = self.data_processor.clean_dataframe(df)
        
        # Remove duplicates
        df = self.data_processor.remove_duplicates(df)
        
        # Append to file
        return self.data_processor.save_csv_safe(
            df, self.output_file, mode='a'
        )

    def run(self, force_update: bool = False) -> bool:
        """Run the scraper.

        Args:
            force_update: Force update even if data exists

        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Starting {self.name} scraper")
        
        try:
            if force_update:
                # Force update: scrape last 6 business days
                dates = self.calendar.get_last_n_business_days(6)
            else:
                # Normal update: get dates that need downloading
                dates = self.get_download_dates()
            
            if not dates:
                logger.info("No new data to download")
                return True
            
            logger.info(f"Downloading data for {len(dates)} dates")
            success = self.scrape(dates[0], dates[-1])
            
            if success:
                logger.info(f"{self.name} scraper completed successfully")
            else:
                logger.error(f"{self.name} scraper failed")
            
            return success
            
        except Exception as e:
            logger.error(f"Error running {self.name} scraper: {e}")
            return False
        finally:
            self.http_client.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.http_client.close() 