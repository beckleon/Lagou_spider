# encoding: utf-8
import requests
import time
import datetime
import random
import pymongo
from urllib.request import quote
from bs4 import BeautifulSoup


def proxys():
    return


def get_data(page_num, keyword):
    """
        生成post的参数
    """
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


def request_page_with_session(session, method, url, data=None):
    time.sleep(random.randint(5, 10))
    if method == "GET":
        # 获取cookies
        rsp = session.get(url, verify=False)
        # 获取总页数
        doc = rsp.text
        if "网络出错啦" in doc:
            print("retry...")
            rsp = session.get(url, verify=False)
            doc = rsp.text
        soup = BeautifulSoup(doc, 'lxml')
        num_soup = soup.find("span", class_="totalNum")
        total_num = int(num_soup.string)

        return session, total_num, soup
    elif method == "POST":
        r = session.post(url, data=data, verify=False)
        content = r.json()['content']['positionResult']['result']
        return content


def get_positions_from_city(city_name, job):
    init_url = "https://www.lagou.com/jobs/list_{}?city={}&cl=false&fromSearch=true&labelWords=&suginput=".format(
        quote(job), quote(city_name))
    city_api_url = "https://www.lagou.com/jobs/positionAjax.json?city={}&needAddtionalResult=false".format(quote(city_name))
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36",
        "Referer": init_url,
        "Content-Type": "application/x-www-form-urlencoded;charset = UTF-8"
    }
    ss = requests.session()
    # 更新 Headers
    ss.headers.update(headers)
    # 获取结果页数 以及返回 session ，以及解析页soup
    ss, total_num, soup = request_page_with_session(ss, 'GET', init_url)
    print(city_name, "total page: ", total_num)

    # 如果页数为30，则获取行政区级别的岗位数据
    if 0 < total_num < 30:
        for i in range(1, total_num + 1):
            print("{} page: {}/{}".format(city_name, i, total_num))
            # 使用 GET 获取 session
            city_ss = requests.session()
            city_ss.headers.update(headers)
            city_ss, _num, _soup = request_page_with_session(city_ss, 'GET', init_url)
            # post 方式获取API结果
            post_data = get_data(i, job)
            result = request_page_with_session(city_ss, 'POST', city_api_url, post_data)
            for posit in result:
                collection.insert_one(posit)
    elif total_num == 30:
        # 获取该城市所有的行政区
        district_list = []
        district_soup = soup.find("div", attrs={"class": "contents", "data-type": "district"}).find_all("a")[1:]
        for district in district_soup:
            district_name = district.string
            district_list.append(district_name)
        # 按行政区获取职位列表
        for dist in district_list:
            district_url = "https://www.lagou.com/jobs/list_{}?px=default&city={}&district={}".format(
                quote(job), quote(city_name), quote(dist))
            ss = requests.session()
            ss.headers.update(headers)
            ss, dist_page_num, dist_soup = request_page_with_session(ss, 'GET', district_url)
            dist_api_url = "https://www.lagou.com/jobs/positionAjax.json?city={}&district={}&" \
                            "needAddtionalResult=false".format(quote(city_name), quote(dist))
            for i in range(1, dist_page_num + 1):
                print("{} - {} page: {}/{}".format(city_name, dist, i, dist_page_num))
                # 使用 GET 获取 session
                dist_ss = requests.session()
                dist_ss.headers.update(headers)
                dist_ss, _num, _soup = request_page_with_session(dist_ss, 'GET', init_url)
                # post 方式获取API结果
                post_data = get_data(i, job)
                result = request_page_with_session(dist_ss, 'POST', dist_api_url, post_data)
                # 遍历结果，插入数据库
                for posit in result:
                    collection.insert_one(posit)
    else:
        print("{} page: {}/{}".format(city_name, 0, total_num))

    return city_name


def main():
    job = "数据分析"
    # 已经完成的城市
    finished_citys = []
    print(len(finished_citys), len(city_list))
    for city in city_list:
        print(city)
        if city in finished_citys:
            continue
        else:
            city_name = get_positions_from_city(city, job)
            finished_citys.append(city_name)
            print(finished_citys)


