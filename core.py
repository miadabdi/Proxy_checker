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
chunk_value = 1024 * 512  # 512 kb


def is_alive(ip, port):

    try:
        test_proxy = {'http': f'socks4://{ip}:{port}',
                      'https': f'socks4://{ip}:{port}'}
        r = requests.get(test_url, proxies=test_proxy,
                         timeout=connectionTimeOut)
        if r.status_code == 200:
            alive_proxies.append(test_proxy)
            return {'status': 'available', 'raw_proxy': f"{ip}:{port}", 'proxy': test_proxy, 'type': "socks4"}
    except:
        pass

    try:
        test_proxy = {'http': f'socks5://{ip}:{port}',
                      'https': f'socks5://{ip}:{port}'}
        r = requests.get(test_url, proxies=test_proxy,
                         timeout=connectionTimeOut)
        if r.status_code == 200:
            return {'status': 'available', 'raw_proxy': f"{ip}:{port}", 'proxy': test_proxy, 'type': "socks5"}
    except:
        pass

    try:
        test_proxy = {'http': f'http://{ip}:{port}',
                      'https': f'https://{ip}:{port}'}
        r = requests.get(test_url, proxies=test_proxy,
                         timeout=connectionTimeOut)
        if r.status_code == 200:
            return {'status': 'available', 'raw_proxy': f"{ip}:{port}", 'proxy': test_proxy, 'type': "http"}

    except:
        return {'status': 'unavailable', 'raw_proxy': f"{ip}:{port}"}


def downloadFile(link, proxy):
    try:
        r = requests.get(link, stream=True, proxies=proxy,
                         timeout=(connectionTimeOut, readTimeout))
        if r.status_code != 200:
            raise Exception(f"Error {r.status_code}")
        total_length = r.headers.get('content-length')
        yield {"Response code": r.status_code, "Total length of file": total_length, "Response time": r.elapsed.total_seconds()}
        if total_length != None:
            start = time.time()
            dl = 0
            for chunk in r.iter_content(chunk_value):
                dl += len(chunk)
                if (time.time() - start) > 15:
                    # It breaks if the download process takes more
                    # than 15 secs becuase if the proxy is slow and
                    # it doesn't break it after a cetain time it would
                    # take a lot of time
                    break

            time_spent = time.time() - start
            speed = dl / time_spent  # speed in bits
            r.close()
            yield {"overall speed": speed / 1024, "Time spent": time_spent}

    # except requests.exceptions.ReadTimeout as e:
    #     return("ReadTimeout happend. This is related to test file not the proxy server. Try a different test file")
    #     print(e)

    except Exception as e:
        yield f"Error accured:  {e}"
