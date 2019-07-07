import pymongo
import json
import pandas as pd


def convert_to_excel(writer, label_name, ldict):
    print(label_name)
    columns = ['标签名', '次数']
    cc_dict = {}
    for c in columns:
        cc_dict[c] = []

    for k, v in ldict.items():
        print(k, v)
        cc_dict['标签名'].append(k)
        cc_dict['次数'].append(v)

    df = pd.DataFrame(data=cc_dict, columns=columns)
    df.to_excel(writer, sheet_name=label_name, na_rep="NULL", index=False)


def count_lables(position_column, column):
    # 去重
    position_dict = {}
    for w in collection.find():
        positionId = w.get(position_column)
        lables = w.get(column)
        position_dict[positionId] = lables

    # 统计词频
    Lables_dict = {}
    for k, v in position_dict.items():
        for ad in v:
            if Lables_dict.get(ad):
                Lables_dict[ad] += 1
            else:
                Lables_dict[ad] = 1
    return Lables_dict


def process_positionAdvantage():
    # 去重
    position_dict = {}
    for w in collection.find():
        positionId = w.get("positionId")
        advantages = w.get("positionAdvantage")
        position_dict[positionId] = advantages
    # 清洗
    Lables_dict = {}
    for k, v in position_dict.items():
        lables = v.replace(",", " ").replace("，", " ").replace("、", " ").replace("\t", " ").replace("。", " ").\
            replace(".", " ").replace(";", " ").replace("；", " ").replace("/", " ").replace("\u3000", " ")
        lable_list = lables.split(" ")
        for ad in lable_list:
            ad = ad.strip()
            if ad:
                if Lables_dict.get(ad):
                    Lables_dict[ad] += 1
                else:
                    Lables_dict[ad] = 1
    return Lables_dict


def main():
    # 把几种标签分别放到一个excel文件的几个sheet上
    writer = pd.ExcelWriter('拉勾网——数据分析岗位——标签统计.xlsx')
    # 处理行业标签、公司标签、技能标签
    position_column = "positionId"
    columns = ["industryLables", "companyLabelList", "skillLables"]
    for column in columns:
        Lables_dict = count_lables(position_column, column)
        convert_to_excel(writer, column, Lables_dict)

    # 处理职位诱惑
    label_name = "职位诱惑"
    Lables_dict = process_positionAdvantage()
    convert_to_excel(writer, label_name, Lables_dict)

    # 最后保存到文件
    writer.save()


if __name__ == '__main__':
    client = pymongo.MongoClient(host='localhost', port=27017)
    db = client['lagou']
    collection = db["position"]
    main()
