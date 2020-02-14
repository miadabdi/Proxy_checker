import sys
import requests
import time
import concurrent.futures
import os
from termcolor import colored

#
# Usable in Windows, MacOS and Linux
# Usable for SOCKS4, SOCKS5, HTTP and HTTPS proxies
# requirments
# $ pip install termcolor
# $ pip install pysocks
# $ pip install -U requests[socks]
#


test_file = 'https://download.microsoft.com/download/8/b/4/8b4addd8-e957-4dea-bdb8-c4e00af5b94b/NDP1.1sp1-KB867460-X86.exe'
test_file = 'http://ipv4.download.thinkbroadband.com/10MB.zip'
# we download a file by requests.get to measure download speed of the proxy

test_url = 'https://google.com'
connectionTimeOut = 25
readTimeout = 45

alive_proxies = []


def is_alive(ip, port):
    def socks4(ip, port):
        try:
            test_proxy = {'http': f'socks4://{ip}:{port}',
                          'https': f'socks4://{ip}:{port}'}
            r = requests.get(test_url, proxies=test_proxy,
                             timeout=connectionTimeOut)
            if r.status_code == 200:
                alive_proxies.append(test_proxy)
                print(colored("Alive", "green"), f" socks4 proxy {ip}:{port}")
                return True
        except Exception as e:
            return e

    def socks5(ip, port):
        try:
            test_proxy = {'http': f'socks5://{ip}:{port}',
                          'https': f'socks5://{ip}:{port}'}
            r = requests.get(test_url, proxies=test_proxy,
                             timeout=connectionTimeOut)
            if r.status_code == 200:
                alive_proxies.append(test_proxy)
                print(colored("Alive", "green"), f" socks5 proxy {ip}:{port}")
                return True
        except Exception as e:
            return e

    def http(ip, port):
        try:
            test_proxy = {'http': f'http://{ip}:{port}',
                          'https': f'https://{ip}:{port}'}
            r = requests.get(test_url, proxies=test_proxy,
                             timeout=connectionTimeOut)
            if r.status_code == 200:
                alive_proxies.append(test_proxy)
                print(colored("Alive", "green"),
                      f" http proxy {ip}:{port}")
                return True
        except Exception as e:
            return e

    print(f"Testing proxy {ip}:{port}")

    if socks4(ip, port) == True:
        return
    elif socks5(ip, port) == True:
        return
    elif http(ip, port) == True:
        return
    else:
        print(colored("Dead", "red"), f" proxy {ip}:{port}")


def downloadFile(link, proxy):
    chunk_value = 1024 * 512  # 512 kb
    print("=====================================================")
    print(f"testing speed: {proxy}")
    try:
        r = requests.get(link, stream=True, proxies=proxy,
                         timeout=(connectionTimeOut, readTimeout))
        if r.status_code != 200:
            print(f"Error {r.status_code}")
            return
        print(f"Requests code status: {r.status_code}")
        total_length = r.headers.get('content-length')
        print(f"Total length {total_length}")
        print(f"Response time: {r.elapsed.total_seconds()} seconds")
        if total_length != None:
            start = time.time()
            dl = 0
            # temp_time = time.time()
            for chunk in r.iter_content(chunk_value):
                dl += len(chunk)
                # the next 5 lines (in addition of temp_time which is a comment now) used to get speed in short period of times
                # time_spent = time.time() - temp_time
                # speed = len(chunk) / time_spent  # speed in bits
                # print(speed / 1024, " Kbp    Time spent: ", time_spent)
                # temp_time = time.time()
                # print()
                if (time.time() - start) > 15:
                    # I think there is logical(?) error here
                    # I think I should end the the request stream
                    # because if I don't it will affect the next
                    # proxy speed test, till it finishes
                    break

            time_spent = time.time() - start
            speed = dl / time_spent  # speed in bits
            print(
                f"overall speed: {speed / 1024} Kbp    Time spent: {time_spent} seconds")

    except requests.exceptions.ReadTimeout as e:
        print("ReadTimeout happend. This is related to test file not the proxy server. Try a different test file")
        print(e)
    except Exception as e:
        print(f"Error accured:  {e}")


def check_proxies(proxies):
    ip, port = proxies.split(':')
    is_alive(ip, port)


proxies = []

# changing path to the directory of the file being tun
running_file_path = os.path.dirname(os.path.abspath(__file__))
os.chdir(running_file_path)

with open('proxies.txt', 'r') as proxies_file:
    proxies.extend(proxies_file.read().split("\n"))


with concurrent.futures.ThreadPoolExecutor() as executer:
    # checking the type and availability of proxies at the same time using threads
    executer.map(check_proxies, proxies)

print("Alive proxies are: ", list(map(lambda x: x['http'][7:], alive_proxies)))

for proxy in alive_proxies:
    downloadFile(test_file, proxy)
