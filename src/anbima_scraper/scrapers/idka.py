"""IDKA scraper for ANBIMA data."""

import csv
import logging
from datetime import date, datetime
from pathlib import Path
from typing import List, Optional

import pandas as pd

from ..config.settings import ANBIMA_URLS, RAW_DATA_DIR
from ..core.scraper import BaseScraper
from ..utils.calendar import format_date_for_anbima, parse_anbima_date

logger = logging.getLogger(__name__)


class IDKAScraper(BaseScraper):
    """Scraper for IDKA (Índice de Duração Constante ANBIMA) data."""

    def __init__(self):
        """Initialize the IDKA scraper."""
        super().__init__("idka")
        self.download_dir = RAW_DATA_DIR / "idka"
        self.download_dir.mkdir(parents=True, exist_ok=True)

    def scrape(self, start_date: Optional[date] = None, 
               end_date: Optional[date] = None) -> bool:
        """Scrape IDKA data for the given date range.

        Args:
            start_date: Start date for scraping
            end_date: End date for scraping

        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Scraping IDKA data from {start_date} to {end_date}")
            
            # Get dates to download
            if start_date is None or end_date is None:
                dates = self.get_download_dates()
            else:
                dates = self.calendar.get_business_days_range(start_date, end_date)
            
            if not dates:
                logger.info("No dates to download")
                return True
            
            # Download files for each date
            downloaded_files = []
            for dt in dates:
                file_path = self._get_download_file_path(dt)
                
                if self.should_download_date(dt, file_path):
                    success = self._download_idka_file(dt, file_path)
                    if success:
                        downloaded_files.append(file_path)
                else:
                    logger.debug(f"Skipping download for {dt}")
            
            if not downloaded_files:
                logger.info("No new files downloaded")
                return True
            
            # Process downloaded files
            success = self._process_downloaded_files(downloaded_files)
            
            # Clean up downloaded files
            for file_path in downloaded_files:
                try:
                    file_path.unlink()
                    logger.debug(f"Cleaned up: {file_path}")
                except Exception as e:
                    logger.warning(f"Failed to clean up {file_path}: {e}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error scraping IDKA data: {e}")
            return False

    def _get_download_file_path(self, dt: date) -> Path:
        """Get download file path for a date.

        Args:
            dt: Date

        Returns:
            File path
        """
        filename = f"{dt.strftime('%Y%m%d')}_idka.csv"
        return self.download_dir / filename

    def _download_idka_file(self, dt: date, file_path: Path) -> bool:
        """Download IDKA file for a specific date.

        Args:
            dt: Date to download
            file_path: File path to save

        Returns:
            True if successful, False otherwise
        """
        try:
            url = ANBIMA_URLS["idka"]
            params = {
                'DataIni': format_date_for_anbima(dt),
                'Idioma': 'PT',
                'escolha': '2',
                'saida': 'csv'
            }
            
            success = self.http_client.download_file(url, file_path, params)
            
            if success:
                logger.info(f"Downloaded IDKA data for {dt}")
            else:
                logger.error(f"Failed to download IDKA data for {dt}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error downloading IDKA file for {dt}: {e}")
            return False

    def _process_downloaded_files(self, file_paths: List[Path]) -> bool:
        """Process downloaded IDKA files.

        Args:
            file_paths: List of file paths to process

        Returns:
            True if successful, False otherwise
        """
        try:
            all_data = []
            
            for file_path in file_paths:
                logger.info(f"Processing file: {file_path}")
                
                # Read and process file
                df = self._process_idka_file(file_path)
                if df is not None and not df.empty:
                    all_data.append(df)
                else:
                    logger.warning(f"No valid data in file: {file_path}")
            
            if not all_data:
                logger.warning("No valid data found in any downloaded files")
                return False
            
            # Combine all data
            combined_df = pd.concat(all_data, ignore_index=True)
            
            # Get last available date from existing data
            last_date = self.get_last_available_date()
            
            if last_date is not None:
                # Filter data newer than last available date
                combined_df['dt_referencia'] = pd.to_datetime(combined_df['dt_referencia'])
                combined_df = combined_df[combined_df['dt_referencia'].dt.date > last_date]
            
            if combined_df.empty:
                logger.info("No new data to add")
                return True
            
            # Save the data
            success = self.append_data(combined_df)
            
            if success:
                logger.info(f"Successfully processed {len(combined_df)} new records")
            else:
                logger.error("Failed to save processed data")
            
            return success
            
        except Exception as e:
            logger.error(f"Error processing downloaded files: {e}")
            return False

    def _process_idka_file(self, file_path: Path) -> Optional[pd.DataFrame]:
        """Process a single IDKA file.

        Args:
            file_path: Path to the file

        Returns:
            Processed DataFrame or None if failed
        """
        try:
            # Read file and check header
            with open(file_path, 'r', encoding='latin1') as f:
                first_line = f.readline().strip()
                
                if 'Data de Referência:' not in first_line:
                    logger.warning(f"Invalid file format: {file_path}")
                    return None
                
                # Extract reference date
                date_part = first_line.split(' ')[-1].strip()
                reference_date = parse_anbima_date(date_part)
            
            # Read CSV data
            df = pd.read_csv(
                file_path,
                sep=';',
                skiprows=2,
                encoding='latin1',
                header=0,
                skipfooter=3,
                engine='python'
            )
            
            if df.empty:
                logger.warning(f"Empty data in file: {file_path}")
                return None
            
            # Add reference date
            df['dt_referencia'] = reference_date
            
            # Rename columns to match expected format
            column_mapping = {
                'Indexador': 'no_indexador',
                'Índices': 'no_indice',
                'Nº Índice': 'nu_indice',
                'Retorno (% Dia)': 'ret_dia_perc',
                'Retorno (% Mês)': 'ret_mes_perc',
                'Retorno (% Ano)': 'ret_ano_perc',
                'Retorno (% 12 Meses)': 'ret_12_meses_perc',
                'Volatilidade (% a.a.) *': 'vol_aa_perc',
                'Taxa de Juros (% a.a.) [Compra (D-1)]': 'taxa_juros_aa_perc_compra_d1',
                'Taxa de Juros (% a.a.) [Venda (D-0)]': 'taxa_juros_aa_perc_venda_d0'
            }
            
            # Rename columns that exist
            existing_columns = {k: v for k, v in column_mapping.items() if k in df.columns}
            df = df.rename(columns=existing_columns)
            
            # Select only the columns we need
            expected_columns = [
                'dt_referencia',
                'no_indexador',
                'no_indice',
                'nu_indice',
                'ret_dia_perc',
                'ret_mes_perc',
                'ret_ano_perc',
                'ret_12_meses_perc',
                'vol_aa_perc',
                'taxa_juros_aa_perc_compra_d1',
                'taxa_juros_aa_perc_venda_d0'
            ]
            
            # Add missing columns with None values
            for col in expected_columns:
                if col not in df.columns:
                    df[col] = None
            
            # Select and reorder columns
            df = df[expected_columns]
            
            logger.info(f"Processed {len(df)} records from {file_path}")
            return df
            
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")
            return None 