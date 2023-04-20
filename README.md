# State_Detection

- 이미지와 사람의 얼굴 온도를 통해 사람의 상태를 탐지해내는 딥러닝 모델

## Dataset Collect
* 웹캠과 적외선 카메라를 통해 사람의 얼굴과 얼굴 온도를 추출해서 데이터셋으로 만들어냄
* 한번 촬영 시 5장을 찍어 부족한 데이터를 늘림
* 선별된 약 20명의 학생을 대상으로 매일 두번씩 약 한달 간의 데이터를 수집

* 얼굴 인식에 사용된 모델은 haarcascade_frontalface_default.xml을 사용 (OpenCV 모델)

## Model

CNN을 기반으로 얼굴의 특징을 추출하여 얼굴 온도 데이터와 결합시켜 Dense 층에서 넣은 후 5가지( 매우 나쁨, 나쁨, 보통 ,좋음 ,매우 좋음 ) 라벨로 학습시킨다


## Diabetes Dataset Analysis

라벨 ( 매우 나쁨 , 매우 나쁨, 보통, 좋음, 매우 좋음 ) 5가지로 분류

![2023-04-21 04 52 56](https://user-images.githubusercontent.com/87608623/233473840-e27e4a85-563d-477e-bb37-d34e280469b1.png)


## Model performance analysis

==매우 낮은 성능을 보임==

데이터셋이 정확하지 못하고, 얼굴의 온도 역시 외부와 내부에 따라 급격하게 변하기 때문에 데이터가 부정확함
또한 사람의 표정만으로 그 사람의 상태를 파악하기는 매우 어려움
보다 정확한 데이터셋을 수집할 수 있다면 더 좋은 성능을 낼 수 있을듯 


## Using

* serviceui.py - 메인 서비스 ui 코드
* service.py - 메인 서비스 코드 (import해서 사용) 
    * do_service가 서비스 실행 코드
* preprocessing.py - 전처리코드 ( import해서 사용)
  * load_img 전처리 코드
  * get_data 전처리된 코드를 모델 학습에 들어갈 수 있도록 전처리
  * model_processing은 서비스 단계에서 전처리하는 코드
* data_anl.py - 데이터 통계 코드
  * anal 라벨, 인원수 통계내어 excel로 return
  * remove_img config/config.csv 에 있는 인원을 제외한 이미지 삭제
  * analysis2 전체 인원의 날짜별 라벨 통계
* fsensor.py - 데이터수집 카메라 ui 코드

> src-img에 날짜별 폴더로 만든 후 이미지 넣으면됨 
> <br>전처리 코드처리하면 dst-img에 자동으로 라벨에 맞게 분류됨
