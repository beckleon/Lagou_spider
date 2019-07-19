# 从数据抓取到可视化分析

本文的目的：通过介绍从拉勾网抓取全国范围内的“数据分析”的职位数据，到使用 Tableau 进行简单的可视化分析，为大家展现一个使用身边数据的小小应用，也让大家用真实的数据感受一下， 当前市场上的 **数据分析** 这个岗位是什么样的。

## 工具准备：

- Chrome 谷歌浏览器
- Anaconda（预装 python, pandas），安装 requests, BeautifulSoup 库
- MongoDB 数据库
- Tableau 2019.2版本（可到官网下载，试用14天）

## 网站分析：

​		进入拉勾网职位搜索页面，输入 **数据分析** 关键字跳转到结果页面，默认显示全国的搜索结果：发现最多显示30页，每页15条职位信息。这种情况显然不符合我们的要求，为了获取全国的职位信息，需要以城市为单位往下搜索；如果城市结果仍然有30页，则继续往下钻按行政区划搜索。

​		打开 Chrome 浏览器开发者工具，切换到 **Network** 页面，持续点击搜索结果“下一页”，查看网络数据的交互情况，可以在 **XHR** 选项卡发现真正的数据加载请求：

![图一](E:\MyWork\documents\知识分享\20190627-拉勾\imgs\请求结果.png)

## 尝试抓取：

​		**第一步**：模拟发送请求，尝试抓取数据。带上请求头和参数，发送 POST 请求，只会得到如下的结果：

```python
{"status":false,"msg":"您操作太频繁,请稍后再访问","clientIp":"xxx.xxx.xxx.xxx","state":2402}
```

这说明拉勾网的反爬措施是对 Cookies 有要求的。 Cookies 是从浏览器端生成的，但是要从网站的 JavaScript 代码分析出 Cookies 的生成方式，无疑是一件很复杂的事情。这个问题先暂且按下，先考虑把拉勾网支持的所有城市的城市名拉下来，可以找到城市列表页的链接是：https://www.lagou.com/jobs/allCity.html ，只需要带上含有 Accept, Referer 和 User-Agent 三个 Key 的请求头发送 GET 请求，就可以拿到页面的 HTML 代码，使用 BeautifulSoup 解析页面即可获取城市列表。

```python
import requests
from bs4 import BeautifulSoup

headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Referer': 'https://www.lagou.com/jobs/list_%E8%BF%90%E7%BB%B4?city=%E6%88%90%E9%83%BD&cl=false&fromSearch=true&labelWords=&suginput=',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'
}
url = "https://www.lagou.com/jobs/allCity.html?keyword=数据分析&px=default&city=全国"
s = requests.Session()
rsp = s.get(url, headers=headers, verify=False)
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
```

​		**第二步**：为了拿到某个城市的搜索结果，并验证是否有30页（如果有的话，还需要顺便拿到该城市下面的行政区列表），我们还需要继续获取搜索结果的城市页面。以北京为例，使用上面的方法访问链接： https://www.lagou.com/jobs/list_%E6%95%B0%E6%8D%AE%E5%88%86%E6%9E%90?city=%E5%8C%97%E4%BA%AC&cl=false&fromSearch=true&labelWords=&suginput=，确实可以拿到北京的搜索结果首页，在该页面上也能找到结果的总页数30以及北京所有的行政区划。

```python
city_url = "https://www.lagou.com/jobs/list_数据分析?city=北京&cl=false&fromSearch=true&labelWords=&suginput="
ss = requests.session()
# 获取cookies
rsp = ss.get(city_url, headers=headers, verify=False)
# 获取总页数
doc = rsp.text
soup = BeautifulSoup(doc, 'lxml')
num_soup = soup.find("span", class_="totalNum")
total_num = int(num_soup.string)
# 如果总页数为30，就抓取行政区
if total_num == 30:
        district_list = []
        district_soup = soup.find("div", attrs={"class": "contents", "data-type": "district"}).find_all("a")[1:]
        for district in district_soup:
            district_name = district.string
            district_list.append(district_name)
```

