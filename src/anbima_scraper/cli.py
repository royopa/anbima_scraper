"""Command line interface for ANBIMA scraper."""

import argparse
import logging
import sys
from typing import List

from .core.anbima_scraper import ANBIMAScraper
from .config.settings import LOGGING_CONFIG

# Configure logging
logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="ANBIMA Scraper - Captura dados financeiros da ANBIMA",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  # Executar todos os scrapers
  python -m anbima_scraper run-all

  # Executar apenas indicadores
  python -m anbima_scraper run indicators

  # Executar múltiplos scrapers
  python -m anbima_scraper run indicators idka

  # Forçar atualização
  python -m anbima_scraper run-all --force

  # Verificar status
  python -m anbima_scraper status

  # Listar scrapers disponíveis
  python -m anbima_scraper list
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Comandos disponíveis')
    
    # Run all command
    run_all_parser = subparsers.add_parser(
        'run-all', 
        help='Executar todos os scrapers'
    )
    run_all_parser.add_argument(
        '--force', 
        action='store_true',
        help='Forçar atualização mesmo se dados existirem'
    )
    
    # Run specific command
    run_parser = subparsers.add_parser(
        'run', 
        help='Executar scrapers específicos'
    )
    run_parser.add_argument(
        'scrapers',
        nargs='+',
        help='Nomes dos scrapers para executar'
    )
    run_parser.add_argument(
        '--force', 
        action='store_true',
        help='Forçar atualização mesmo se dados existirem'
    )
    
    # Status command
    subparsers.add_parser(
        'status', 
        help='Verificar status dos scrapers'
    )
    
    # List command
    subparsers.add_parser(
        'list', 
        help='Listar scrapers disponíveis'
    )
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        scraper = ANBIMAScraper()
        
        if args.command == 'run-all':
            return _run_all(scraper, args.force)
        elif args.command == 'run':
            return _run_specific(scraper, args.scrapers, args.force)
        elif args.command == 'status':
            return _show_status(scraper)
        elif args.command == 'list':
            return _list_scrapers(scraper)
        else:
            logger.error(f"Comando desconhecido: {args.command}")
            return 1
            
    except KeyboardInterrupt:
        logger.info("Operação cancelada pelo usuário")
        return 1
    except Exception as e:
        logger.error(f"Erro inesperado: {e}")
        return 1


def _run_all(scraper: ANBIMAScraper, force: bool) -> int:
    """Run all scrapers.

    Args:
        scraper: ANBIMA scraper instance
        force: Force update flag

    Returns:
        Exit code
    """
    logger.info("Executando todos os scrapers...")
    
    results = scraper.run_all(force_update=force)
    
    # Print results
    print("\nResultados:")
    print("-" * 50)
    
    successful = 0
    for name, success in results.items():
        status = "✓" if success else "✗"
        print(f"{status} {name}")
        if success:
            successful += 1
    
    print("-" * 50)
    print(f"Total: {successful}/{len(results)} bem-sucedidos")
    
    return 0 if successful == len(results) else 1


def _run_specific(scraper: ANBIMAScraper, 
                 scraper_names: List[str], 
                 force: bool) -> int:
    """Run specific scrapers.

    Args:
        scraper: ANBIMA scraper instance
        scraper_names: List of scraper names
        force: Force update flag

    Returns:
        Exit code
    """
    logger.info(f"Executando scrapers: {', '.join(scraper_names)}")
    
    results = scraper.run_multiple(scraper_names, force_update=force)
    
    # Print results
    print("\nResultados:")
    print("-" * 50)
    
    successful = 0
    for name, success in results.items():
        status = "✓" if success else "✗"
        print(f"{status} {name}")
        if success:
            successful += 1
    
    print("-" * 50)
    print(f"Total: {successful}/{len(results)} bem-sucedidos")
    
    return 0 if successful == len(results) else 1


def _show_status(scraper: ANBIMAScraper) -> int:
    """Show scraper status.

    Args:
        scraper: ANBIMA scraper instance

    Returns:
        Exit code
    """
    logger.info("Verificando status dos scrapers...")
    
    status = scraper.get_scraper_status()
    
    print("\nStatus dos Scrapers:")
    print("-" * 60)
    print(f"{'Scraper':<25} {'Última Data':<20} {'Status'}")
    print("-" * 60)
    
    for name, last_date in status.items():
        if last_date is None:
            status_text = "Sem dados"
        else:
            status_text = "Atualizado"
        
        date_str = last_date.strftime("%Y-%m-%d") if last_date else "N/A"
        print(f"{name:<25} {date_str:<20} {status_text}")
    
    print("-" * 60)
    
    return 0


def _list_scrapers(scraper: ANBIMAScraper) -> int:
    """List available scrapers.

    Args:
        scraper: ANBIMA scraper instance

    Returns:
        Exit code
    """
    scrapers = scraper.get_available_scrapers()
    
    print("\nScrapers Disponíveis:")
    print("-" * 30)
    
    for name in scrapers:
        print(f"• {name}")
    
    print("-" * 30)
    print(f"Total: {len(scrapers)} scrapers")
    
    return 0


if __name__ == '__main__':
    sys.exit(main()) 