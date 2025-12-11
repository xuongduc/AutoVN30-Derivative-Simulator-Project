import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os

class DerivativesAnalyzer:
    def __init__(self, file_path):
        self.file_path = file_path
        self.minute_data = None
        self.processed_data = {} 

    def process_raw_data(self):
        df = pd.read_csv(self.file_path)
        
        df['time'] = pd.to_datetime(df['time_stamp'], format='%H:%M:%S.%f')
        df.set_index('time', inplace=True)
        
        # Resample về nến 1 phút
        self.minute_data = df['gia_khop'].resample('1min').last().dropna()        
        return self.minute_data


    def calculate_metrics(self, timeframe_minutes):
        if self.minute_data is None:
            self.process_raw_data()
            
        tf_str = f'{timeframe_minutes}min'
        
        # 1. Resample từ dữ liệu 1 phút lên khung thời gian mong muốn => Tính MA
        df_min = self.minute_data.to_frame(name='gia_khop')
        df_tf = df_min.resample(tf_str).last()
        df_tf['ma'] = df_min.resample(tf_str).agg({'gia_khop': 'mean'})
        
        # 2. Tính độ dốc (Slope) và Góc (Angle)
        # Slope = MA hiện tại - MA trước đó (trên mỗi bar)
        df_tf['ma_slope'] = df_tf['ma'].diff()
        
        # Tính góc (Angle) bằng arctan của slope, đổi ra độ.
        df_tf['ma_angle'] = np.degrees(np.arctan(df_tf['ma_slope']))
        
        # 3. Tính độ lệch (Deviation) giữa Giá khớp và MA
        df_tf['deviation'] = df_tf['gia_khop'] - df_tf['ma']
        
        self.processed_data[timeframe_minutes] = df_tf
        print(f'Data set sau khi tính toán: \n{df_tf}')
        return df_tf


    def plot_charts(self, timeframe_minutes, save_to_file=True, output_folder = 'MACharts'):
        if timeframe_minutes not in self.processed_data:
            self.calculate_metrics(timeframe_minutes)
            
        df = self.processed_data[timeframe_minutes]
        
        fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
        
        # Chart 1: Giá và MA
        axes[0].plot(df.index, df['gia_khop'], label='Giá Khớp', color='blue', alpha=0.7)
        axes[0].plot(df.index, df['ma'], label='MA', color='orange', linestyle='--', linewidth=1.5)
        axes[0].set_title(f'Khung {timeframe_minutes} Phút: Giá vs MA')
        axes[0].set_ylabel('Điểm')
        axes[0].legend(loc='upper left')
        axes[0].grid(True)
        
        # Chart 2: Góc của MA
        axes[1].plot(df.index, df['ma_angle'], label='Góc MA (Độ)', color='green')
        axes[1].axhline(0, color='black', linewidth=0.8, linestyle='--')
        axes[1].set_title('Hệ số Góc của MA (Trend Strength)')
        axes[1].set_ylabel('Độ')
        axes[1].legend(loc='upper left')
        axes[1].grid(True)
        
        # Chart 3: Độ lệch (Deviation)
        axes[2].plot(df.index, df['deviation'], label='Độ lệch (Giá - MA)', color='red')
        axes[2].axhline(0, color='black', linewidth=0.8, linestyle='--')
        axes[2].set_title('Độ lệch giữa Giá và MA (Mean Reversion)')
        axes[2].set_ylabel('Điểm')
        axes[2].legend(loc='upper left')
        axes[2].grid(True)

        time_format = mdates.DateFormatter('%H:%M:%S')
        plt.gca().xaxis.set_major_locator(mdates.MinuteLocator(interval=timeframe_minutes))
        plt.gca().xaxis.set_major_formatter(time_format)
        plt.gcf().autofmt_xdate()
        
        plt.xlabel('Thời gian')
        plt.tight_layout()
        plt.xlim(df.index[0], df.index[-1])
        
        # --- LƯU FILE ẢNH ---
        if save_to_file:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            full_output_folder = os.path.join(script_dir, output_folder)
            if not os.path.exists(full_output_folder):
                os.makedirs(full_output_folder)
            
            filename = f'chart_{timeframe_minutes}min.png'
            full_path = os.path.join(full_output_folder, filename)
            
            plt.savefig(full_path, dpi=300)
            print(f"Đã lưu biểu đồ tại: {full_path}")

        plt.show()


if __name__ == "__main__":
    csv_path = "data/251104/41I1FB000.csv"
    analyzer = DerivativesAnalyzer(csv_path)
    analyzer.plot_charts(15)
