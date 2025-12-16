from Alpha.test1 import alpha as alpha1
from Alpha.test2 import alpha as alpha2
from Evaluate.evaluate import path_process, execute_alpha, calculate_pnl


path = path_process("/Users/phuongxuongduc/Documents/GitHub/AutoVN30-Derivative-Simulator-Project/data")[1] + "/41I1FB000.csv"


# Ví dụ: Cắt lỗ 5 điểm
threshold = -5 
tick_size = "15s" # Tuỳ chỉnh


signal, prices = execute_alpha(alpha1, path, threshold, tick_size)

total_profit = calculate_pnl(signal, prices, transaction_fee=0.4)
print(total_profit)