​		**第三步**：在第二步中获取到了城市首页的 Cookies，尝试使用这个 Session 发送 POST 请求抓取 AJAX 的接口：

```python
city_api_url = "https://www.lagou.com/jobs/positionAjax.json?city=北京&needAddtionalResult=false"
data = {
    "first": "true",	# 第一页为true，其他为 false
    "pn": 1,			# 页数
    "kd": "数据分析"	# 搜索关键词
}
r = ss.post(city_api_url, headers=headers, verify=False)
print(r.json())
```

的确拿到了 JSON 格式的结果。但是使用这个方法尝试抓取几页之后，依然会得到"您操作太频繁,请稍后再访问"的结果，在尝试使用代理 IP 以及抓取间隔控制等多种方法后，仍然是这样。问题到底出在哪里？为什么还是会被反爬？

通过对网络交互数据的仔细追踪，不难发现每次向 API 发送 POST 请求之后，网站会自动发送一条 GET 请求：

![GET请求](E:\MyWork\documents\知识分享\20190627-拉勾\imgs\GET请求.png)

这条请求并没有什么实质性的作用，所带参数只不过是上一条 POST 请求拿回来结果的公司 ID，故猜想这个 GET 请求是用来确认或者更新 Cookies 的，那么为了确保 Cookies 持续有效，我们只需在每次发送 POST 请求之前，使用 GET 请求刷新 Cookies 即可。为了验证想法，尝试使用下面的代码抓取北京30页的结果：

```python
# encoding: utf-8
import requests
import time
import random
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
    kd = "数据分析"
    for i in range(1, 31):
        # 随即休眠5到10秒
        time.sleep(random.randint(5, 10))
        ss = requests.session()
        # 先使用 GET 获取 Cookies
        rsp = ss.get(city_url, headers=headers, verify=False)
        # 检测返回的页面是否出错，如果有要求登录账号，就重新发起请求
        doc = rsp.text
        if "网络出错啦" in doc:
            print("retry...")
            rsp = ss.get(city_url, headers=headers, verify=False)
            doc = rsp.text
        # 再使用 POST 获取数据
        r = ss.post(city_api_url, headers=headers, data=get_data(i, kd), verify=False)
        print(r.json())

if __name__ == '__main__':
    city_url = "https://www.lagou.com/jobs/list_{}?city={}&cl=false&fromSearch=true&labelWords=&suginput=".format(quote("数据分析"), quote("北京"))
    city_api_url = "https://www.lagou.com/jobs/positionAjax.json?city=北京&needAddtionalResult=false"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36",
        "Referer": city_url,
        "Content-Type": "application/x-www-form-urlencoded;charset = UTF-8"
    }
    main()
```

在尝试的过程中，也曾加入代理 IP 地址进行测试，但是基于某种原因（可能是代理 IP 已经被污染了）不成功，故而放弃；而如果只用本地 IP ，一段时间内抓取太频繁亦会被对方检测出来，严重情况下可能会被封 IP，所以这里每次 GET 请求之前加入了随机的等待时间（5~10 s）；之后发现连续请求若干次之后，GET 请求的页面又会被要求登录账号，这种情况下我们只需要检查返回页面，并重新发起一次 GET 请求就可以了。

在研究反反爬的套路时，我们要大胆假设，小心求证，一步步逼近反爬工程师挖下的坑，架好板子走过去或者找好岔路绕过去。从最终的代码来看，既无法使用代理也无法加入多线程，导致抓取速度很慢，只能说对方网站为了确保自己的数据不被反反爬，确实牺牲了很多性能和网络资源（包括自己的和对方的） -_-!!!

