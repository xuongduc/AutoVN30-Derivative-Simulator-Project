from Alpha.test1 import alpha as alpha1
from Alpha.test2 import alpha as alpha2
from Evaluate.evaluate import path_process, evaluate


path = path_process("/Users/phuongxuongduc/Documents/GitHub/AutoVN30-Derivative-Simulator-Project/data")[1] + "/41I1FB000.csv"


# Ví dụ: Cắt lỗ 5 điểm
threshold = -5 
tick_size = "15s" # Tuỳ chỉnh

# Chạy Alpha Price Slope Full
kq_price = evaluate(alpha1, path, threshold, tick_size)
print(kq_price)

# Chạy Alpha Vol Slope Full
kq_vol = evaluate(alpha2, path, threshold, tick_size)
print(kq_vol)