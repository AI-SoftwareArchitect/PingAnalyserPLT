import re
import matplotlib.pyplot as plt
import threading
from tqdm import tqdm
import time
import subprocess
import argparse

print('''
  _____ _                                  _                     _____  _   _______ 
 |  __ (_)               /\               | |                   |  __ \| | |__   __|
 | |__) | _ __   __ _   /  \   _ __   __ _| |_   _ ___  ___ _ __| |__) | |    | |   
 |  ___/ | '_ \ / _` | / /\ \ | '_ \ / _` | | | | / __|/ _ \ '__|  ___/| |    | |   
 | |   | | | | | (_| |/ ____ \| | | | (_| | | |_| \__ \  __/ |  | |    | |____| |   
 |_|   |_|_| |_|\__, /_/    \_\_| |_|\__,_|_|\__, |___/\___|_|  |_|    |______|_|   
                 __/ |                        __/ |                                 
                |___/                        |___/                                  
				VERSION: 1.0.0
				AUTHOR: AI-SoftwareArchitect on github
''')

# Global değişkenler
ping_times = []
lock = threading.Lock()
finished = False  # Global değişken

def extract_time_from_ping(line):
    """Ping çıktı satırından time değerini çıkarır"""
    match = re.search(r'time=(\d+\.?\d*)', line)
    return float(match.group(1)) if match else None

def ping(url, time_info):
    """Ping atma işlemini gerçekleştirir ve süreleri kaydeder"""
    global ping_times, finished  # Global değişkenleri belirt
    # İlerleme çubuğu için tqdm kullanımı
    for i in tqdm(range(time_info), desc="Ping atılıyor", leave=True):
        # Ping komutunu çalıştır
        result = subprocess.run(['ping', '-c', '1', url], stdout=subprocess.PIPE, text=True)
        for line in result.stdout.split('\n'):
            if 'time=' in line:
                time_value = extract_time_from_ping(line)
                if time_value:
                    with lock:
                        ping_times.append(time_value)
        time.sleep(1)  # Her ping arasında 1 saniye bekle
    finished = True  # Ping işlemi tamamlandığında finished'i güncelle

def plot_cumulative_times():
    """Ping sürelerini işleyip grafiği günceller"""
    plt.ion()  # İnteraktif mod
    fig, ax = plt.subplots(figsize=(10, 6))
    line, = ax.plot([], [], marker='o', linestyle='-', color='skyblue', linewidth=2)
    ax.set_title('Kümülatif Ping Süreleri')
    ax.set_xlabel('Ping Sayısı')
    ax.set_ylabel('Kümülatif Süre (ms)')
    ax.grid(True)

    while not finished:  # finished değişkenini kontrol et
        with lock:
            cumulative_times = [sum(ping_times[:i+1]) for i in range(len(ping_times))]
        
        line.set_xdata(range(1, len(cumulative_times) + 1))
        line.set_ydata(cumulative_times)
        ax.relim()  # Eksen limitlerini yeniden hesapla
        ax.autoscale_view()  # Eksen görünümünü otomatik olarak ayarla
        plt.pause(0.1)  # Grafiği güncellemek için kısa bir süre bekle

    plt.ioff()  # İnteraktif modu kapat
    plt.close(fig)  # Grafiği kapat

parser = argparse.ArgumentParser(description='Ping analyser')
parser.add_argument('-u', type=str, help='url information', required=True)
parser.add_argument('-t', type=int, help='time information', required=True)

args = parser.parse_args()

url = args.u
time_info = args.t

# Thread'leri başlat
ping_thread = threading.Thread(target=ping, args=(url, time_info))
ping_thread.start()

# Grafik güncellemelerini ana thread içinde başlat
plot_cumulative_times()

# Ping thread'inin bitmesini bekle
ping_thread.join()
