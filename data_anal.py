import numpy as np
import os
import pandas as pd
import csv
import pandas as pd



def anal(path): #날짜별 촬영 인원수와 각각의 라벨 갯수 통계
    dir_name = os.listdir(path)
    dir_name.sort()
    save_data = []

    for y in dir_name:
        sub_path = path + "/" + y
        jpg_names = os.listdir(sub_path)
        jpg_names.sort()
        dir_count = len(dir_name)
        jpg_label_count = {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0}
        jpg_count = len(jpg_names) / 15
        for jpg in jpg_names:
            temp = jpg.split("_")
            temptemp = np.array(temp[4].split("."))
            if temptemp.shape == (2,):
                jpg_label_count[temp[3]] = jpg_label_count[temp[3]]+1
        save_data.append([y,int(jpg_count),jpg_label_count['1']/5,jpg_label_count['2']/5,jpg_label_count['3']/5,jpg_label_count['4']/5,jpg_label_count['5']/5])
    df = pd.DataFrame.from_dict(save_data)
    df.columns = ['날짜','인원수','매우좋음','좋음','보통','나쁨','매우나쁨']
    df.to_excel(excel_writer="csv_data/data_analysis.xlsx", index=False)

# anal('./src-img')


def analysis2(path): #전체 인원의 날짜별 라벨 통계
    datelist = []
    datalist = {}
    memnamelist = []
    membern = []
    config = open("config/config-member.csv",'r',encoding="utf-8") #config에 입력한 명단 제외한 이미지 삭제
    compare_img = csv.reader(config)
    configl = open("config/config-memberlist.csv",'r',encoding="utf-8") #config에 입력한 명단 제외한 이미지 삭제
    oriname = csv.reader(configl)
    for i in compare_img:
        membern.append(i[0])
    for z in oriname:
        memnamelist.append(z[0])
        datalist[z[0]] = []
    dir_name = os.listdir(path)
    dir_name.sort()
    for y in dir_name:
        datelist.append(y)
    save_data = pd.DataFrame(index=memnamelist,columns=datelist)

    for y in dir_name:
        sub_path = path + "/" + y
        jpg_names = os.listdir(sub_path)
        jpg_names.sort()
        for jpg in jpg_names:
            temp = jpg.split("_")
            temptemp = np.array(temp[4].split("."))
            if temptemp.shape == (2,):
                if [y,temp[3]] not in datalist[temp[1]]:
                    datalist[temp[1]].append([y,temp[3]])

    for memname in memnamelist:
        print("실행1")
        for num in range(len(datalist[memname])):
            print("실행됨")
            save_data.loc[memname][datalist[memname][num][0]] = datalist[memname][num][1]
        
        

    save_data.reset_index(drop=True,inplace=True)
    save_data.index=membern
    save_data.to_excel(excel_writer="csv_data/data_analysis2.xlsx")

analysis2("./src-img")
        
# remove_img("./test_img","config/config.csv")
                

            
        
        