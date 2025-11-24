import numpy as np

def alpha(df_chunk, **kwargs):

    if df_chunk.empty or len(df_chunk) < 2:
        return 0.0

    y = df_chunk['gia_khop'].values
    
    x = np.arange(len(y))

    slope = np.polyfit(x, y, 1)[0]

    return np.sign(slope)