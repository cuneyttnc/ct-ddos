@echo off
set SETURL="https://website.com"
set PROXY="./proxies/"
set VERIFY="-show"
start socks5.bat
start socks4.bat
start http.bat
pause
exit
