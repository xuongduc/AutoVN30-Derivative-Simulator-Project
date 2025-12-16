import configparser
import os

# READ CONFIG
config = configparser.ConfigParser()
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../../.."))
config.read(os.path.join(project_root, "config.ini"))

ConsumerID     = config.get("DEFAULT", "TradingConsumerID", fallback="")
ConsumerSecret = config.get("DEFAULT", "TradingConsumerSecret", fallback="")
PrivateKey     = config.get("DEFAULT", "TradingPrivateKey", fallback="")
Url            = config.get("DEFAULT", "Url", fallback="https://fc-tradeapi.ssi.com.vn/") 
StreamURL      = config.get("DEFAULT", "StreamURL", fallback="https://fc-tradehub.ssi.com.vn/")
TwoFAType      = int(config.get("DEFAULT", "TwoFAType", fallback="1")) # 0-PIN, 1-OTP
NotifyId       = config.get("DEFAULT", "NotifyId", fallback="-1")
DerivativesAccount       = config.get("DEFAULT", "DerivativesAccount", fallback="R205098")
OTPCode       = config.get("DEFAULT", "OTPCode", fallback="")
