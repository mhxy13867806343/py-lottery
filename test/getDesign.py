import requests
from pyquery import PyQuery as pq
url="chrome-extension://lecdifefmmfjnjjinhaennhdlmcaeeeb/main.html#/"

resource=requests.get(url,headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"})
print(resource)