"""Configuration management from environment variables"""
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()


class Config:
    """Bot configuration from environment variables"""

    # Polymarket Authentication
    PRIVATE_KEY = os.getenv("PK", "")
    WALLET_ADDRESS = os.getenv("BROWSER_ADDRESS", "")

    # Google Sheets
    SPREADSHEET_URL = os.getenv("SPREADSHEET_URL", "")
    GOOGLE_CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE", "service-account.json")

    # Bot settings
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    # Risk management
    MAX_POSITION_SIZE = float(os.getenv("MAX_POSITION_SIZE", "1000"))
    MAX_TOTAL_EXPOSURE = float(os.getenv("MAX_TOTAL_EXPOSURE", "5000"))
    MIN_MERGE_SIZE = float(os.getenv("MIN_MERGE_SIZE", "1.0"))

    # Network
    POLYMARKET_API_URL = os.getenv("POLYMARKET_API_URL", "https://clob.polymarket.com")
    WEBSOCKET_URL = os.getenv(
        "WEBSOCKET_URL", "wss://ws-subscriptions-clob.polymarket.com/ws"
    )
    CHAIN_ID = int(os.getenv("CHAIN_ID", "137"))

    @classmethod
    def validate(cls):
        """Validate required configuration"""
        errors = []

        if not cls.PRIVATE_KEY:
            errors.append("PK (private key) is required")

        if not cls.WALLET_ADDRESS:
            errors.append("BROWSER_ADDRESS (wallet address) is required")

        if not cls.SPREADSHEET_URL:
            errors.append("SPREADSHEET_URL is required")

        if not Path(cls.GOOGLE_CREDENTIALS_FILE).exists():
            errors.append(f"Google credentials file not found: {cls.GOOGLE_CREDENTIALS_FILE}")

        if errors:
            raise ValueError("Configuration errors:\n" + "\n".join(f"  - {e}" for e in errors))

        return True


# Create a singleton config instance
config = Config()