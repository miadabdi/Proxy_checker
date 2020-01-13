# Proxy Checker

## Usage

You should insert your proxies in `server:port` format per line into proxies.txt.  
Then run prroxy_checker.py  

- This program is compatible with Windows, MacOS and Linux.
- Usable for SOCKS4, SOCKS5, HTTP and HTTPS proxies.
- Proxies with authentications are not soppurted, yet. We are trying to provide that in future.

## Requirements

```bash
$ pip3 install termcolor
$ pip3 install pysocks
$ pip3 install -U requests[socks]
```
