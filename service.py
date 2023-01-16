from tensorflow.keras.models import Model, load_model
from tensorflow.keras.layers import Input, Dense, concatenate, Flatten, Dropout
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.utils import plot_model #모델 시각화된 이미지 뽑는 함수
import cv2
from preprocessing import load_img, get_data, model_processing

import numpy as np

a = []
b = []
finpre = []


def build_cnn():
    cnn_base = ResNet50(
        include_top=False, weights="imagenet", input_shape=[63, 63, 3], classes=5
    )
    cnn_base.trainable = False

    inputA = Input(shape=(63, 63, 3), name="input_img")
    inputB = Input(shape=(1,), name="input_temper")

    base_layer = cnn_base(inputA)
    flatten = Flatten()(base_layer)

    x = concatenate([flatten, inputB])
    x = Dense(32, activation="relu")(x)
    x = Dropout(0.5)(x)
    outputs = Dense(5, activation="softmax")(x)

    model = Model(inputs=[inputA, inputB], outputs=outputs, name="State_output")
    model.compile(
        optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"]
    )
    return model


def model_learn():  # 모델 만들기
    x_train, temper_data, y_train = get_data("./dst-img")
    # temper_data = np.array(temper_data).astype(np.float32)
    # y_train = np.array(y_train)
    print("이미지 데이터:", x_train.shape)
    print("온도 데이터:", temper_data.shape)
    print("라벨 데이터:", y_train.shape)
    model = build_cnn()
    model.fit(
        {"input_img": x_train, "input_temper": temper_data},
        y_train,
        batch_size=100,
        epochs=100,
        validation_split=0.1,
    )
    model.save("State.h5")


# model_learn()


def predict_model(img_data, temper_data, model):
    a = model.predict([img_data, temper_data])
    print(a)
    finpre = []
    sumlist = np.array(a).sum(axis=0)
    print(sumlist)
    allsum = sumlist.sum()
    print(allsum)
    for i in range(5):
        finpre.append(round(float((format(sumlist[i] / allsum * 100.0, "2f"))), 2))
    str = f"매우나쁨: {finpre[0]}% | 나쁨: {finpre[1]}% | 보통: {finpre[2]}% | 좋음: {finpre[3]}% | 매주좋음: {finpre[4]}%"
    return str


def get_model():
    model = load_model("State.h5")
    return model


def do_service(img_data, temper_data, model):  # 최종 실행 함수
    img, temper = model_processing(img_data, temper_data)
    return predict_model(img, temper, model)


def return_text(prelist):
    return


# for i in range(1, 6):
#     img = cv2.imread(str(i) + ".jpg", 1)
#     a.append(img)
#     temper = np.load(str(i) + ".npy")
#     b.append(temper)


# model = get_model()
# x = do_service(a, b, model)
# print(x)
