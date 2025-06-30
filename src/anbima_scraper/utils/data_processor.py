"""Data processing utilities for ANBIMA scraper."""

import csv
import logging
from datetime import date, datetime
from pathlib import Path
from typing import Dict, List, Optional, Union

import pandas as pd

from ..config.settings import DATA_SETTINGS

logger = logging.getLogger(__name__)


class DataProcessor:
    """Data processing utilities."""

    @staticmethod
    def read_csv_safe(
        file_path: Union[str, Path],
        encoding: str = "utf-8",
        **kwargs
    ) -> Optional[pd.DataFrame]:
        """Safely read CSV file.

        Args:
            file_path: Path to CSV file
            encoding: File encoding
            **kwargs: Additional pandas read_csv arguments

        Returns:
            DataFrame if successful, None otherwise
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            logger.warning(f"File not found: {file_path}")
            return None
        
        try:
            df = pd.read_csv(
                file_path,
                encoding=encoding,
                sep=DATA_SETTINGS["csv_separator"],
                **kwargs
            )
            logger.debug(f"Successfully read CSV: {file_path}")
            return df
        except Exception as e:
            logger.error(f"Error reading CSV {file_path}: {e}")
            return None

    @staticmethod
    def save_csv_safe(
        df: pd.DataFrame,
        file_path: Union[str, Path],
        mode: str = "w",
        **kwargs
    ) -> bool:
        """Safely save DataFrame to CSV.

        Args:
            df: DataFrame to save
            file_path: Output file path
            mode: Write mode ('w' or 'a')
            **kwargs: Additional pandas to_csv arguments

        Returns:
            True if successful, False otherwise
        """
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            df.to_csv(
                file_path,
                mode=mode,
                encoding=DATA_SETTINGS["encoding"],
                sep=DATA_SETTINGS["csv_separator"],
                index=False,
                **kwargs
            )
            logger.info(f"Successfully saved CSV: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving CSV {file_path}: {e}")
            return False

    @staticmethod
    def get_last_date_from_csv(file_path: Union[str, Path]) -> Optional[date]:
        """Get last date from CSV file.

        Args:
            file_path: Path to CSV file

        Returns:
            Last date if found, None otherwise
        """
        df = DataProcessor.read_csv_safe(file_path)
        if df is None or df.empty:
            return None
        
        # Try common date column names
        date_columns = ['dt_referencia', 'data_referencia', 'date', 'data']
        
        for col in date_columns:
            if col in df.columns:
                try:
                    # Convert to datetime and get max date
                    df[col] = pd.to_datetime(df[col], errors='coerce')
                    max_date = df[col].max()
                    if pd.notna(max_date):
                        return max_date.date()
                except Exception as e:
                    logger.debug(f"Error processing date column {col}: {e}")
                    continue
        
        logger.warning(f"No valid date column found in {file_path}")
        return None

    @staticmethod
    def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
        """Clean DataFrame by removing invalid rows.

        Args:
            df: DataFrame to clean

        Returns:
            Cleaned DataFrame
        """
        if df.empty:
            return df
        
        # Remove rows with all NaN values
        initial_rows = len(df)
        df = df.dropna(how='all')
        
        # Remove rows with error messages
        error_patterns = [
            'Não há dados disponíveis',
            'error',
            '<',
            'Nenhum arquivo encontrado'
        ]
        
        for pattern in error_patterns:
            mask = df.astype(str).apply(
                lambda x: x.str.contains(pattern, case=False, na=False)
            ).any(axis=1)
            df = df[~mask]
        
        removed_rows = initial_rows - len(df)
        if removed_rows > 0:
            logger.info(f"Removed {removed_rows} invalid rows")
        
        return df

    @staticmethod
    def sort_by_date(
        df: pd.DataFrame,
        date_column: str = 'dt_referencia'
    ) -> pd.DataFrame:
        """Sort DataFrame by date column.

        Args:
            df: DataFrame to sort
            date_column: Name of date column

        Returns:
            Sorted DataFrame
        """
        if df.empty or date_column not in df.columns:
            return df
        
        try:
            df[date_column] = pd.to_datetime(df[date_column])
            df = df.sort_values(date_column)
            df.set_index(date_column, inplace=True)
            return df
        except Exception as e:
            logger.error(f"Error sorting by date: {e}")
            return df

    @staticmethod
    def filter_by_date_range(
        df: pd.DataFrame,
        start_date: date,
        end_date: date,
        date_column: str = 'dt_referencia'
    ) -> pd.DataFrame:
        """Filter DataFrame by date range.

        Args:
            df: DataFrame to filter
            start_date: Start date
            end_date: End date
            date_column: Name of date column

        Returns:
            Filtered DataFrame
        """
        if df.empty or date_column not in df.columns:
            return df
        
        try:
            df[date_column] = pd.to_datetime(df[date_column])
            mask = (df[date_column].dt.date >= start_date) & \
                   (df[date_column].dt.date <= end_date)
            return df[mask]
        except Exception as e:
            logger.error(f"Error filtering by date range: {e}")
            return df

    @staticmethod
    def remove_duplicates(
        df: pd.DataFrame,
        subset: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """Remove duplicate rows from DataFrame.

        Args:
            df: DataFrame to deduplicate
            subset: Columns to consider for duplicates

        Returns:
            DataFrame without duplicates
        """
        if df.empty:
            return df
        
        initial_rows = len(df)
        df = df.drop_duplicates(subset=subset)
        removed_rows = initial_rows - len(df)
        
        if removed_rows > 0:
            logger.info(f"Removed {removed_rows} duplicate rows")
        
        return df 