"""
Dollar Cost Averaging (DCA) Strategy using Alpaca API
This script automatically invests $100 daily in the S&P 500 ETF (SPY).
"""

import os
import time
import logging
from datetime import datetime, timedelta
import schedule
from dotenv import load_dotenv
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("dca_strategy.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger()

# Load environment variables from .env file
load_dotenv()

# Initialize Alpaca API client
api_key = os.getenv('ALPACA_API_KEY')
api_secret = os.getenv('ALPACA_API_SECRET')
is_paper = os.getenv('IS_PAPER', 'true').lower() == 'true'  # Use paper trading by default

if not api_key or not api_secret:
    logger.error("API keys not found. Please check your .env file.")
    exit(1)

# Initialize Alpaca Trading client
trading_client = TradingClient(api_key, api_secret, paper=is_paper)

# Configuration
SYMBOL = "SPY"  # S&P 500 ETF
DAILY_INVESTMENT = 100.0  # $100 per day


def check_market_hours():
    """Check if the market is open today."""
    clock = trading_client.get_clock()
    
    if not clock.is_open:
        next_open = clock.next_open.strftime('%Y-%m-%d %H:%M:%S')
        logger.info(f"Market is closed. Next market open: {next_open}")
        return False
    
    return True


def get_account_info():
    """Get and log account information."""
    account = trading_client.get_account()
    logger.info(f"Account ID: {account.id}")
    logger.info(f"Cash Balance: ${float(account.cash):.2f}")
    logger.info(f"Portfolio Value: ${float(account.portfolio_value):.2f}")
    
    return float(account.cash)


def place_order():
    """Place a market order for SPY with the daily investment amount."""
    if not check_market_hours():
        logger.info("Skipping order as market is closed.")
        return
    
    cash_balance = get_account_info()
    
    if cash_balance < DAILY_INVESTMENT:
        logger.warning(f"Insufficient funds. Available cash: ${cash_balance:.2f}")
        return
    
    # Create market order
    market_order_data = MarketOrderRequest(
        symbol=SYMBOL,
        notional=DAILY_INVESTMENT,  # Use notional to specify dollar amount
        side=OrderSide.BUY,
        time_in_force=TimeInForce.DAY
    )
    
    try:
        # Submit order
        order = trading_client.submit_order(market_order_data)
        logger.info(f"Order placed successfully - Order ID: {order.id}")
        logger.info(f"Buying ${DAILY_INVESTMENT} of {SYMBOL}")
    except Exception as e:
        logger.error(f"Error placing order: {e}")


def run_dca_strategy():
    """Execute the DCA strategy once."""
    logger.info("Running DCA strategy...")
    try:
        place_order()
        logger.info("DCA execution completed")
    except Exception as e:
        logger.error(f"Error executing DCA strategy: {e}")


def schedule_dca():
    """Schedule the DCA strategy to run daily at market open."""
    # Schedule the job to run every day at 9:35 AM (5 minutes after market open)
    schedule.every().day.at("09:35").do(run_dca_strategy)
    logger.info("DCA strategy scheduled to run daily at 9:35 AM")
    
    # Run immediately when script starts for the first time
    run_dca_strategy()
    
    # Keep the script running
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute


if __name__ == "__main__":
    logger.info("Starting DCA strategy for S&P 500 ($100 daily investment)")
    schedule_dca()