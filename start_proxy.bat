@echo off
set SETURL="https://website.com"
set PROXY="./proxies/"
set VERIFY="-show"
python proxy.py
pause
start socks5.bat
start socks4.bat
start http.bat
exit
