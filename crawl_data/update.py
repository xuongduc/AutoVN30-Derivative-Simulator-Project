import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import date, datetime
from os import makedirs as create
from os.path import isdir, isfile
from telebot.bot import send

print(datetime.now())
send(f"Đã bắt update tỷ trọng và các danh sách vn30 vào: {datetime.now().time()}")

root = f"/root/cosi/doAn/data/{date.today().strftime('%y%m%d')}"    
if not isdir(f"{root}"):
     create(f"{root}")
 

def get_vietstock_influence(top=30, cat_id=4):
    session = requests.Session()

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.6 Safari/605.1.15",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9,vi;q=0.8",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }

    
    url_home = f"https://finance.vietstock.vn/ket-qua-giao-dich?tab=cp-anh-huong&exchange={cat_id}"
    r = session.get(url_home, headers=headers)
    if r.status_code != 200:
        raise Exception(f"Không thể truy cập trang (status={r.status_code})")

    soup = BeautifulSoup(r.text, "html.parser")
    token_tag = soup.find("input", {"name": "__RequestVerificationToken"})
    if not token_tag:
        raise Exception("Không tìm thấy __RequestVerificationToken trong HTML")

    token = token_tag["value"]

    
    api_url = "https://finance.vietstock.vn/data/TopStockInfluence"
    payload = {
        "fromDate": time.strftime("%Y-%m-%d", time.localtime(time.time() - 30 * 86400)),
        "toDate": time.strftime("%Y-%m-%d"),
        "catID": cat_id,
        "top": top,
        "type": 0,
        "__RequestVerificationToken": token
    }

    headers_api = {
        "Origin": "https://finance.vietstock.vn",
        "Referer": url_home,
        "User-Agent": headers["User-Agent"],
        "X-Requested-With": "XMLHttpRequest"
    }

    res = session.post(api_url, data=payload, headers=headers_api)
    if res.status_code != 200:
        raise Exception(f"Lỗi POST API: {res.status_code}")

    try:
        data = res.json()
        if not isinstance(data, list):
            raise ValueError("Kết quả trả về không phải dạng danh sách JSON")
        return data
    except Exception as e:
        print("JSON không hợp lệ. Nội dung trả về:")
        print(res.text[:500])
        raise e


try:
    temp = get_vietstock_influence(top=30, cat_id=4)
    data = {}

    print(f"Lấy được {len(temp)} mã cổ phiếu:")
    for stock in temp:
        print(f"{stock['StockCode']:<6}  Tỷ trọng: {stock['Weight']}")
        data[ stock["StockCode"]] = stock["Weight"]

    with open(f"{root}/vn30.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print(" Đã lưu vào vn30.json thành công!")

except Exception as e:
    print("Lỗi trong quá trình lấy dữ liệu:", e)