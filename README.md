# AutoVN30-Derivative-Simulator-Project

### Cấu trúc thư mục
```
.
├── crawl_data/     # Lưu ý: phải chạy file update trước khi chạy main.py
│   ├── main.py     # Script chính để bắt đầu quá trình crawl dữ liệu.
│   └── update.py   # Script để cập nhật dữ liệu.         
│
├── slice_data/
│   └── slice_data.py #chứa class Data, có nhiệm vụ xử lí dữ liệu thô, và slice data.
│
├── Telegram_bot/
│   └── bot.py      # Chứa toàn bộ code logic để chạy bot Telegram (gửi tin nhắn).
│
├── Measure/
│   └── measure.py      #chứa hàm để đo thời gian, measure(func, parameter_of_the_func).
│
└── README.md         # File tài liệu bạn đang đọc.
```
---

### ▶️ Cách sử dụng

#### Lưu ý: tất cả đều phải chạy trong thư mục gốc (AutoVN30-Derivative-Simulator-Project)

1. Telegram Bot (Module):
- Cần phải nhập token của con bot do bạn tạo ra, cũng như là chat_id của bạn để có thể chạy bot.
- Bot chỉ có hàm `send(msg)` với msg là nội dung tin nhắn bạn muốn gửi.
- Để sử dụng, thêm câu lệnh vào file python chính: 
    ```python
    from Telegram_bot.bot import send
    ```

2. Crawl Data:
- Trước khi chạy main thì phải chạy update.py bằng lệnh:
    ```bash
    python3 -m crawl_data.update
    ```
- Sau đó, để bắt crawl nhập lệnh:
    ```bash
    python3 -m crawl_data.main
    ```
3. Slice Data (Module):
- Đầu tiên cần tạo obj Data:
    ```python
    name = Data(path, freq)
    ```
    - `path` : là đường dẫn tới initial data.
    - `freq` : là thời gian 1 tick
        - Nếu tick theo giây thì để: vd: "15s".
        - Nếu tick theo phút thì để: vd: "15m".
- Module có các hàm:
    - `slice(index)` :
        - Với index là vị trí của tick.
        - Hàm dùng để lấy toàn bộ data của tick đó. Datatype : pandas.DataFrame.
    - `get_all()` : Trả về toàn bộ các ticks.

4.Measure (Module):
- Chỉ có 1 hàm tên measure.
- Các parameter của hàm:
    - `func`: chứa hàm cần đo thời gian chạy.
    - Các parameter còn lại để chaỵ được hàm func.
    - Vd:
    ```python
        from Measure.measure import measure

        def func1(para1, para2, para3):
            print("something")
        
        def func2(para1):
            for i in range(0, 1000):
                print(1)
        

        measue(func1, 1, 2, 3)  #func1 chứa 3 param

         measue(func1, 1)    #func2 chứa 1 param
    ```

