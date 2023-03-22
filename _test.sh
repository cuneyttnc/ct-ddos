#!/bin/bash
URL="https://airport.online/istanbul-airport/"
PROXY="./proxies"
VERIFY="-check -show"
export URL PROXY VERIFY
python3 ct.py -url $URL -m cc -v http -t 1000 -f $PROXY/http.txt -b 1 -s 2592000 $VERIFY