if __name__ == '__main__':
    client = pymongo.MongoClient(host='localhost', port=27017)
    db = client['lagou']
    collection = db["position"]

    city_list = ['安庆', '澳门特别行政区', '鞍山', '安阳', '安康', '阿克苏', '北京', '保定', '北海', '蚌埠', '包头', '滨州',
                 '保山', '巴中', '宝鸡', '亳州', '巴音郭楞', '百色', '白城', '本溪', '成都', '长沙', '重庆', '常州', '长春',
                 '沧州', '赤峰', '常德', '承德', '潮州', '郴州', '滁州', '朝阳', '昌吉', '东莞', '大连', '德州', '东营',
                 '大庆', '德阳', '大同', '达州', '大理', '儋州', '定西', '德宏', '丹东', '迪庆', '恩施', '鄂州', '鄂尔多斯',
                 '佛山', '福州', '阜阳', '抚州', '抚顺', '防城港', '阜新', '广州', '贵阳', '桂林', '赣州', '广元', '广安',
                 '贵港', '甘孜藏族自治州', '杭州', '合肥', '哈尔滨', '惠州', '海口', '呼和浩特', '淮安', '海外', '湖州',
                 '邯郸', '怀化', '黄石', '衡阳', '衡水', '河源', '菏泽', '黄冈', '淮北', '黄山', '呼伦贝尔', '淮南', '鹤壁',
                 '红河', '哈密', '汉中', '贺州', '河池', '鹤岗', '济南', '金华', '嘉兴', '江门', '济宁', '荆州', '揭阳',
                 '吉林', '晋中', '吉安', '焦作', '晋城', '九江', '酒泉', '荆门', '景德镇', '佳木斯', '锦州', '金昌', '鸡西',
                 '昆明', '开封', '克拉玛依', '喀什', '廊坊', '兰州', '临沂', '洛阳', '柳州', '拉萨', '聊城', '乐山', '龙岩',
                 '吕梁', '漯河', '临汾', '泸州', '连云港', '丽江', '丽水', '六安', '莱芜', '六盘水', '凉山彝族自治州',
                 '娄底', '辽阳', '林芝', '临沧', '来宾', '绵阳', '茂名', '梅州', '眉山', '马鞍山', '牡丹江', '南京', '宁波',
                 '南昌', '南宁', '南通', '南阳', '南充', '宁德', '南平', '内江', '莆田', '濮阳', '攀枝花', '萍乡', '盘锦',
                 '平顶山', '青岛', '泉州', '秦皇岛', '清远', '衢州', '庆阳', '钦州', '曲靖', '齐齐哈尔', '黔西南', '黔南',
                 '黔东南', '日照', '深圳', '上海', '苏州', '沈阳', '石家庄', '汕头', '绍兴', '宿迁', '三亚', '商丘', '韶关',
                 '上饶', '汕尾', '十堰', '宿州', '邵阳', '三门峡', '松原', '四平', '绥化', '遂宁', '三沙', '商洛', '随州',
                 '三明', '天津', '太原', '唐山', '台州', '泰安', '泰州', '台北', '天门', '天水', '铜川', '铁岭', '吐鲁番',
                 '铜仁', '通化', '通辽', '武汉', '无锡', '温州', '潍坊', '乌鲁木齐', '芜湖', '威海', '渭南', '武威', '文山',
                 '梧州', '吴忠', '乌兰察布', '西安', '厦门', '徐州', '西宁', '新乡', '咸阳', '邢台', '香港特别行政区',
                 '湘潭', '襄阳', '孝感', '许昌', '信阳', '咸宁', '宣城', '湘西土家族苗族自治州', '忻州', '兴安盟', '烟台',
                 '银川', '宜昌', '盐城', '扬州', '岳阳', '榆林', '宜宾', '运城', '阳江', '宜春', '云浮', '玉溪', '益阳',
                 '玉林', '雅安', '延边', '营口', '伊犁', '延安', '永州', '鹰潭', '阳泉', '郑州', '珠海', '中山', '湛江',
                 '株洲', '镇江', '淄博', '肇庆', '张家口', '漳州', '遵义', '驻马店', '长治', '舟山', '自贡', '枣庄',
                 '资阳', '周口', '昭通', '张家界']
    main()
