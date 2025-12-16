from ssi_fc_data import fc_md_client, model
from src.api.utils.dataAPI import data_config
from datetime import datetime, timedelta
from logger_config import get_logger
from zoneinfo import ZoneInfo
import logging


logger = get_logger(__name__, level = logging.INFO)

client = fc_md_client.MarketDataClient(data_config)
def access_token():
    print(client.access_token(model.accessToken(data_config.consumerID, data_config.consumerSecret)))

def get_intradate_data():
    print(client.intraday_ohlc(data_config, model.intraday_ohlc('VN30F1M', '21/11/2025', '21/11/2025', 1, 100, True, 1)))

def get_current_price(symbol: str = 'VN30F1M') -> float:
    currentDate = datetime.now(ZoneInfo('Asia/Ho_Chi_Minh')).strftime('%d/%m/%Y')
    response = client.intraday_ohlc(data_config, model.intraday_ohlc(symbol, currentDate, currentDate))
    if response["data"]:
        latest_record = max(response["data"], key=lambda x: x["Time"])
        currentPrice = latest_record["Value"]
        logger.info(f"Current price: {currentPrice}")
    else:
        latest_record = None
        logger.warning(f"No {symbol} data available for the current date {currentDate}.")

def get_current_Opening_price(symbol: str = 'VN30F1M') -> float:
    currentDate = datetime.now(ZoneInfo('Asia/Ho_Chi_Minh')).strftime('%d/%m/%Y')
    response = client.intraday_ohlc(data_config, model.intraday_ohlc(symbol, currentDate, currentDate))
    if response["data"]:
        latest_record = max(response["data"], key=lambda x: x["Time"])
        currentPrice = latest_record["Open"]
        logger.info(f"Stick's current Opening price: {currentPrice}")
    else:
        latest_record = None
        logger.warning(f"No {symbol} data available for the current date {currentDate}.")

def get_current_High_price(symbol: str = 'VN30F1M') -> float:
    currentDate = datetime.now(ZoneInfo('Asia/Ho_Chi_Minh')).strftime('%d/%m/%Y')
    response = client.intraday_ohlc(data_config, model.intraday_ohlc(symbol, currentDate, currentDate))
    if response["data"]:
        latest_record = max(response["data"], key=lambda x: x["Time"])
        currentPrice = latest_record["High"]
        logger.info(f"Stick's current High price: {currentPrice}")
    else:
        latest_record = None
        logger.warning(f"No {symbol} data available for the current date {currentDate}.")
        
def get_current_Low_price(symbol: str = 'VN30F1M') -> float:
    currentDate = datetime.now(ZoneInfo('Asia/Ho_Chi_Minh')).strftime('%d/%m/%Y')
    response = client.intraday_ohlc(data_config, model.intraday_ohlc(symbol, currentDate, currentDate))
    if response["data"]:
        latest_record = max(response["data"], key=lambda x: x["Time"])
        currentPrice = latest_record["Low"]
        logger.info(f"Stick's current Low price: {currentPrice}")
    else:
        latest_record = None
        logger.warning(f"No {symbol} data available for the current date {currentDate}.")
        
def get_current_closing_price(symbol: str = 'VN30F1M') -> float:
    currentDate = datetime.now(ZoneInfo('Asia/Ho_Chi_Minh')).strftime('%d/%m/%Y')
    response = client.intraday_ohlc(data_config, model.intraday_ohlc(symbol, currentDate, currentDate))
    if response["data"]:
        latest_record = max(response["data"], key=lambda x: x["Time"])
        currentPrice = latest_record["Close"]
        logger.info(f"Stick's current closing price: {currentPrice}")
    else:
        latest_record = None
        logger.warning(f"No {symbol} data available for the current date {currentDate}.")
        
def get_celling_price(symbol: str = 'VN30F1M') -> float:
    yesterday = (datetime.now(ZoneInfo('Asia/Ho_Chi_Minh')) - timedelta(days=1)).strftime('%d/%m/%Y')
    response = client.intraday_ohlc(data_config, model.intraday_ohlc(symbol, yesterday, yesterday))
    if response["data"]:
        latest_record = max(response["data"], key=lambda x: x["TradingDate"])
        cellingPrice = latest_record["CeilingPrice"]
        logger.info(f"Ceiling price: {cellingPrice}")
    else:
        latest_record = None
        logger.warning(f"No {symbol} data available for the current date {cellingPrice}.")
    
def get_floor_price(symbol: str = 'VN30F1M') -> float:
    yesterday = (datetime.now(ZoneInfo('Asia/Ho_Chi_Minh')) - timedelta(days=1)).strftime('%d/%m/%Y')
    response = client.intraday_ohlc(data_config, model.intraday_ohlc(symbol, yesterday, yesterday))
    if response["data"]:
        latest_record = max(response["data"], key=lambda x: x["TradingDate"])
        floorPrice = latest_record["FloorPrice"]
        logger.info(f"Floor price: {floorPrice}")
    else:
        latest_record = None
        logger.warning(f"No {symbol} data available for the current date {floorPrice}.")

def main():
    implement = True
    while implement:
        print('\n-----------------------')
        print('          MENU           ')
        print('-----------------------')
        print('01  - Get intraday data.')
        print('02  - Get current price.')
        print('03  - Get current opening price.')
        print('04  - Get current high price.')
        print('05  - Get current low price.')
        print('06  - Get current closing price.')
        print('07  - Get celling price.')
        print('08  - Get floor price.')
        print('00  - Exist.\n')
        value = input('Enter your choice: ')

        if value == '01':
            get_intradate_data()
        if value == '02':
            get_current_price()
        if value == '03':
            get_current_Opening_price()
        if value == '04':
            get_current_High_price()
        if value == '05':
            get_current_closing_price()
        if value == '06':
            get_current_price()
        if value == '06':
            get_celling_price()
        if value == '06':
            get_floor_price()
        if value == '00':
            implement = False
            print('\n-------------Exist-------------\n')

if __name__ == '__main__':
    main()