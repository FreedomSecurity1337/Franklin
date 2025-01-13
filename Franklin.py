# Dev : ./Freedom Security
# Disclaimer : you can recode this script but don't sell it!
# recode boleh asal jangan di jual ya kontol noob bangsat
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import random
import sys
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import threading
import signal
import warnings
import os
from urllib3.exceptions import InsecureRequestWarning

warnings.filterwarnings("ignore", category=InsecureRequestWarning)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/114.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Mobile/15E"
]

RESET = "\033[0m"
CYAN = "\033[36m"
GREEN = "\033[32m"
WHITE = "\033[97m"
RED = "\033[31m"

ganteng_lock = threading.Lock()
stop_crawling = False
executor = None

def signal_handler(sig, frame):
    global stop_crawling, executor
    stop_crawling = True
    print(f"{RED}[INFO] stopping crawling{RESET}", flush=True)
    if executor:
        executor.shutdown(wait=True)
    os._exit(0)

def ngambil_page(bingung_url, domain_ah, udah_dikunjungi):
    global stop_crawling
    headers = {"User-Agent": random.choice(USER_AGENTS)}
    try:
        if stop_crawling:
            return []

        response = requests.get(bingung_url, headers=headers, timeout=5, verify=False)
        status_code = response.status_code
        timestamp = datetime.now().strftime(f"{WHITE}[{GREEN}%Y-%m-%d %H:%M:%S{WHITE}]")

        parsed_url = urlparse(bingung_url)
        if parsed_url.netloc == domain_ah:
            color = GREEN
        else:
            color = CYAN

        print(f"{timestamp} {status_code} {color}{bingung_url}{RESET}")

        if status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")

            with ganteng_lock:
                udah_dikunjungi.add(bingung_url)

            links = [
                urljoin(bingung_url, a["href"])
                for a in soup.find_all("a", href=True)
                if domain_ah in urljoin(bingung_url, a["href"])
            ]
            return links
    except requests.exceptions.SSLError as e:
        print(f"{RED}[ERROR] SSL Error: {e}{RESET}", flush=True)
    except Exception as e:
        print(f"{RED}[ERROR] {e}{RESET}", flush=True)
    return []

def web_boring(start_bingung, threads_aja):
    global stop_crawling, executor
    parsed_url = urlparse(start_bingung)
    domain_ah = parsed_url.netloc
    udah_dikunjungi = set()
    bingung_nyari = [start_bingung]

    executor = ThreadPoolExecutor(max_workers=threads_aja)
    while bingung_nyari:
        if stop_crawling:
            break

        futures = {}
        for url_bingung in bingung_nyari:
            with ganteng_lock:
                if url_bingung not in udah_dikunjungi:
                    futures[executor.submit(ngambil_page, url_bingung, domain_ah, udah_dikunjungi)] = url_bingung
        bingung_nyari = []
        for future in futures:
            if stop_crawling:
                break
            result = future.result()
            if result:
                with ganteng_lock:
                    bingung_nyari.extend(link for link in result if link not in udah_dikunjungi)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)

    if len(sys.argv) != 3:
        print("Usage: python3 franklin.py <start_url> <threads>")
        sys.exit(1)

    start_bingung = sys.argv[1]
    try:
        threads_aja = int(sys.argv[2])
    except ValueError:
        print(f"{RED}[ERROR] Threads must be an integer!{RESET}")
        sys.exit(1)

    web_boring(start_bingung, threads_aja)
