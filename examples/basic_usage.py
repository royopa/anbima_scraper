#!/usr/bin/env python3
"""
Exemplo básico de uso do ANBIMA Scraper.

Este script demonstra como usar o scraper para capturar dados da ANBIMA.
"""

import logging
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from anbima_scraper import ANBIMAScraper
from anbima_scraper.config.settings import LOGGING_CONFIG

# Configure logging
logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)


def main():
    """Exemplo de uso básico."""
    print("=== ANBIMA Scraper - Exemplo Básico ===\n")
    
    # Criar instância do scraper
    scraper = ANBIMAScraper()
    
    # Listar scrapers disponíveis
    print("Scrapers disponíveis:")
    scrapers = scraper.get_available_scrapers()
    for name in scrapers:
        print(f"  - {name}")
    print()
    
    # Verificar status atual
    print("Status atual:")
    status = scraper.get_scraper_status()
    for name, last_date in status.items():
        date_str = last_date.strftime("%Y-%m-%d") if last_date else "Sem dados"
        print(f"  {name}: {date_str}")
    print()
    
    # Executar apenas o scraper de indicadores
    print("Executando scraper de indicadores...")
    success = scraper.run_scraper("indicators")
    
    if success:
        print("✓ Indicadores atualizados com sucesso!")
    else:
        print("✗ Falha ao atualizar indicadores")
    
    print()
    
    # Executar scraper IDKA
    print("Executando scraper IDKA...")
    success = scraper.run_scraper("idka")
    
    if success:
        print("✓ IDKA atualizado com sucesso!")
    else:
        print("✗ Falha ao atualizar IDKA")
    
    print()
    
    # Verificar status após atualizações
    print("Status após atualizações:")
    status = scraper.get_scraper_status()
    for name, last_date in status.items():
        date_str = last_date.strftime("%Y-%m-%d") if last_date else "Sem dados"
        print(f"  {name}: {date_str}")
    
    print("\n=== Exemplo concluído ===")


if __name__ == "__main__":
    main() 