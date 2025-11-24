import numpy as np
import pandas as pd

def alpha(df_chunk, **kwargs):

    if df_chunk.empty or len(df_chunk) < 2:
        return 0.0

    if 'kl_khop' not in df_chunk.columns:
        print("Cảnh báo: Không tìm thấy cột 'kl_khop'")
        return 0.0

    p_open = df_chunk['gia_khop'].iloc[0]
    p_close = df_chunk['gia_khop'].iloc[-1]
    delta_p = p_close - p_open


    y_vol = df_chunk['kl_khop'].values
    x_vol = np.arange(len(y_vol)) 
    

    slope_vol = np.polyfit(x_vol, y_vol, 1)[0]

    result = slope_vol * delta_p
    
    return np.sign(result)