import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os

class DerivativesAnalyzer:
    def __init__(self, file_path):
        self.file_path = file_path
        self.minute_data = None
        self.output_path = "src/output/data/processed_raw_data/"
        self.processed_data = {} 

    def process_raw_data(self):
        df = pd.read_csv(self.file_path)
        
        df['time'] = pd.to_datetime(df['time_stamp'], format='%H:%M:%S.%f')
        df.set_index('time', inplace=True)
        
        # Resample to 1-minute candles
        self.minute_data = df['gia_khop'].resample('1min').last().dropna()        
        return self.minute_data


    def calculate_metrics(self, timeframe_minutes):
        if self.minute_data is None:
            self.process_raw_data()
            
        tf_str = f'{timeframe_minutes}min'
        
        # 1. Resample data from 1-minute candles to desired timeframe => Caculate MA
        df_min = self.minute_data.to_frame(name='gia_khop')
        df_tf = df_min.resample(tf_str).last()
        df_tf['ma'] = df_min.resample(tf_str).agg({'gia_khop': 'mean'})
        
        # 2. Caculate Slope and Angle of MA
        # Slope = [current MA] - [previous MA]
        df_tf['ma_slope'] = df_tf['ma'].diff()
        
        # Angle = arctan of slope. Convert to degrees.
        df_tf['ma_angle'] = np.degrees(np.arctan(df_tf['ma_slope']))
        
        # 3. Caculate Deviation between gia_khop and MA
        df_tf['deviation'] = df_tf['gia_khop'] - df_tf['ma']

        # 4. Determine signal for the corresponding time points. ["1":"BUY", "0":"Close", "-1":"SELL"]
        df_tf['signal'] = 0
        position = 0

        for i in range(1, len(df_tf)):
            delta_angle = df_tf['ma_angle'].iloc[i] - df_tf['ma_angle'].iloc[i - 1]
            delta_price = df_tf['gia_khop'].iloc[i] - df_tf['gia_khop'].iloc[i - 1]

            # Place order
            if position == 0:
                # BUY
                if delta_angle > 0 and delta_price > 0:
                    df_tf.iloc[i, df_tf.columns.get_loc('signal')] = 1
                    position = 1
                # SELL
                if delta_angle < 0 and delta_price < 0:
                    df_tf.iloc[i, df_tf.columns.get_loc('signal')] = -1
                    position = -1

            # Close order
            elif position == 1:
                if (delta_angle <= 0 or delta_price <= 0):
                    df_tf.iloc[i, df_tf.columns.get_loc('signal')] = 0
                    position = 0
            elif position == -1:
                if (delta_angle >= 0 or delta_price >= 0):
                    df_tf.iloc[i, df_tf.columns.get_loc('signal')] = 0
                    position = 0
        
        self.processed_data[timeframe_minutes] = df_tf
        
        # Store processed data file
        if not os.path.exists(self.output_path):
                os.makedirs(self.output_path)
        df_tf.to_csv( f'{self.output_path}{timeframe_minutes}min.csv')

        return df_tf


    def plot_charts(self, timeframe_minutes, save_to_file=True, output_folder = 'MACharts'):
        if timeframe_minutes not in self.processed_data:
            self.calculate_metrics(timeframe_minutes)
            
        df = self.processed_data[timeframe_minutes]
        
        fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
        
        # Chart 1: Matched Price and MA
        axes[0].plot(df.index, df['gia_khop'], label='Matched Price', color='blue', alpha=0.7)
        axes[0].plot(df.index, df['ma'], label='MA', color='orange', linestyle='--', linewidth=1.5)
        axes[0].set_title(f'Timeframe {timeframe_minutes} minutes: Matched Price vs MA')
        axes[0].set_ylabel('Price')
        axes[0].legend(loc='upper left')
        axes[0].grid(True)
        
        # Chart 2: MA Angles
        axes[1].plot(df.index, df['ma_angle'], label='MA Angles (Degrees)', color='green')
        axes[1].axhline(0, color='black', linewidth=0.8, linestyle='--')
        axes[1].set_title('The Gradient of the MA (Indicating Trend Strength)')
        axes[1].set_ylabel('Degrees')
        axes[1].legend(loc='upper left')
        axes[1].grid(True)
        
        # Chart 3: Deviation
        axes[2].plot(df.index, df['deviation'], label='Deviation (Matched Price - MA)', color='red')
        axes[2].axhline(0, color='black', linewidth=0.8, linestyle='--')
        axes[2].set_title('Price-to-MA Deviation (Mean Reversion)')
        axes[2].set_ylabel('Points')
        axes[2].legend(loc='upper left')
        axes[2].grid(True)

        time_format = mdates.DateFormatter('%H:%M:%S')
        plt.gca().xaxis.set_major_locator(mdates.MinuteLocator(interval=timeframe_minutes))
        plt.gca().xaxis.set_major_formatter(time_format)
        plt.gcf().autofmt_xdate()
        
        plt.xlabel('Time')
        plt.tight_layout()
        plt.xlim(df.index[0], df.index[-1])
        
        # --- STORE CHARTS AS IMAGES ---
        if save_to_file:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            full_output_folder = os.path.join(script_dir, output_folder)
            if not os.path.exists(full_output_folder):
                os.makedirs(full_output_folder)
            
            filename = f'chart_{timeframe_minutes}min.png'
            full_path = os.path.join(full_output_folder, filename)
            
            plt.savefig(full_path, dpi=300)
            print(f"Stored {filename} at: {full_path}")

        plt.show()


if __name__ == "__main__":
    csv_path = "src/data/251103/41I1FB000.csv"
    analyzer = DerivativesAnalyzer(csv_path)

    analyzer.plot_charts(5)
    analyzer.plot_charts(10)
    analyzer.plot_charts(15)
