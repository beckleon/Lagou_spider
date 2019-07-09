# encoding: utf-8
import requests
import time
import random
import pymongo
from urllib.request import quote


def get_data(page_num, keyword):
    if page_num == 1:
        first = "true"
    else:
        first = "false"
    data = {
        "first": first,
        "pn": page_num,
        "kd": keyword
    }
    return data


def main():
    for i in range(1, 31):
        print(i)
        time.sleep(random.randint(5, 10))
        ss = requests.session()
        # 先使用 GET 获取 Cookies
        rsp = ss.get(city_url, headers=headers, verify=False)
        # 检测返回的页面是否出错，如果有要求登录账号，就重新发起请求
        doc = rsp.text
        if "网络出错啦" in doc:
            print("retry...")
            rsp = ss.get(city_url, headers=headers, verify=False)
        # 再使用 POST 获取数据
        r = ss.post(city_api_url, headers=headers, data=get_data(i, kd), verify=False)
        print(r.json())
        result = r.json()['content']['positionResult']['result']
        for r in result:
            collection.insert_one(r)


if __name__ == '__main__':
    client = pymongo.MongoClient(host='localhost', port=27017)
    db = client['lagou']
    collection = db["pc_position"]

    kd = "数据分析"
    cityname = "北京"
    city_url = "https://www.lagou.com/jobs/list_{}?city={}&cl=false&fromSearch=true&labelWords=&suginput=".format(
        quote(kd), quote(cityname))
    city_api_url = "https://www.lagou.com/jobs/positionAjax.json?city={}&needAddtionalResult=false".format(quote(cityname))
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36",
        "Referer": city_url,
        "Content-Type": "application/x-www-form-urlencoded;charset = UTF-8"
    }
    main()