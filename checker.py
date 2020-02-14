import os
from termcolor import colored
from core import *
import concurrent.futures


def check_proxies(proxies):
    ip, port = proxies.split(':')
    print(f"Testing proxy {ip}:{port}")
    proxy_result = is_alive(ip, port)
    if proxy_result['status'] != 'unavailable':
        alive_proxies.append(proxy_result['proxy'])
        print(colored("Available", "green"), f"{proxy_result['raw_proxy']}")
    else:
        print(colored("Unavailable", "red"), f"{proxy_result['raw_proxy']}")


alive_proxies = []
proxies = []

# changing path to the directory of the file being tun
running_file_path = os.path.dirname(os.path.abspath(__file__))
os.chdir(running_file_path)

with open('proxies.txt', 'r') as proxies_file:
    proxies.extend(proxies_file.read().split("\n"))


with concurrent.futures.ThreadPoolExecutor() as executer:
    # checking the type and availability of proxies at the same time using threads
    executer.map(check_proxies, proxies)

print("====================================================================")
print("Alive proxies are: ", list(map(lambda x: x['http'][7:], alive_proxies)))
print("====================================================================")

for proxy in alive_proxies:
    print("----------------------------------------------------------")
    print(f"Test speed: {proxy}")
    for rec in downloadFile(test_file, proxy):
        if isinstance(rec, Exception):
            print(rec)
        else:
            for key, value in rec.items():
                print(f"{key}: {value}")
