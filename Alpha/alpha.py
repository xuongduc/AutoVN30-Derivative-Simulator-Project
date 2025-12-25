import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

class MaAlpha:
    def __init__(self, ma_window=20, slope_points=5, tf="5min", loss_range=-5, exit_eps=0.5, transaction_fee=0.4):
        self.ma_window = ma_window
        self.slope_points = slope_points
        self.tf = tf
        self.loss_range = loss_range
        self.exit_eps: float = exit_eps
        self.transaction_fee: float = transaction_fee
        self.df_1min: pd.DataFrame = None
        self.df_5min: pd.DataFrame = None
        self.processed_data = {}

    def process_data(self, file_path: str) -> pd.DataFrame:
        USE_COLS = [
            'crawled_time',
            'time_stamp',
            'gia_khop'
        ]

        df = pd.read_csv(
            file_path,
            usecols=USE_COLS,
            dtype={
                'crawled_time': 'string',
                'time_stamp': 'string'
            }
        )
        df['time_stamp'] = pd.to_datetime(
            df['crawled_time'] + ' ' + df['time_stamp'],
            format='%Y-%m-%d %H:%M:%S.%f',
            errors='coerce'
        )
        df = df.dropna(subset=['time_stamp'])
        df = df.drop(columns='crawled_time').set_index('time_stamp')

        self.df_1min = df['gia_khop'].resample('1min').ohlc().dropna()
        self.df_5min = df['gia_khop'].resample('5min').ohlc().dropna()

        self.df_1min = self.add_ma_features(self.df_1min)
        self.df_5min = self.add_ma_features(self.df_5min)

        self.df_1min.to_csv("data/processed/41I1FB000_1min.csv")
        self.df_5min.to_csv("data/processed/41I1FB000_5min.csv")

        return self.df_1min, self.df_5min
    
    
    def ma_alpha(
        self,
        df_chunk: pd.DataFrame,
        last_alpha: int,
        *,
        V1: float,
        V2: float,
        M1: float,
        M2: float
    ) -> int:
        if df_chunk is None or df_chunk.empty:
            return 0

        required = ("close", "ma20", "slope_ma20", "diff", "diff_delta")
        for c in required:
            if c not in df_chunk.columns:
                return 0

        # Use the latest available row (time t)
        last = df_chunk.iloc[-1]

        ma20 = last["ma20"]
        slope_ma20 = last["slope_ma20"]
        diff_now = last["diff"]
        diff_delta = last["diff_delta"]
        close_price = last["close"]

        # If indicators are not ready yet (NaN at the beginning), do nothing
        if pd.isna(ma20) or pd.isna(slope_ma20) or pd.isna(diff_now) or pd.isna(diff_delta):
            return 0

        slope_ma20 = float(slope_ma20)
        diff_now = float(diff_now)
        diff_delta = float(diff_delta)

        # Trend regime
        uptrend_cod1 = (slope_ma20 > M2)
        uptrend_cod2 = (slope_ma20 < 0.5 * (M1 + M2))
        uptrend_cod3 = (close_price > ma20)
        uptrend_cod4 = (diff_delta > 0)
        uptrend = uptrend_cod1 and uptrend_cod2 and uptrend_cod3 and uptrend_cod4 # The slope-MA20 value is located in the lower half of the range from M1 to M2.

        downtrend_cod1 = (slope_ma20 < M1)
        downtrend_cod2 = (slope_ma20 > 0.5 * (M1 + M2))
        downtrend_cod3 = (close_price < ma20)
        downtrend_cod4 = (diff_delta < 0)
        downtrend = downtrend_cod1 and downtrend_cod2 and downtrend_cod3 and downtrend_cod4 # The slope-MA20 value is located in the upper half of the range from M1 to M2.

        # Exit rules
        exit_long_cod1 = self.near(diff_now, V1) or (diff_now > V1)
        exit_long_cod2 = self.near(slope_ma20, M1) or (slope_ma20 > M1)
        exit_long_cod3 = (diff_now > 0.5 * (V1 + V2)) and (slope_ma20 > M1)
        exit_long = exit_long_cod1 or exit_long_cod2 or exit_long_cod3

        exit_short_cod1 = self.near(diff_now, V2) or (diff_now < V2)
        exit_short_cod2 = self.near(slope_ma20, M2) or (slope_ma20 < M2)
        exit_short_cod3 = (diff_now < 0.5 * (V1 + V2)) and (slope_ma20 < M1)
        exit_short = exit_short_cod1 or exit_short_cod2 or exit_short_cod3

        # Long entry logic
        if uptrend:
            if exit_long:
                return 0
            if (slope_ma20 > M2) and (slope_ma20 < 0.5 * (M1 + M2)) and last_alpha != -1:
                return 1
            return 0

        # Short entry logic
        if downtrend:
            if exit_short:
                return 0
            if (slope_ma20 < M1) and (slope_ma20 > 0.5 * (M1 + M2)) and last_alpha != 1:
                return -1
            return 0

        return last_alpha


    def run_alpha(
        self,
        ticks: pd.DataFrame,
        *,
        bands: dict,
        loss_range: float = -5.0
    ) -> tuple[np.ndarray, np.ndarray, pd.DatetimeIndex]:
        bar_close = ticks['close']

        signals = []
        prices = []

        last_alpha = 0
        entry_price = 0.0

        # target_time = pd.Timestamp("2023-11-11 10:15:00")
        for t, close in bar_close.items():
            # if t == target_time:
            #     breakpoint()
            chunk = ticks.loc[:t]

            # Ticks of 5-minute bars
            bar_start = t - pd.Timedelta(self.tf)
            bar_ticks = ticks.loc[bar_start:t]

            # Stop-loss check
            if last_alpha != 0 and entry_price is not None:
                if not bar_ticks.empty:
                    check_price = float(bar_ticks['close'].min()) if last_alpha == 1 else float(bar_ticks['close'].max())
                else:
                    check_price = float(close)

                # pnl_points = check_price - entry_price
                pnl_points = (check_price - entry_price) * last_alpha
                if pnl_points < loss_range:
                    current_alpha = 0
                    entry_price = None
                else:
                    current_alpha = None
            else:
                current_alpha = None

            # If not stopped, calculate alpha
            if current_alpha is None:
                current_alpha = self.ma_alpha(chunk, last_alpha, **bands)

                if last_alpha == 0 and current_alpha != 0:
                    entry_price = float(close)
                elif last_alpha != 0 and current_alpha == 0:
                    entry_price = None
            
            signals.append(int(current_alpha))
            prices.append(float(close))
            last_alpha = int(current_alpha)
        
        return np.array(signals), np.array(prices), bar_close.index
    

    def calculate_pnl(self, df_5min, bar_close_index: pd.DatetimeIndex , alpha_signals: np.ndarray, price_history: np.ndarray, transaction_fee: float = 0.4) -> float:
        dfp = pd.DataFrame({"Index": bar_close_index, "close_price": price_history, "position": alpha_signals})
        dfp["prev_position"] = dfp["position"].shift(1).fillna(0)
        dfp["price_diff"] = dfp["close_price"].diff().fillna(0)

        dfp["gross_pnl"] = dfp["price_diff"] * dfp["prev_position"]
        dfp["net_pnl"] = np.where(
            dfp['gross_pnl'] != 0,
            dfp['gross_pnl'] - transaction_fee,
            0.0
        )
        dfp["sum_pnl"] = dfp["net_pnl"].cumsum()

        cols_to_add = [
            "position",
            "prev_position",
            "price_diff",
            "gross_pnl",
            "net_pnl",
            "sum_pnl",
        ]
        df_5min = df_5min.join(
            dfp.set_index("Index")[cols_to_add],
            how="left"
        )
        df_5min.to_csv("data/processed/pnl_details.csv")

        return float(dfp["sum_pnl"].iloc[-1]), df_5min
    

    def plot_ma_charts(self, df: pd.DataFrame, *, bands: dict | None = None, tick_step: int = 3, save_to_file: bool=True, path: str = "data/processed"):
        if df is None or df.empty:
            return

        dfp = df.dropna(subset=["close"]).copy()
        if dfp.empty:
            return

        fig, axes = plt.subplots(4, 1, figsize=(24, 10), sharex=True)

        # x-axis: 0..N-1
        x = np.arange(len(dfp))
        tlabels = dfp.index.strftime("%Y-%m-%d %H:%M")

        # Chart 1: close Price and MA
        axes[0].plot(x, dfp["close"], label="Close Price", color="blue", alpha=0.7)
        axes[0].plot(x, dfp["ma20"], label="MA20", color="orange", linestyle="--", linewidth=1.5)
        axes[0].set_title("Close Price and MA20")
        axes[0].set_ylabel("Price")
        axes[0].legend()
        axes[0].grid(True)

        # Chart 2: Diff
        axes[1].plot(x, dfp["diff"], label="Diff (%)", color="green")
        axes[1].axhline(0, color="black", linestyle="--", linewidth=0.8)
        # ---- Add V1 / V2 lines ----
        if bands is not None:
            V1 = bands.get("V1", None)
            V2 = bands.get("V2", None)
            if V1 is not None:
                axes[1].axhline(V1, linestyle="--", linewidth=1.0, label=f"V1 = {V1:.3f}%")
            if V2 is not None:
                axes[1].axhline(V2, linestyle="--", linewidth=1.0, label=f"V2 = {V2:.3f}%")
        axes[1].set_title("Diff between Close Price and MA20 (%)")
        axes[1].set_ylabel("Diff (%)")
        axes[1].legend()
        axes[1].grid(True)

        # Chart 3: Diff_delta
        axes[2].plot(x, dfp["diff_delta"], label="Diff Delta", color="purple")
        axes[2].axhline(0, color="black", linestyle="--", linewidth=0.8)
        axes[2].set_title("Diff Delta")
        axes[2].legend()
        axes[2].grid(True)

        # Chart 4: Slope of MA20
        axes[3].plot(x, dfp["slope_ma20"], label="Slope of MA20", color="red")
        axes[3].axhline(0, color="black", linestyle="--", linewidth=0.8)
        # ---- Add M1 / M2 lines ----
        if bands is not None:
            M1 = bands.get("M1", None)
            M2 = bands.get("M2", None)
            if M1 is not None:
                axes[3].axhline(M1, linestyle="--", linewidth=1.0, label=f"M1 = {M1:.6f}")
            if M2 is not None:
                axes[3].axhline(M2, linestyle="--", linewidth=1.0, label=f"M2 = {M2:.6f}")
        axes[3].set_title("Slope of MA20")
        axes[3].set_ylabel("Slope")
        axes[3].legend()
        axes[3].grid(True)

        # ---- X ticks: ----
        tick_step = max(1, int(tick_step))
        tick_pos = np.arange(0, len(dfp), tick_step)

        axes[-1].set_xlim(0, len(dfp['close']) - 1)
        axes[-1].set_xticks(tick_pos)
        axes[-1].set_xticklabels(tlabels[tick_pos], rotation=90)

        plt.tight_layout()

        # Store chart as image file:
        if save_to_file:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            folder_dir = os.path.abspath(os.path.join(script_dir, ".."))
            full_output_path = os.path.join(folder_dir, path)
            if not os.path.exists(full_output_path):
                os.makedirs(full_output_path)

            file_path = os.path.join(full_output_path, "ma_alpha_charts.png")
            plt.savefig(file_path)
            print(f"Stored chart image at: {file_path}")

        plt.show()


    
    # ======================================================================
    #                            HELPER FUNCTIONS                          =
    # ======================================================================
    def estimate_bands(
        self,
        df_5min: pd.DataFrame,
        *,
        ma_window: int = 20,
        slope_points: int = 5,
        diff_q_high: float = 0.80,
        diff_q_low: float = 0.20,
        slope_q_high: float = 0.80,
        slope_q_low: float = 0.20,
        winsor: float = 0.05,
    ) -> dict:
        # Calculate 20-period moving average on 5-minute data
        ma20 = df_5min['close'].rolling(ma_window).mean().dropna()

        # Align closing prices with ma20 index (because the MA has NaN at the beginning)
        cls_alighed = df_5min['close'].loc[ma20.index]

        # Calculate the price deviation from MA (in percentage)
        diff = (cls_alighed / ma20 - 1.0) * 100.0

        # Calculate the slope of the MA
        slope = (ma20 - ma20.shift(slope_points - 1)) / float(slope_points)

        # Handling infinity and NaN values
        diff = diff.replace([np.inf, -np.inf], np.nan).dropna()
        slope = slope.replace([np.inf, -np.inf], np.nan).dropna()

        # Find and synchronize shared indexes
        common = diff.index.intersection(slope.index)

        # Synchronize the data with the newly found common index
        diff = diff.loc[common]
        slope = slope.loc[common]

        # Winsorize function: Trimming extraneous values ​​on a Pandas Series
        def wins(s: pd.Series) -> pd.Series:
            if winsor <= 0.0:
                return s
            lo = s.quantile(winsor)
            hi = s.quantile(1.0 - winsor)
            return s.clip(lo, hi)

        diff_w = wins(diff)
        V1 = float(diff_w.quantile(diff_q_high))
        V2 = float(diff_w.quantile(diff_q_low))

        slope_w = wins(slope)
        slope_pos = slope_w[slope_w > 0]
        slope_neg = slope_w[slope_w < 0]

        M1 = float(slope_pos.quantile(slope_q_high)) if len(slope_pos) > 5 else float(slope_w.quantile(slope_q_high))
        M2 = float(slope_neg.quantile(slope_q_low)) if len(slope_neg) > 5 else float(slope_w.quantile(slope_q_low))

        M1 = max(M1, 0.0)
        M2 = min(M2, 0.0)

        return {"V1": V1, "V2": V2, "M1": M1, "M2": M2}
    

    def near(self, x: float, level: float) -> bool:
        tolerance = self.exit_eps if level == 0 else max(1e-9, abs(level) * self.exit_eps)
        return abs(x - level) <= tolerance


    def add_ma_features(self, df: pd.DataFrame) -> pd.DataFrame:
        if df is None or df.empty or "close" not in df.columns:
            return df

        out = df.copy()
        out["ma20"] = out["close"].rolling(self.ma_window).mean()
        out["slope_ma20"] = (out["ma20"] - out["ma20"].shift(self.slope_points - 1)) / float(self.slope_points)
        out["diff"] = (out["close"] / out["ma20"] - 1.0) * 100.0
        out["diff_delta"] = out["diff"].diff()

        return out


# ======================================================================
#                                 TESTING                              =
# ======================================================================
if __name__ == "__main__":
    alpha = MaAlpha(ma_window=20, slope_points=5, tf="5min", loss_range=-5)

    df_1min, df_5min = alpha.process_data("data/new/41I1FB000_1.csv")
    # print("1-minute data:")
    # print(df_1min.head())
    # print("\n5-minute data:")
    # print(df_5min.head())

    bands = alpha.estimate_bands(df_5min)
    # print("Estimated Bands:", bands)

    signals, prices, idx = alpha.run_alpha(df_5min, bands=bands, loss_range=-5.0)
    pnl, pnl_df = alpha.calculate_pnl(df_5min, idx, signals, prices, transaction_fee=0.4)
    print("Total PnL:", pnl)
    print(pnl_df.head(50))

    alpha.plot_ma_charts(pnl_df, bands=bands, tick_step=3, save_to_file=True)