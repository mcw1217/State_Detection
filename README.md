# State_Detection

- 이미지와 사람의 얼굴 온도를 통해 사람의 상태를 탐지해내는 딥러닝 모델

## Dataset Collect
* 웹캠과 적외선 카메라를 통해 사람의 얼굴과 얼굴 온도를 추출해서 데이터셋으로 만들어냄
* 한번 촬영 시 5장을 찍어 부족한 데이터를 늘림
* 선별된 약 20명의 학생을 대상으로 매일 두번씩 약 한달 간의 데이터를 수집

* 얼굴 인식에 사용된 모델은 haarcascade_frontalface_default.xml을 사용

## Model

CNN을 기반으로 얼굴의 특징을 추출하여 얼굴 온도 데이터와 결합시켜 Dense 층에서 넣은 후 5가지( 매우 나쁨, 나쁨, 보통 ,좋음 ,매우 좋음 ) 라벨로 학습시킨다


## One Touch Install
start.exe를 실행하여, 자동으로 Miniconda설치와 Mysql 연동을 진행함 (Mysql은 아래 링크에서 다운로드 후 start.exe가 위치한 파일 넣어주고 start.exe를 실행시키면 자동으로 
설정이 완료됨

mysql 다운로드 링크
https://drive.google.com/file/d/1tyE0_1dR1o6CFzuyeBVRuc5bABr3QX5p/view

## Diabetes Dataset Analysis

라벨 ( 매우 나쁨 , 매우 나쁨, 보통, 좋음, 매우 좋음 ) 
![2023-04-21 04 52 56](https://user-images.githubusercontent.com/87608623/233473840-e27e4a85-563d-477e-bb37-d34e280469b1.png)



## Model performance analysis

==매우 낮은 성능을 보임==

데이터셋이 정확하지 못하고, 얼굴의 온도 역시 외부와 내부에 따라 급격하게 변하기 때문에 데이터가 부정확함
또한 사람의 표정만으로 그 사람의 상태를 파악하기는 매우 어려움
보다 정확한 데이터셋을 수집할 수 있다면 더 좋은 성능을 낼 수 있을듯 



