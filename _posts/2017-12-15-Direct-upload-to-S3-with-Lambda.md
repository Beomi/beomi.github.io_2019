---
title: "AWS S3에 서버없이 파일 업로드하기 with Flask on Lambda"
date: 2017-12-15
layout: post
categories:
- Python
- AWS
- Flask
published: false
image: /img/lambda_n_tensorflow.png
---

## 들어가며

이전 글인 [AWS Lambda에 Tensorflow/Keras 배포하기](/2017/12/07/Deploy-Tensorflow-Keras-on-AWS-Lambda/)에서 Lambda 함수가 실행되는 트리거는 s3버킷에 파일이 **생성**되는 것이었습니다.

물론 파일을 올릴 수 있는 방법은 여러가지가 있습니다. 아주 단순하게 POST 폼 전송 요청을 받고 `boto3`등을 이용해 서버에서 s3으로 파일을 전송할 수도 있고, 더 단순하게는 AWS s3 콘솔을 이용해 파일을 올리라고 할 수도 있습니다.

하지만 이런 부분에는 약간의 단점이 함께 있습니다.

첫 번째 방법처럼 파일을 수신해 다시 s3에 올린다면 그 과정에서 서버 한대가 상시로 켜져있어야 하고 전송되는 속도 역시 서버에 의해 제약을 받습니다. 한편 두 번째 방법은 가장 단순하지만 제3자에게서 파일을 받기 위해서 AWS 계정(비록 제한된 권한이 있다 하더라도)을 제공한다는 것 자체가 문제가 됩니다.

따라서 이번 글에서는 사용자의 브라우저에서 바로 s3으로 POST 요청을 전송할 수 있도록 만드는 과정을 다룹니다.

## 시나리오

![](https://www.dropbox.com/s/rh6bo6b7slztfae/Screenshot%202017-12-15%2018.15.38.png?dl=1)

사용자는 아주 일반적인 Form 하나를 보게 됩니다. 여기에서 드래그-드롭 혹은 파일 선택을 이용해 일반적으로 파일을 올리게 됩니다. 물론 이 때 올라가는 주소는 AWS S3의 주소가 됩니다.

하지만 이게 바로 이뤄진다면 문제가 생길 소지가 많습니다. 먼저 




## 참조

- [Browser-Based Upload using HTTP POST (Using AWS Signature Version 4)](http://docs.aws.amazon.com/ko_kr/AmazonS3/latest/API/sigv4-post-example.html)





