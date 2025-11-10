import concurrent.futures
import time
 
def cube(x):
    return x**3
 
if __name__ == "__main__":
    with concurrent.futures.ProcessPoolExecutor(3) as executor:
        start_time = time.perf_counter()
        result = list(executor.map(cube, range(1,1000)))
        finish_time = time.perf_counter()
    print(f"Program finished in {finish_time-start_time} seconds")
    print(result)