最终的抓取代码加入了对行政区的抓取，并对抓取动作进行一定的整合，有兴趣的同学可以参见 [Github 代码](https://github.com/beckleon/Lagou_spider)。

## 数据清洗：

在2019年7月2日这一天我们抓取了全国45个城市共1997条招聘数据。抓回来的原始数据保存在本地 MongoDB 中，我们需要对其进行清洗并提取出有用的字段之后才能使用。可能感兴趣的字段如下所示：

![数据清洗](E:\MyWork\documents\知识分享\20190627-拉勾\imgs\数据清洗.png)

1. **去重**：以 ***positionId*** 字段对岗位进行去重，因为可能有些发布者会发布一些置顶的急招广告，在每个结果页都展示。
2. **变更格式**：探索发现工作经验 ***workyear*** 、公司规模 ***companySize***  这两个字段的内容都是互不相交的区间，可以进行分类；而工资 ***salary*** 字段不是，需要把这个字段的内容拆开来，分别为最低、最高工资，顺便计算出平均值 ***average_salary***。
3. **去除异常值**：发现一条 ***positionId*** 为6097918的兼职工作，月薪达到了200k-300k，判定为异常值，去掉。
4. **单独处理**：把  ***industryField***,  ***positionAdvantage***, ***positionLables***, ***industryLables***, ***companyLabelList***, ***skillLables*** 这几个适合做词云的字段单独拉出来处理统计次数。

最后剩下1953条有效职位数据，导出至 Excel 文件备用。

## 使用 Tableau 做可视化分析：

由于 Tableau 的操作相对简单，学习成本不高，本文不对其进行讲解。导入数据后，分类放好 **维度** 和 **度量** 的值。为后面准确分析和操作的方便，在 **度量** 中，需要自己创建几个计算字段的公式（右键->创建计算字段）：

- 公司数目：COUNTD([companyId])
- 职位数目：COUNTD([positionId])
- 全职职位的平均工资：SUM(IF [jobNature]='全职' THEN[average_salary] ELSE 0 END)/SUM(IF [jobNature]='全职' THEN[记录数] ELSE 0 END)

我们分三个维度进行分析：

### 1、从职位维度：

![tableau-职位维度](E:\MyWork\documents\知识分享\20190627-拉勾\imgs\tableau-职位维度.png)

可以看到全职工作占据了95.6%的比重，其次是实习职位。从职位的城市分布来看，沿海城市占据了绝对多数，其中北上深广四大一线城市遥遥领先。在此强烈推荐参加高考的考生尽量报考沿海以及一线城市的高校，将来无论实习还是工作机会都大很多。从城市的平均工资来看，北京仍遥遥领先，其次是深圳、杭州、上海，反观广州却跌到了第十。

### 2、从公司来看：

![tableau-公司职位数](E:\MyWork\documents\知识分享\20190627-拉勾\imgs\tableau-公司职位数.png)

“字节跳动”公司招聘的数据分析类职位是最多的，其次是百融云创、京东以及腾讯这一类的大公司。

![tableau-公司规模财务](E:\MyWork\documents\知识分享\20190627-拉勾\imgs\tableau-公司规模财务.png)

需要数据分析类人才的公司基本都是上一定规模的公司，而小公司、初创公司不太需要。

### 3、从对求职者的要求来看：

![tableau-求职者](E:\MyWork\documents\知识分享\20190627-拉勾\imgs\tableau-求职者.png)

大部分职位要求本科学历以上，而且对有3~5年工作经验的求职者比较青睐。

### 4、词云展示：

![tableau-词云](E:\MyWork\documents\知识分享\20190627-拉勾\imgs\tableau-词云.png)

当然还有更多可以分析的维度，有待读者的发掘。

## 结语：

以上从数据抓取到数据清洗，再到可视化分析，为大家展示了如何使用我们身边数据的整个流程。希望大家在掌握工具的同时，也能对自己的工作、生活等方面起到更大的帮助作用。