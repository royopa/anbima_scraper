"""Indicators scraper for ANBIMA data."""

import logging
from datetime import datetime
from typing import Dict, Optional

import pandas as pd

from ..config.settings import ANBIMA_URLS, INDICATOR_MAPPINGS
from ..core.scraper import BaseScraper

logger = logging.getLogger(__name__)


class IndicatorsScraper(BaseScraper):
    """Scraper for ANBIMA indicators."""

    def __init__(self):
        """Initialize the indicators scraper."""
        super().__init__("indicators")

    def scrape(self, start_date: Optional[datetime] = None, 
               end_date: Optional[datetime] = None) -> bool:
        """Scrape indicators data.

        Args:
            start_date: Start date (not used for indicators)
            end_date: End date (not used for indicators)

        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info("Scraping ANBIMA indicators")
            
            # Get data from ANBIMA website
            df = self._fetch_indicators_data()
            if df is None or df.empty:
                logger.error("Failed to fetch indicators data")
                return False
            
            # Process the data
            processed_df = self._process_indicators_data(df)
            if processed_df is None or processed_df.empty:
                logger.error("Failed to process indicators data")
                return False
            
            # Check if we need to update
            if not self._should_update(processed_df):
                logger.info("Indicators data is up to date")
                return True
            
            # Save the data
            success = self.append_data(processed_df)
            
            if success:
                logger.info("Indicators data updated successfully")
            else:
                logger.error("Failed to save indicators data")
            
            return success
            
        except Exception as e:
            logger.error(f"Error scraping indicators: {e}")
            return False

    def _fetch_indicators_data(self) -> Optional[pd.DataFrame]:
        """Fetch indicators data from ANBIMA website.

        Returns:
            DataFrame with raw indicators data or None if failed
        """
        try:
            url = ANBIMA_URLS["indicators"]
            response = self.http_client.get(url)
            
            # Parse HTML tables
            tables = pd.read_html(
                response.content, 
                thousands='.', 
                decimal=','
            )
            
            if len(tables) < 3:
                logger.error("Expected at least 3 tables, got {len(tables)}")
                return None
            
            # Get the indicators table (usually the 3rd table)
            df = tables[2]
            logger.info(f"Fetched indicators data: {len(df)} rows")
            
            return df
            
        except Exception as e:
            logger.error(f"Error fetching indicators data: {e}")
            return None

    def _process_indicators_data(self, df: pd.DataFrame) -> Optional[pd.DataFrame]:
        """Process raw indicators data.

        Args:
            df: Raw indicators DataFrame

        Returns:
            Processed DataFrame or None if failed
        """
        try:
            if df.empty:
                return None
            
            # Extract reference date from first row
            reference_date = self._extract_reference_date(df)
            if reference_date is None:
                logger.error("Could not extract reference date")
                return None
            
            # Remove header rows and clean data
            df = df.loc[1:].copy()  # Skip first row (header)
            df.dropna(inplace=True)
            
            # Add capture date
            df['data_captura'] = reference_date
            
            # Process description column
            df['descricao'] = df[1].copy(deep=False)
            
            # Process date column
            df[1] = pd.to_datetime(df[1], format="%d/%m/%Y", errors='coerce')
            df[1].fillna(df['data_captura'], inplace=True)
            
            # Map indicators
            df[0] = df.apply(
                lambda x: self._map_indicator(x[0], x['descricao']), 
                axis=1
            )
            
            # Rename columns
            df.rename(columns={
                0: 'indice',
                1: 'data_referencia',
                2: 'valor'
            }, inplace=True)
            
            # Select and reorder columns
            df = df[[
                'data_referencia',
                'data_captura',
                'indice',
                'descricao',
                'valor'
            ]]
            
            logger.info(f"Processed indicators data: {len(df)} rows")
            return df
            
        except Exception as e:
            logger.error(f"Error processing indicators data: {e}")
            return None

    def _extract_reference_date(self, df: pd.DataFrame) -> Optional[datetime]:
        """Extract reference date from DataFrame.

        Args:
            df: Raw DataFrame

        Returns:
            Reference date or None if not found
        """
        try:
            if df.empty:
                return None
            
            first_cell = str(df.head(1).iloc[0][0])
            
            if 'Data e Hora da Última Atualização:' in first_cell:
                date_part = first_cell.split('Data e Hora da Última Atualização: ')[1]
                date_str = date_part.split(' - ')[0]
                return datetime.strptime(date_str, '%d/%m/%Y')
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting reference date: {e}")
            return None

    def _map_indicator(self, value: str, description: str) -> str:
        """Map indicator value to standardized name.

        Args:
            value: Indicator value
            description: Indicator description

        Returns:
            Mapped indicator name
        """
        value_str = str(value)
        desc_str = str(description)
        
        # Check for specific patterns
        if value_str.startswith('Estimativa SELIC'):
            return 'selic_estimativa_anbima'
        elif value_str.startswith('Taxa SELIC do BC2'):
            return 'selic'
        elif value_str.startswith('DI-CETIP3'):
            return 'cdi'
        elif value_str.startswith('IGP-M (') and desc_str.startswith('Número Índice'):
            return 'igpm_numero_indice'
        elif value_str.startswith('IGP-M (') and desc_str.startswith('Var % no mês'):
            return 'igpm_variacao_percentual_mes'
        elif value_str.startswith('IGP-M1') and desc_str.startswith('Projeção'):
            return 'igpm_projecao_anbima'
        elif value_str.startswith('IPCA (') and desc_str.startswith('Número Índice'):
            return 'ipca_numero_indice'
        elif value_str.startswith('IPCA (') and desc_str.startswith('Var % no mês'):
            return 'ipca_variacao_percentual_mes'
        elif value_str.startswith('IPCA1') and desc_str.startswith('Projeção'):
            return 'ipca_projecao_anbima'
        elif value_str.startswith('Dolar Comercial Compra'):
            return 'dolar_comercial_compra'
        elif value_str.startswith('Dolar Comercial Venda'):
            return 'dolar_comercial_venda'
        elif value_str.startswith('Euro Compra'):
            return 'euro_compra'
        elif value_str.startswith('Euro Venda'):
            return 'euro_venda'
        elif value_str.startswith('TR2'):
            return 'tr'
        elif value_str.startswith('TBF2'):
            return 'tbf'
        elif value_str.startswith('FDS4'):
            return 'fds'
        else:
            # Return original value if no mapping found
            logger.warning(f"No mapping found for indicator: {value}")
            return value_str

    def _should_update(self, new_df: pd.DataFrame) -> bool:
        """Check if data should be updated.

        Args:
            new_df: New data DataFrame

        Returns:
            True if should update, False otherwise
        """
        if new_df.empty:
            return False
        
        # Get last available date from existing data
        last_date = self.get_last_available_date()
        if last_date is None:
            # No existing data, should update
            return True
        
        # Get reference date from new data
        new_df_copy = new_df.copy()
        new_df_copy['data_referencia'] = pd.to_datetime(new_df_copy['data_referencia'])
        new_reference_date = new_df_copy['data_referencia'].max().date()
        
        # Update if new data is more recent
        should_update = new_reference_date > last_date
        
        if should_update:
            logger.info(f"New data available: {new_reference_date} > {last_date}")
        else:
            logger.info(f"Data is up to date: {new_reference_date} <= {last_date}")
        
        return should_update 