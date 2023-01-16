import cv2
import numpy as np
import os
import pandas as pd
import csv

face_cascade = cv2.CascadeClassifier("haarcascades/haarcascade_frontalface_default.xml")

faildata=[]
falldata = 0
jpg_save = []
temper = []
save_label_data = {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0}
minsizelist = []
mintemp =[]
imglist = []
maxtemper = []
labeldata = []
model_img = []
model_temper = []


def load_img(path, dstpath):
    global falldata
    dir_name = os.listdir(path)
    dir_name.sort()

    for y in dir_name:
        sub_path = path + "/" + y
        jpg_names = os.listdir(sub_path)
        jpg_names.sort()
        # print("서브path",sub_path)
        for jpg in jpg_names:
            jpg_path = sub_path + "/" + jpg
            temp = jpg.split("_")
            temptemp = np.array(temp[4].split("."))
            if temptemp.shape == (2,):
                jpg_save.append(jpg_path)
            elif temptemp.shape == (4,):
                temper.append(jpg_path)
            # print("경로 분류",jpg_save, temper)
            print("jpg 갯수:",len(jpg_save))
            print("temper 갯수:",len(temper))

        for imgdata, temperdata in zip(jpg_save, temper):
            img = cv2.imread(imgdata, 1)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            data = np.load(temperdata)
            temp = imgdata.split("_")
            temptemp = np.array(temp[4].split("."))
            faces = face_cascade.detectMultiScale(gray, 1.2, 6)
            face = np.array(faces)
            # print(face.shape)
            # print("얼굴 값",faces)
            if face.shape == (1,4):
                for (x, y, w, h) in faces:
                    img = img[y : y + h, x : x + w]
                    tempa = data[y - 5 : y + h - 5, x : x + w]
                    temp_mean = (tempa.mean(axis=0)).mean()
                    temp_max = tempa.max()
                    name = (
                        dstpath
                        + "/"
                        + temp[3]
                        + "/"
                        + temp[1]
                        + "_"
                        + str(temp_max)
                        + "_"
                        + str(temp_mean)
                        + "_"
                        + temp[4]
                    )
                    # print("이미지 경로",imgdata)
                    minsizelist.append(np.array(img).shape[0])
                    mintemp.append(temp_max)
                    img = cv2.resize(img, (63,63), interpolation = cv2.INTER_AREA)
                    cv2.imwrite(name, img)
                    save_label_data[temp[3]] = save_label_data[temp[3]]+1

            else:
                falldata = falldata + 1 
                faildata.append(imgdata)
        jpg_save.clear()
        temper.clear()    

    print(save_label_data)
    print("실패 데이터 수:", falldata)
    print(np.array(minsizelist).min()) #전체 사진 크기중 가장 작은 값을 알려주는 구문
    # print(np.array(mintemp).max()) 온도 최소 29 최대 34
    save_label_df = pd.DataFrame.from_dict([save_label_data])
    df = pd.DataFrame(faildata, columns=['faildata'])
    df.to_csv("csv_data/fail.csv",index=False)
    save_label_df.to_csv("csv_data/save_label.csv",index=False)

def get_data(path):
    dir_name = os.listdir(path)
    dir_name.sort()

    for y in dir_name:
        sub_path = path + "/" + y
        jpg_names = os.listdir(sub_path)
        jpg_names.sort()
        for i in range(len(y)):
            labeldata.extend([int(y)-1]*len(jpg_names))
            
        # print("서브path",sub_path)
        for jpg in jpg_names:
            jpg_path = sub_path + "/" + jpg
            imglist.append(cv2.imread(jpg_path,3))
            temp = jpg.split("_")
            maxtemper.append(temp[1])
    
    # print(np.array(maxtemper).shape,"이거")
    # print(np.array(imglist).shape,"저거")
    # print(np.array(labeldata).shape,"요거")
    imglist_np = np.array(imglist) /255.
    return imglist_np, np.array(maxtemper).astype(np.float32), np.array(labeldata)

def model_processing(img_data, temper_data):
    for imgdata, temperdata in zip(img_data, temper_data):
        gray = cv2.cvtColor(imgdata, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.2, 6)
        face = np.array(faces)
        if face.shape == (1,4):
            for (x, y, w, h) in faces:
                img = imgdata[y : y + h, x : x + w]
                tempa = temperdata[y - 5 : y + h - 5, x : x + w]
                temp_max = tempa.max()
                img = cv2.resize(img, (63,63), interpolation = cv2.INTER_AREA)
                model_img.append(img)
                model_temper.append(temp_max)

    imglist_np = np.array(model_img) /255.
    return imglist_np, np.array(model_temper).astype(np.float32)


def remove_img(path): #config에 입력한 명단 제외한 이미지 삭제 / 바로 삭제되니 사용에 주의 / 원본 복사해두고 path에 사본 위치 넣는게 좋음
    dir_name = os.listdir(path)
    dir_name.sort()
    config = open("config/config.csv",'r',encoding="utf-8") #config에 입력한 명단 제외한 이미지 삭제
    compare_img = csv.reader(config)
    save_compare = []
    for line in compare_img:
        save_compare.append(line[0])
        

    for y in dir_name:
        sub_path = path + "/" + y
        img_list = os.listdir(sub_path)
        img_list.sort()
        for img in img_list:
            img_path = sub_path + "/" + img
            temp = img_path.split("_")
            if temp[2] not in save_compare:
                os.remove(img_path)

            
    print("삭제 완료")
    
    
# get_data("./dst-img")
load_img("./src-img", "./dst-img")
