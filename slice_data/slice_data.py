import pandas as pd
import time

class Data:
    def __init__(self, path, tick):
        self.path = path
        self.tick = tick
        self.df = pd.read_csv(path)
        self.time_col = self.df.columns[0]
        self.df[self.time_col] = pd.to_datetime(self.df[self.time_col], format="%H:%M:%S.%f")
        self.tick_groups = self.df.groupby(pd.Grouper(key=self.time_col, freq=self.tick))
        self.group_names =list(self.tick_groups.groups.keys())
    def slice(self, index) -> pd.DataFrame:
        if index < 0 or index >= len(self.group_names):
            print(f"Error: Index {index} is out of bounds. Total ticks: {len(self.group_names)}")
            return pd.DataFrame()
        try:
            name = self.group_names[index]
            return self.tick_groups.get_group(name)
        except KeyError:
            return pd.DataFrame()
        

    def __len__(self) -> int:
        return len(self.group_names)
    
    def get_all(self):
        return self.tick_groups
    
if __name__ == "__main__": 
    path = "/Users/phuongxuongduc/docmunent/nam3/doan/data/251021/41I1FB000.csv"
    freq = "15s"

    #bắt đầu đo thời gian
    start_time = time.perf_counter()

    #khởi tạo data initial, và đã thực hiện slice trong lúc khởi tạo lun
    #syntax: Data(đường dẫn, freqency)
    test = Data(path, freq)



    #index là vị trí cái tick
    index = 10
    print(test.slice(index))
    print(test.slice(index+5))#thử gọi 2 lần để test thời gian

    end_time = time.perf_counter()
    duration = end_time - start_time
    print(f"thời gian chạy {duration}")

    
    

    