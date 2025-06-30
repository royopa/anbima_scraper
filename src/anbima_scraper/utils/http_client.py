"""HTTP client utilities for ANBIMA scraper."""

import logging
import random
from pathlib import Path
from typing import Dict, Optional, Union

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from ..config.settings import REQUEST_SETTINGS, USER_AGENTS_FILE

logger = logging.getLogger(__name__)


class ANBIMAHTTPClient:
    """HTTP client with retry logic and user agent rotation for ANBIMA requests."""

    def __init__(self, timeout: int = 30, max_retries: int = 3):
        """Initialize the HTTP client.

        Args:
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries
        """
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = self._create_session()
        self.user_agents = self._load_user_agents()

    def _create_session(self) -> requests.Session:
        """Create a requests session with retry strategy."""
        session = requests.Session()
        
        retry_strategy = Retry(
            total=self.max_retries,
            status_forcelist=[429, 500, 502, 503, 504],
            method_whitelist=["HEAD", "GET", "OPTIONS"],
            backoff_factor=REQUEST_SETTINGS["retry_delay"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session

    def _load_user_agents(self) -> list[str]:
        """Load user agents from file."""
        if not USER_AGENTS_FILE.exists():
            logger.warning(f"User agents file not found: {USER_AGENTS_FILE}")
            return [REQUEST_SETTINGS["headers"]["User-Agent"]]
        
        try:
            with open(USER_AGENTS_FILE, 'r', encoding='utf-8') as f:
                user_agents = [line.strip() for line in f if line.strip()]
            return user_agents
        except Exception as e:
            logger.error(f"Error loading user agents: {e}")
            return [REQUEST_SETTINGS["headers"]["User-Agent"]]

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with random user agent."""
        headers = REQUEST_SETTINGS["headers"].copy()
        headers["User-Agent"] = random.choice(self.user_agents)
        return headers

    def get(
        self, 
        url: str, 
        params: Optional[Dict] = None,
        stream: bool = False
    ) -> requests.Response:
        """Make a GET request with retry logic.

        Args:
            url: Target URL
            params: Query parameters
            stream: Whether to stream the response

        Returns:
            Response object

        Raises:
            requests.RequestException: If request fails after retries
        """
        headers = self._get_headers()
        
        logger.debug(f"Making GET request to: {url}")
        
        try:
            response = self.session.get(
                url,
                params=params,
                headers=headers,
                timeout=self.timeout,
                stream=stream
            )
            response.raise_for_status()
            logger.debug(f"Request successful: {response.status_code}")
            return response
        except requests.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise

    def download_file(
        self, 
        url: str, 
        file_path: Union[str, Path], 
        params: Optional[Dict] = None
    ) -> bool:
        """Download a file from URL.

        Args:
            url: Source URL
            file_path: Destination file path
            params: Query parameters

        Returns:
            True if download successful, False otherwise
        """
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            response = self.get(url, params=params, stream=True)
            
            total_size = int(response.headers.get('content-length', 0))
            
            with open(file_path, 'wb') as f:
                if total_size == 0:
                    f.write(response.content)
                else:
                    downloaded = 0
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            logger.debug(
                                f"Downloaded: {downloaded}/{total_size} bytes"
                            )
            
            logger.info(f"File downloaded successfully: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Download failed: {e}")
            if file_path.exists():
                file_path.unlink()
            return False

    def close(self):
        """Close the session."""
        self.session.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close() 