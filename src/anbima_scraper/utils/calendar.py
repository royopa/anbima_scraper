"""Calendar utilities for business days calculation."""

import logging
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import List, Optional

from bizdays import Calendar, load_holidays

from ..config.settings import BUSINESS_DAYS_SETTINGS

logger = logging.getLogger(__name__)


class ANBIMACalendar:
    """Calendar utility for ANBIMA business days."""

    def __init__(self):
        """Initialize the ANBIMA calendar."""
        self.calendar = self._create_calendar()

    def _create_calendar(self) -> Calendar:
        """Create ANBIMA business calendar."""
        try:
            holidays = load_holidays(str(BUSINESS_DAYS_SETTINGS["holidays_file"]))
            return Calendar(
                holidays, 
                BUSINESS_DAYS_SETTINGS["weekdays"]
            )
        except Exception as e:
            logger.error(f"Error creating calendar: {e}")
            # Fallback to basic calendar without holidays
            return Calendar([], BUSINESS_DAYS_SETTINGS["weekdays"])

    def is_business_day(self, dt: date) -> bool:
        """Check if date is a business day.

        Args:
            dt: Date to check

        Returns:
            True if business day, False otherwise
        """
        return self.calendar.isbizday(dt)

    def get_business_days_range(
        self, 
        start_date: date, 
        end_date: date
    ) -> List[date]:
        """Get list of business days in range.

        Args:
            start_date: Start date
            end_date: End date

        Returns:
            List of business days
        """
        return self.calendar.bizdays(start_date, end_date)

    def get_next_business_day(self, dt: date) -> date:
        """Get next business day.

        Args:
            dt: Reference date

        Returns:
            Next business day
        """
        return self.calendar.offset(dt, 1)

    def get_previous_business_day(self, dt: date) -> date:
        """Get previous business day.

        Args:
            dt: Reference date

        Returns:
            Previous business day
        """
        return self.calendar.offset(dt, -1)

    def get_last_n_business_days(self, n: int, end_date: Optional[date] = None) -> List[date]:
        """Get last N business days.

        Args:
            n: Number of business days
            end_date: End date (defaults to today)

        Returns:
            List of business days
        """
        if end_date is None:
            end_date = date.today()
        
        start_date = self.calendar.offset(end_date, -n + 1)
        return self.get_business_days_range(start_date, end_date)

    def get_date_range_for_download(
        self, 
        last_available_date: Optional[date] = None,
        days_back: int = 6
    ) -> List[date]:
        """Get date range for data download.

        Args:
            last_available_date: Last available date in database
            days_back: Number of days to go back from today

        Returns:
            List of dates to download
        """
        today = date.today()
        
        if last_available_date is None:
            # Default to 6 business days back
            start_date = self.calendar.offset(today, -days_back)
        else:
            # Start from next business day after last available
            start_date = self.get_next_business_day(last_available_date)
        
        if start_date > today:
            logger.info("No new data to download")
            return []
        
        return self.get_business_days_range(start_date, today)


def format_date_for_anbima(dt: date) -> str:
    """Format date for ANBIMA API.

    Args:
        dt: Date to format

    Returns:
        Formatted date string
    """
    return dt.strftime("%d/%m/%Y")


def parse_anbima_date(date_str: str) -> date:
    """Parse date from ANBIMA format.

    Args:
        date_str: Date string in ANBIMA format

    Returns:
        Parsed date

    Raises:
        ValueError: If date string is invalid
    """
    try:
        return datetime.strptime(date_str, "%d/%m/%Y").date()
    except ValueError as e:
        raise ValueError(f"Invalid date format: {date_str}") from e 