import psutil, sys, time, os
import traceback

def clear():
    if os.name == "nt":
        _ = os.system("cls")
    else:
        _ = os.system("clear")

def get_threads_cpu_percent(p, interval=0.1):
   total_percent = p.cpu_percent(interval)
   total_time = sum(p.cpu_times())
   return [('%s ' % (total_percent * ((t.system_time + t.user_time)/total_time))) for t in p.threads()]



proc = psutil.Process(4086143)
f = open("memsum_cpu.txt", "+a")

while True:
    clear()
    try:
        threads = get_threads_cpu_percent(proc)
        threads.sort(reverse=True)
        for line in threads:
            f.write(str(line)+"\n")
            print(line)
        f.write("*"*50 + "\n")
    except:
        traceback.print_exc()
    time.sleep(1)
# 3316103 3343197