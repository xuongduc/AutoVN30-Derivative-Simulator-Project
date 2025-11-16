
import requests
import json
import sys

TOKEN = "mọi người thế token của mng vô" 
CHAT_ID = "thế chat id vô"

telegram_api_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"


def send(msg):
	payload = {
		'chat_id': CHAT_ID,
		'text': msg
	}

	print("Đang gửi ...")

	try:
		response = requests.post(
			telegram_api_url, 
			json=payload, 
			timeout=20
		)

		response_data = response.json()

		if response.status_code == 200 and response_data.get('ok'):
			print(">>> Gửi tin nhắn THÀNH CÔNG!")
		else:
			print(f">>> Gửi tin nhắn THẤT BẠI. Phản hồi từ Telegram:")
			print(json.dumps(response_data, indent=2))

	except requests.exceptions.ReadTimeout:

		print(f"LỖI: ReadTimeout! Không nhận được phản hồi từ Telegram sau 20 giây.")
		print("(Tin nhắn CÓ THỂ đã được gửi đi.)")
		
	except requests.exceptions.ConnectTimeout:
		print(f"LỖI: ConnectTimeout! Không thể kết nối tới server Telegram.")

	except requests.exceptions.RequestException as e:
		# Bắt tất cả các lỗi khác từ thư viện requests
		print(f"LỖI (Requests): {e}")

	except Exception as e:
		print(f"LỖI (Chung): {e}")


if __name__ == "__main__":

    message_arg = sys.argv[1]
    
    print(f"Đang thực thi từ dòng lệnh...")

    send(message_arg)