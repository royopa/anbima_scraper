"""Tests for indicators scraper."""

import pytest
from unittest.mock import Mock, patch
import pandas as pd
from datetime import datetime

from anbima_scraper.scrapers.indicators import IndicatorsScraper


class TestIndicatorsScraper:
    """Test class for IndicatorsScraper."""

    @pytest.fixture
    def scraper(self):
        """Create scraper instance for testing."""
        return IndicatorsScraper()

    def test_init(self, scraper):
        """Test scraper initialization."""
        assert scraper.name == "indicators"
        assert scraper.output_file is not None

    def test_map_indicator_selic(self, scraper):
        """Test SELIC indicator mapping."""
        result = scraper._map_indicator("Taxa SELIC do BC2", "Descrição")
        assert result == "selic"

    def test_map_indicator_cdi(self, scraper):
        """Test CDI indicator mapping."""
        result = scraper._map_indicator("DI-CETIP3", "Descrição")
        assert result == "cdi"

    def test_map_indicator_unknown(self, scraper):
        """Test unknown indicator mapping."""
        result = scraper._map_indicator("Unknown Indicator", "Descrição")
        assert result == "Unknown Indicator"

    def test_extract_reference_date_valid(self, scraper):
        """Test valid reference date extraction."""
        df = pd.DataFrame({
            0: ["Data e Hora da Última Atualização: 15/12/2023 - 10:30"]
        })
        
        result = scraper._extract_reference_date(df)
        expected = datetime(2023, 12, 15)
        
        assert result == expected

    def test_extract_reference_date_invalid(self, scraper):
        """Test invalid reference date extraction."""
        df = pd.DataFrame({
            0: ["Invalid format"]
        })
        
        result = scraper._extract_reference_date(df)
        assert result is None

    def test_should_update_new_data(self, scraper):
        """Test should update with new data."""
        # Mock last available date
        scraper.get_last_available_date = Mock(return_value=None)
        
        new_df = pd.DataFrame({
            'data_referencia': ['2023-12-15']
        })
        
        result = scraper._should_update(new_df)
        assert result is True

    def test_should_update_no_new_data(self, scraper):
        """Test should not update when no new data."""
        from datetime import date
        
        # Mock last available date
        scraper.get_last_available_date = Mock(return_value=date(2023, 12, 15))
        
        new_df = pd.DataFrame({
            'data_referencia': ['2023-12-10']  # Older date
        })
        
        result = scraper._should_update(new_df)
        assert result is False 