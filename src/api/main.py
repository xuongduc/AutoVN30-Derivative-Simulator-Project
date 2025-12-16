from logger_config import get_logger
from src.api.utils.dataAPI import get_data as data_api
from src.api.utils.tradingAPI import orders as orders
import logging


logger = get_logger(__name__, level = logging.INFO)


def place_lo_order(instrumentIDValue, buySellValue, priceValue, quantityValue):
    orders.new_lo_order(
        instrumentID = instrumentIDValue,
        buySell = buySellValue,
        price = priceValue,
        quantity = quantityValue
    )

def place_lo_order_at_current_price(instrumentIDValue, buySellValue, quantityValue):
    currentPrice = data_api.get_current_price(instrumentIDValue)
    orders.new_lo_order(
        instrumentID = instrumentIDValue,
        buySell = buySellValue,
        price = currentPrice,
        quantity = quantityValue
    )

def place_lo_order_at_celling_price(instrumentIDValue, buySellValue, quantityValue):
    cellingPrice = data_api.get_celling_price(instrumentIDValue)
    orders.new_lo_order(
        instrumentID = instrumentIDValue,
        buySell = buySellValue,
        price = cellingPrice,
        quantity = quantityValue
    )

def place_lo_order_at_floor_price(instrumentIDValue, buySellValue, quantityValue):
    floorPrice = data_api.get_floor_price(instrumentIDValue)
    orders.new_lo_order(
        instrumentID = instrumentIDValue,
        buySell = buySellValue,
        price = floorPrice,
        quantity = quantityValue
    )

def main():
    logger.info("------ RUNNER ------")
    implement = True
    instrumentIDValue = 'VN30F2512'
    buyValue = 'B'
    sellValue = 'S'
    priceValue: float = 2044.7
    quantityValue: int = 1

    while implement:
        print('\n-----------------------')
        print('          MENU           ')
        print('-----------------------')
        print('01  - Place a new LO order.')
        # print('02  - Place a new LO order at current price.') 
        # print('03  - Place a new LO order at celling price.')
        # print('04  - Place a new LO order at floor price.')
        print('00  - Exist.\n')
        value = input('Enter your choice: ')

        match value:
            case '01':
                return place_lo_order(instrumentIDValue, sellValue, priceValue, quantityValue)
            # case '02':
            #     return place_lo_order_at_current_price(instrumentIDValue, sellValue, quantityValue)
            # case '03':
            #     return place_lo_order_at_celling_price(instrumentIDValue, sellValue, quantityValue)
            # case '04':
            #     return place_lo_order_at_floor_price(instrumentIDValue, buyValue, quantityValue)
            # case '05':
            #     return "..."
            case _:
                logger.warning("Invalid choice or Exist.")
                implement = False
                return 

if __name__ == '__main__':
    main()