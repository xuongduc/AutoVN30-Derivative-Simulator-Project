import configparser
import os

# READ CONFIG
config = configparser.ConfigParser()
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../../.."))
config.read(os.path.join(project_root, "config.ini"))

auth_type      = config.get("DEFAULT", "auth_type", fallback="Bearer")
consumerID     = config.get("DEFAULT", "DataConsumerID", fallback="")
consumerSecret = config.get("DEFAULT", "DataConsumerSecret", fallback="")
url            = config.get("DEFAULT", "Url", fallback="https://fc-data.ssi.com.vn/") 
stream_url     = config.get("DEFAULT", "StreamURL", fallback="https://fc-datahub.ssi.com.vn/")
