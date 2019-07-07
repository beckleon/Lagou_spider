import pymongo
import pandas as pd


def convert_to_excel(pdict):
    columns = ['职位ID', '公司ID', '国家', '经度', '纬度', '行业领域', '教育水平', '工作经验', '城市', '区域', '职位诱惑',
               '最低工资', '最高工资', '平均工资', '职位名称', '公司规模', '公司缩写名', '财务阶段', '工作性质', '公司标签',
               '职位标签', '行业标签', '公司全名', '第一类别', '第二类别', '第三类别', '技术标签']
    cc_dict = {}
    for c in columns:
        cc_dict[c] = []

    for k, v in pdict.items():
        print(k)
        for c in columns:
            cc_dict[c].append(v.get(c))

    df = pd.DataFrame(data=cc_dict, columns=columns)
    df.to_excel('拉勾网——数据分析岗位.xlsx', na_rep="NULL")


def data_clean():
    position_dict = {}
    for w in collection.find():
        positionId = w.get("positionId")
        print(positionId)
        salary = w.get("salary")
        low_salary = salary.lower().split("-")[0].replace("k", "000")
        high_salary = salary.lower().split("-")[1].replace("k", "000")
        average_salary = (int(low_salary)+int(high_salary))/2
        position_dict[positionId] = {
            "职位ID": positionId,
            "经度": w.get("longitude"),
            "纬度": w.get("latitude"),
            "国家": "中国",
            "公司ID": w.get("companyId"),
            "行业领域": w.get("industryField"),
            "教育水平": w.get("education"),
            "工作经验": w.get("workYear"),
            "城市": w.get("city"),
            "区域": w.get("district"),
            "职位诱惑": w.get("positionAdvantage"),
            "最低工资": low_salary,
            "最高工资": high_salary,
            "平均工资": average_salary,
            "职位名称": w.get("positionName"),
            "公司规模": w.get("companySize"),
            "公司缩写名": w.get("companyShortName"),
            "财务阶段": w.get("financeStage"),
            "工作性质": w.get("jobNature"),
            "公司标签": w.get("companyLabelList"),
            "职位标签": w.get("positionLables"),
            "行业标签": w.get("industryLables"),
            "公司全名": w.get("companyFullName"),
            "第一类别": w.get("firstType"),
            "第二类别": w.get("secondType"),
            "第三类别": w.get("thirdType"),
            "技术标签": w.get("skillLables")
        }
    return position_dict


def main():
    position_dict = data_clean()
    convert_to_excel(position_dict)


if __name__ == '__main__':
    client = pymongo.MongoClient(host='localhost', port=27017)
    db = client['lagou']
    collection = db["position"]
    main()
