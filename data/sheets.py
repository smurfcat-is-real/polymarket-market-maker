"""Google Sheets integration for configuration management.

Manages reading and updating configuration from Google Sheets:
- Market selection and parameters
- Trading hyperparameters  
- Market database updates
"""

import gspread
import pandas as pd
from typing import Dict, List, Optional
from google.oauth2.service_account import Credentials
from gspread_dataframe import set_with_dataframe, get_as_dataframe
from utils.logger import get_logger
from bot.config import Config

logger = get_logger(__name__)


class GoogleSheetsManager:
    """Manages Google Sheets integration for bot configuration."""
    
    # Required OAuth scopes
    SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    
    # Worksheet names
    WORKSHEET_SELECTED = "Selected Markets"
    WORKSHEET_PARAMS = "Hyperparameters"
    WORKSHEET_ALL_MARKETS = "All Markets"
    
    def __init__(self, config: Config):
        """Initialize Google Sheets manager.
        
        Args:
            config: Bot configuration with credentials path and sheet URL
        """
        self.config = config
        self.client: Optional[gspread.Client] = None
        self.spreadsheet: Optional[gspread.Spreadsheet] = None
        self._connect()
    
    def _connect(self):
        """Establish connection to Google Sheets."""
        try:
            logger.info("Connecting to Google Sheets...")
            
            # Load credentials from service account JSON
            credentials = Credentials.from_service_account_file(
                self.config.google_credentials_path,
                scopes=self.SCOPES
            )
            
            # Authorize the client
            self.client = gspread.authorize(credentials)
            
            # Open the spreadsheet
            self.spreadsheet = self.client.open_by_url(self.config.spreadsheet_url)
            
            logger.success(f"Connected to spreadsheet: {self.spreadsheet.title}")
            
        except FileNotFoundError:
            logger.error(f"Credentials file not found: {self.config.google_credentials_path}")
            raise
        except Exception as e:
            logger.error(f"Failed to connect to Google Sheets: {e}")
            raise
    
    def get_selected_markets(self) -> pd.DataFrame:
        """Get markets selected for trading.
        
        Returns:
            DataFrame with selected market configurations
        """
        try:
            worksheet = self.spreadsheet.worksheet(self.WORKSHEET_SELECTED)
            df = get_as_dataframe(worksheet, evaluate_formulas=True)
            
            # Clean up the dataframe
            df = df.dropna(how='all')  # Remove completely empty rows
            df = df.loc[:, ~df.columns.str.contains('^Unnamed')]  # Remove unnamed columns
            
            logger.info(f"Loaded {len(df)} selected markets")
            return df
            
        except gspread.exceptions.WorksheetNotFound:
            logger.error(f"Worksheet '{self.WORKSHEET_SELECTED}' not found")
            return pd.DataFrame()
        except Exception as e:
            logger.error(f"Error reading selected markets: {e}")
            return pd.DataFrame()
    
    def get_hyperparameters(self) -> Dict[str, Dict]:
        """Get trading hyperparameters by profile.
        
        Returns:
            Dict mapping profile names to their parameters
        """
        try:
            worksheet = self.spreadsheet.worksheet(self.WORKSHEET_PARAMS)
            df = get_as_dataframe(worksheet, evaluate_formulas=True)
            
            # Clean up
            df = df.dropna(how='all')
            df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
            
            # Convert to dict with profile name as key
            params = {}
            for _, row in df.iterrows():
                profile = row.get('profile', row.get('param_type', 'default'))
                params[profile] = row.to_dict()
            
            logger.info(f"Loaded {len(params)} parameter profiles")
            return params
            
        except gspread.exceptions.WorksheetNotFound:
            logger.error(f"Worksheet '{self.WORKSHEET_PARAMS}' not found")
            return {}
        except Exception as e:
            logger.error(f"Error reading hyperparameters: {e}")
            return {}
    
    def get_all_markets(self) -> pd.DataFrame:
        """Get database of all available markets.
        
        Returns:
            DataFrame with all market data
        """
        try:
            worksheet = self.spreadsheet.worksheet(self.WORKSHEET_ALL_MARKETS)
            df = get_as_dataframe(worksheet, evaluate_formulas=True)
            
            df = df.dropna(how='all')
            df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
            
            logger.info(f"Loaded {len(df)} total markets")
            return df
            
        except gspread.exceptions.WorksheetNotFound:
            logger.warning(f"Worksheet '{self.WORKSHEET_ALL_MARKETS}' not found")
            return pd.DataFrame()
        except Exception as e:
            logger.error(f"Error reading all markets: {e}")
            return pd.DataFrame()
    
    def update_all_markets(self, df: pd.DataFrame):
        """Update the all markets worksheet with new data.
        
        Args:
            df: DataFrame containing updated market data
        """
        try:
            worksheet = self.spreadsheet.worksheet(self.WORKSHEET_ALL_MARKETS)
            
            # Clear existing data
            worksheet.clear()
            
            # Write new data
            set_with_dataframe(worksheet, df)
            
            logger.info(f"Updated all markets worksheet with {len(df)} markets")
            
        except Exception as e:
            logger.error(f"Error updating all markets: {e}")
    
    def update_market_stats(self, market_id: str, stats: Dict):
        """Update statistics for a specific market.
        
        Args:
            market_id: Market condition ID
            stats: Dictionary of stats to update (e.g., volatility)
        """
        try:
            worksheet = self.spreadsheet.worksheet(self.WORKSHEET_SELECTED)
            df = get_as_dataframe(worksheet)
            
            # Find the market row
            mask = df['condition_id'] == market_id
            if mask.any():
                # Update stats columns
                for col, value in stats.items():
                    if col in df.columns:
                        df.loc[mask, col] = value
                
                # Write back
                set_with_dataframe(worksheet, df)
                logger.debug(f"Updated stats for market {market_id}")
            else:
                logger.warning(f"Market {market_id} not found in selected markets")
                
        except Exception as e:
            logger.error(f"Error updating market stats: {e}")
    
    def refresh_connection(self):
        """Refresh the Google Sheets connection."""
        try:
            self._connect()
            logger.info("Refreshed Google Sheets connection")
        except Exception as e:
            logger.error(f"Failed to refresh connection: {e}")
    
    def create_template_spreadsheet(self) -> str:
        """Create a new spreadsheet with template structure.
        
        Returns:
            URL of the created spreadsheet
        """
        try:
            # Create new spreadsheet
            spreadsheet = self.client.create("Polymarket Bot Configuration")
            
            # Create worksheets
            # Selected Markets
            ws_selected = spreadsheet.add_worksheet(
                title=self.WORKSHEET_SELECTED,
                rows=100,
                cols=20
            )
            selected_headers = [
                'condition_id', 'token1', 'token2', 'question', 'answer1', 'answer2',
                'enabled', 'param_type', 'neg_risk', 'min_size', 'trade_size', 
                'max_size', 'max_spread', 'tick_size', '3_hour', 'best_bid', 'best_ask'
            ]
            ws_selected.append_row(selected_headers)
            
            # Hyperparameters
            ws_params = spreadsheet.add_worksheet(
                title=self.WORKSHEET_PARAMS,
                rows=50,
                cols=15
            )
            param_headers = [
                'param_type', 'trade_size', 'max_size', 'min_size', 'max_spread',
                'stop_loss_threshold', 'take_profit_threshold', 'volatility_threshold',
                'spread_threshold', 'sleep_period'
            ]
            ws_params.append_row(param_headers)
            
            # Add default parameters
            default_params = [
                'default', 100, 250, 10, 5, -2, 1, 10, 3, 1
            ]
            ws_params.append_row(default_params)
            
            # All Markets
            ws_all = spreadsheet.add_worksheet(
                title=self.WORKSHEET_ALL_MARKETS,
                rows=1000,
                cols=20
            )
            all_headers = [
                'condition_id', 'question', 'token1', 'token2', 'answer1', 'answer2',
                'neg_risk', 'volume', 'liquidity', 'end_date', 'active'
            ]
            ws_all.append_row(all_headers)
            
            # Delete default "Sheet1"
            try:
                default_sheet = spreadsheet.worksheet("Sheet1")
                spreadsheet.del_worksheet(default_sheet)
            except:
                pass
            
            logger.success(f"Created template spreadsheet: {spreadsheet.title}")
            return spreadsheet.url
            
        except Exception as e:
            logger.error(f"Error creating template: {e}")
            raise
