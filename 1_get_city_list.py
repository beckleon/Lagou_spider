import requests
import time
from urllib.request import quote
from bs4 import BeautifulSoup


def main():
    url_start = "https://www.lagou.com/jobs/allCity.html?keyword=数据分析&px=default&city=全国"
    s = requests.Session()
    rsp = s.get(url_start, headers=headers, timeout=3, verify=False)
    doc = rsp.text
    soup = BeautifulSoup(doc, 'lxml')
    alphabet_list = soup.find_all("ul", class_="city_list")
    city_list = []
    for alpha in alphabet_list:
        cities = alpha.find_all("li")
        for city in cities:
            city_name = city.a.string
            city_list.append(city_name)
    print(city_list)


if __name__ == '__main__':
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Referer': 'https://www.lagou.com/jobs/list_%E8%BF%90%E7%BB%B4?city=%E6%88%90%E9%83%BD&cl=false&fromSearch=true&labelWords=&suginput=',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'
    }
    main()