import sys
import requests
import time
from subprocess import run, PIPE, DEVNULL, call, Popen
import concurrent.futures
import os
from termcolor import colored

#
# only usable for http proxies in linux
# requirments
# python libraries : subprocess, termcolor
# linux tool "curl"
#


test_file = 'https://download.microsoft.com/download/8/b/4/8b4addd8-e957-4dea-bdb8-c4e00af5b94b/NDP1.1sp1-KB867460-X86.exe'
# we download a file by requests.get

alive_proxies = []


def is_alive(ip, port):
    print(f"Testing proxy {ip}:{port}")

    # the following code is a way to check the type of proxy and check wather it is alive
    # https://stackoverflow.com/a/35382089/11672221
    # the socks type won't be checked because seemes requests is not compatible with socks proxy
    '''
    result = run(f'curl -x socks://{ip}:{port} check-host.net/ip -m 15'.split(),
                    stdout=DEVNULL, stderr=DEVNULL, universal_newlines=True)
    if result.returncode == 0:
        alive_proxies.append(f'socks5://{ip}:{port}')
        print(colored("Alive", "green"), f" socks proxy {ip}:{port}")
        return
    '''

    result = run(f'curl -x http://{ip}:{port} check-host.net/ip -m 15'.split(),
                 stdout=DEVNULL, stderr=DEVNULL, universal_newlines=True)
    if result.returncode == 0:
        alive_proxies.append(f'http://{ip}:{port}')
        print(colored("Alive", "green"), f" http proxy {ip}:{port}")
        return

    print(colored("Dead", "red"), f" proxy {ip}:{port}")


def downloadFile(link, proxy):
    chunk_value = 1024 * 512  # 512 kb
    print("=====================================================")
    print(f"testing proxy: {proxy}")
    try:
        r = requests.get(link, stream=True, proxies=proxy, timeout=20)
        if r.status_code != 200:
            print(f"Error {r.status_code}")
            return
        print(f"Requests code status: {r.status_code}")
        total_length = r.headers.get('content-length')
        print(f"Total length {total_length}")
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
            # print("proxy: ", proxy)
            print("overall speed: ", speed / 1024,
                  " Kbp    Time spent: ", time_spent, " seconds")
        r.close()
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

print("Alive proxies are: ", alive_proxies)

for proxy in alive_proxies:
    downloadFile(test_file, {'http': proxy})
