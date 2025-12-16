import os
import pandas as pd
from pathlib import Path 
from Slice_data.slice_data import Data
from Measure import measure



def path_process(path_to_data):
    root_dir = Path(path_to_data)
    folder_list = []

    if not root_dir.exists():
        print(f"Cảnh báo: Đường dẫn '{path_to_data}' không tồn tại.")
        return []
    

    for item in root_dir.iterdir():
        folder_list.append(str(item))

    folder_list.sort()
    return folder_list[1:]


def stop_loss(prev_alpha, prev_p, p, threshold = -5):
    pnl = (p - prev_p)
    if pnl < threshold:
        return 0
    return prev_alpha
    


def execute_alpha(alpha_func, file_path, loss_range, tick,*args, **kargs):

    intradata = Data(file_path, tick)
    
    result = []
    price_history = []
    data_len = len(intradata)
    
    last_alpha = 0.0
    entry_price = 0.0
    
    for i in range(data_len):
        df_chunk = intradata.slice(i)
        
        if df_chunk.empty:
            result.append(last_alpha)
            price_history.append(price_history[-1] if price_history else 0)
            continue

        close_price_chunk = df_chunk['gia_khop'].iloc[-1]
        price_history.append(close_price_chunk)
        
        is_stopped = False
        
        if last_alpha != 0:
            check_price = 0.0
            
            if last_alpha > 0: 
                check_price = df_chunk['gia_khop'].min()
            else: 
                check_price = df_chunk['gia_khop'].max()
            
            sl_result = stop_loss(last_alpha, entry_price, check_price, loss_range)
            
            if sl_result == 0:
                current_alpha = 0
                is_stopped = True
                entry_price = 0.0
        
        if not is_stopped:
            current_alpha = alpha_func(df_chunk, *args, **kargs)
            
            if last_alpha == 0 and current_alpha != 0:
                entry_price = close_price_chunk
            elif last_alpha != 0 and current_alpha == 0:
                entry_price = 0.0

        result.append(current_alpha)
        last_alpha = current_alpha

    return result, price_history


def calculate_pnl(alpha_signals, price_history, transaction_fee=0.4):
    df = pd.DataFrame({
        'close_price': price_history,
        'position': alpha_signals
    })
    
    df['prev_position'] = df['position'].shift(1).fillna(0)
    df['gross_pnl'] = df['close_price'].diff().fillna(0) * df['prev_position']
    
    df['fees'] = df['position'].diff().abs().fillna(0) * transaction_fee
    
    df['net_pnl'] = df['gross_pnl'] - df['fees']
    df['cumulative_pnl'] = df['net_pnl'].cumsum()
    
    return df['cumulative_pnl'].iloc[-1]


