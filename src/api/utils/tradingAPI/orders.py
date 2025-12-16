from ssi_fctrading import FCTradingClient
from ssi_fctrading.models import fcmodel_requests

import src.api.utils.tradingAPI.trading_config as trading_config
import random
from logger_config import get_logger
from zoneinfo import ZoneInfo
import logging
import json


logger = get_logger(__name__, level = logging.INFO)

client = FCTradingClient(
    trading_config.Url,
    trading_config.ConsumerID,
    trading_config.ConsumerSecret,
    trading_config.PrivateKey,
    trading_config.TwoFAType
)
client.get_access_token()
client.verifyCode(trading_config.OTPCode)
deviceId: str = FCTradingClient.get_deviceid()
userAgent: str = FCTradingClient.get_user_agent()
account: str = trading_config.DerivativesAccount

def new_lo_order(
    instrumentID: str, 
	market: str = 'VNFE',       # VNFE - Phái sinh, VN - Cổ phiếu
	buySell: str = 'B',         # B - Buy, S - Sell
	price: float = 0.0, 
	quantity: int = 1
):
    
    request = fcmodel_requests.NewOrder(
        str(account).upper(),
        str(random.randint(0, 99999999)),
        instrumentID.upper(),
        market.upper(),
        buySell.upper(),
        "LO",
        float(price),
        int(quantity),
        False,   # stopOrder
        0.0,     # stopPrice
        "",      # stopType
        0.0,     # stopStep
        0.0,     # lossStep
        0.0,     # profitStep
        deviceId=str(deviceId),
        userAgent=str(userAgent)
    )
    request_dict = request.__dict__
    logger.info("Request body:\n" + json.dumps(request_dict, indent=2, ensure_ascii=False))

    response = client.new_order(request)
    logger.info(f"New LO order response: \n"+  json.dumps(response, indent=2, ensure_ascii=False))
    # return response

if __name__ == "__main__":
    print(new_lo_order(
        instrumentID = 'VN30F1M',
        buySell = 'S',
        price = 2000.0,
        quantity = 1
    ))