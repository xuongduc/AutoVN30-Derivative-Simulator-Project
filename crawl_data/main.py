import ssl
import json
from websocket import WebSocketApp
from datetime import date, datetime
from os import makedirs as create
from os.path import isdir, isfile
import pandas as pd
import time
import sys
from telebot.bot import send


#phải chạy file update.py trước

send(f"Đã bắt đầu crawl vào {datetime.now().time()}")
root = "/root/cosi/doAn"
print(datetime.now().time())


if not isdir(root + "/data"):
    create(root + "/data")

WEBSOCKET_URL = "wss://iboard-pushstream.ssi.com.vn/realtime"
def parseCode():
    with open(f"{root}/data/{date.today().strftime('%y%m%d')}/vn30.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    return list(data.keys()) + ["41I1FA000", "41I1FB000"]



exit_time = [(11, 30), (14,30)]
def off():
    now = datetime.now().time()
    for h, m in exit_time:
        if (now.hour > h) or (now.hour >= h and now.minute >= m):
            return True
    return False
    


def on_open(ws):
    symbols = parseCode()
    #symbols = ["ACB"]
    print("Connected")
    subscribe_msg = {"type": "sub",
                    "topic": "stockRealtimeBySymbolsAndBoards",
                    "variables": {
                    "boardIds": ["MAIN"],
                    "symbols": symbols
                    },
                    "component": "priceTableEquities"
                    }

    ws.send(json.dumps(subscribe_msg))
    print("Sent subscription:", subscribe_msg)

def parse_stock(msg: str):

    def val(i, as_int=False, scale=1.0):
        try:
            return (int(f[i]) if as_int else float(f[i])) / scale
        except (ValueError, TypeError, IndexError):
            return None

    f = msg.split('|')
    if len(f) < 102:
        return None

    ma_ck = f[1][2:]  
    
    # phái sinh
    if ma_ck in ("41I1FA000", "41I1FB000"):
        data = {
            "time_stamp": datetime.now().time(),   

            "ngay_dh": f[62],

            "oi": val(58, as_int=True),
            "tran": val(59),
            "san": val(60),
            "tc": val(61),

            # Ben mua
            "gia_mua3": val(2), "kl_mua3": val(3, as_int=True),
            "gia_mua2": val(4), "kl_mua2": val(5, as_int=True),
            "gia_mua1": val(6), "kl_mua1": val(7, as_int=True),
           
            

            # Khop lenh
            "gia_khop": val(42),
            "kl_khop": val(43, as_int=True),
            "thay_doi": val(52),
            "thay_doi_pct (%)": val(53),

            # Ben ban
            "gia_ban1": val(22), "kl_ban1": val(23, as_int=True),
            "gia_ban2": val(24), "kl_ban2": val(25, as_int=True),
            "gia_ban3": val(26), "kl_ban3": val(27, as_int=True),

            # Thong ke
            "tong_kl": val(54, as_int=True),
            "cao": val(44),
            "thap": val(46),

            # Nuoc ngoai
            "nn_mua": val(48, as_int=True),
            "nn_ban": val(50, as_int=True),

        }
    else:
        data = {
            "time_stamp": datetime.now(),

            # Trần/Sàn/TC
            "tran": val(59, scale=1000),
            "san": val(60, scale=1000),
            "tc": val(61, scale=1000),

            # Ben mua
            "gia_mua3": val(6, scale=1000), "kl_mua3": val(7, as_int=True),
            "gia_mua2": val(4, scale=1000), "kl_mua2": val(5, as_int=True),
            "gia_mua1": val(2, scale=1000), "kl_mua1": val(3, as_int=True),

            # Khop lenh
            "gia_khop": val(42, scale=1000),
            "kl_khop": val(43, as_int=True),
            "thay_doi": val(52, scale=1000),
            "thay_doi_pct (%)": val(53),

            # Ben ban
            "gia_ban1": val(22, scale=1000), "kl_ban1": val(23, as_int=True),
            "gia_ban2": val(24, scale=1000), "kl_ban2": val(25, as_int=True),
            "gia_ban3": val(26, scale=1000), "kl_ban3": val(27, as_int=True),

            # Thong ke
            "tong_kl": val(54, as_int=True),
            "cao": val(44, scale=1000),
            "thap": val(46, scale=1000),

            # Nuoc ngoai
            "nn_mua": val(48, as_int=True),
            "nn_ban": val(50, as_int=True),
            "room": val(65, as_int=True),
        }

    return [ma_ck,data]



count = 0
def save_data(stock: dict, ticker : str):
    global count
    path = f"{root}/data/{date.today().strftime('%y%m%d')}"
    
    if not isdir(f"{path}"):
        create(f"{path}")

    file_path = f"{path}/{ticker}.csv"
    file_exists = isfile(file_path)
    
    data = pd.DataFrame([stock])

    try:
        if file_exists:
            data.to_csv(file_path, mode='a', header=False, index=False)
        else:
            data.to_csv(file_path, mode='w', header=True, index=False)
        if count < 20:
            print(f"saved {ticker} ", end= ", ")
            count+=1
        else: 
            print(f"saved {ticker}")
            count = 0
            
    except Exception as e:
        print(f"\n[ERROR] Không thể lưu file {ticker}: {e}\n")
        send(f"\n[ERROR] Không thể lưu file {ticker}: {e}\n")
def on_message(ws, message):
    if message.startswith("MAIN|S#"):
        stock_data = parse_stock(message)
        if True:
            save_data(stock_data[1], stock_data[0])   
        else:
            print("Raw stock:", message[:200], "...")
    else:
        print(message)
        



def on_error(ws, error):
    print(f"{datetime.now()}: ", end= "")
    print("Error:", error)
    send("Error:", error)

def on_close(ws, code, msg):
    print("Closed:", code, msg)



while True:
    print("reconnect")
    send("reconnect sever")
    try:
        ws = WebSocketApp(
            WEBSOCKET_URL,
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close
        )
        ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
    except Exception as e:
        print(f"[{datetime.now()}] Exception: {e}")