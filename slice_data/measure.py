import time

def measure(func,*args, **kwargs):
    start_time = time.perf_counter()
    func(*args, **kwargs)
    end_time = time.perf_counter()
    duration = end_time - start_time
    print(duration)