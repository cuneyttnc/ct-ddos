#!/bin/bash
URL="https://website.com"
PROXY="./proxies"
VERIFY="-show"
export URL PROXY VERIFY
./socks5.sh "$URL" "$PROXY" "$VERIFY" & ./socks4.sh "$URL" "$PROXY" "$VERIFY" & ./http.sh "$URL" "$PROXY" "$VERIFY"
