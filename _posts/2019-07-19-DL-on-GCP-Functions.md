---
title: "PyTorch on GCP Functions"
date: 2019-07-19
layout: post
categories:
  - gcp
  - pytorch
published: false
image: https://beomi-tech-blog.s3.amazonaws.com/img/2019-07-19-050354.jpg

---

## Intro

2017년 12월 [AWS Lambda에 Tensorflow/Keras 배포하기](/2017/12/07/Deploy-Tensorflow-Keras-on-AWS-Lambda/)에서는 AWS의 서버리스 플랫폼인 Lambda와 API Gateway를 통해 모델을 탑재하고 API 서비스를 만드는 과정을 담았다.

하지만 2017년의 Tensorflow 1.4, PyTorch 0.3 혹은 그 이전버전들은 pip로 설치하는 패키지와 모듈의 크기가 250MB 이내여서 한번에 업로드가 가능했지만, 최근의 Tensorflow 1.14혹은 2.0, 그리고 PyTorch 1.1등은 pip로 설치한 뒤 so파일 압축을 진행해도 250MB는 훨씬 넘어버린다. (그만큼 기능도 많이 들어갔지만..)

따라서 어쩔수 없는 방법으로 패키지 쪼개기를 통해 s3에서 나머지 패키지를 받아서 PATH에 등록하는 등의 방법을 적용할 수 있었지만, 서버리스 플랫폼들은 `실행시간 == 돈` 이기 때문에 돈이 줄줄 새는 것과 같다. 실제 딥러닝 연산 컴퓨팅에 들어가는 비용보다 s3에서 전송받아서 압축을 해제하는 시간에 더 많은 지출이 나간다는 본말 전도가 생기는 것이다.

그래서 GCP와 Azure등을 살펴보던 차, GCP는 현재 아래와 같이 최대 배포크기 500MB인 것을 볼 수 있다. (AWS는 앞서 말한 것처럼 250MB으로 제한된다.)

![image-20190719145141941](https://beomi-tech-blog.s3.amazonaws.com/img/2019-07-19-055142.png)

> 그렇다면 AWS Lambda보다 GCP Functions가 무조건 낫나? NO!
>
> 위 사진에서 볼 수 있는 것처럼 GCP Functions는 최대 메모리가 2GB이지만 AWS Lambda는 현재 3GB까지 지원되기 때문에 램이 부족하다면 AWS Lambda를 쓰는 것이 낫다.

한편 GCP Functions에서 `python3.7` 환경을 제공해주는 등 Python에 대한 지원이 증가하고 있고, 7월 9일 GCP 블로그에 [How to serve deep learning models using TensorFlow 2.0 with Cloud Functions](https://cloud.google.com/blog/products/ai-machine-learning/how-to-serve-deep-learning-models-using-tensorflow-2-0-with-cloud-functions) 라는 글도 올라오는 등, GCP Functions에 딥러닝 모듈을 올려서 서빙하려는 시도들이 보이는 듯 하다.

위 블로그에서는 Tensorflow2.0을 올렸으니, 이번 글에서는 **PyTorch1.1**을 올려보자.

## GCP Functions의 장점들

### 자동 API Endpoint 생성

우선 AWS Lambda 함수와의 비교를 해야 한다. Lambda에 딥러닝 모듈을 올리고 웹 API로 배포하려면 Lambda뿐만 아니라 API Gateway 설정을 통해 Lambda 함수를 트리거할 수 있도록 별도의 설정을 진행해야 한다.

이때 GCP Functions의 장점이 나오는데, GCP Functions는 별도의 설정 없이 `HTTP` 를 트리거로 선택하는 것 만으로 즉시 API Endpoint URI가 생긴다.

![image-20190719145604774](https://beomi-tech-blog.s3.amazonaws.com/img/2019-07-19-055605.png)

위 스크린샷과 같이 트리거 유형을 HTTP로 설정하면 위와 같은 URL에서 즉시 API Call을 통해 함수를 실행할 수 있다.

### requirements.txt/Pipfile로 패키지 관리

AWS Lambda에서는 AWS Layers([AWS Lambda Layers로 함수 공통용 Python 패키지 재사용하기](/2018/11/30/using-aws-lambda-layers-on-python3/) 참고)를 통해 Python 의존 패키지 관리를 좀 더 쉽게 할 수 있도록 만들어주었다. (2018년 11월) 하지만 이것 역시 docker나 VM등을 이용해 파이썬 패키지를 빌드하는 과정이 필요하다. (귀찮다!)

GCP Functions에서는 우리가 파이썬 프로젝트에서 의존성 패키지를 관리할때 사용하는 `requirements.txt` 혹은 `Pipfile` 을 업로드하면 자동으로 알아서 설치까지 진행해준다! (우와)







