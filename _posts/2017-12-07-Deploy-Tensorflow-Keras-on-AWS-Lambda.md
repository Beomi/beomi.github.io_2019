---
title: "AWS Lambda에 Tensorflow/Keras 배포하기"
date: 2017-12-07
layout: post
categories:
- Python
- AWS
- Tensorflow
published: false
image: /img/lambda_n_tensorflow.png
---

> 이번 글은 macOS을 기반으로 작성되었지만, `docker` 명령어를 사용할 수 있는 모든 플랫폼(윈도우/맥/리눅스)에서 따라올 수 있습니다.

## 들어가며

여러분이 이미지를 받아 텐서플로로 분류를 해 준 뒤 결과를 반환해주는 작업을 하는 모델을 만들었다고 가정해봅시다. 이때 가장 빠르고 간단하게 결과를 내는(Inference/추론을 하는)방법은 Cuda가속을 할 수 있는 고급 시스템 위에서 텐서플로 모델을 이용해 결과를 반환하도록 서비를 구현할 수 있습니다. 혹은 조금 느리더라도 CPU를 사용하는 EC2와 같은 VM위에서 텐서플로 코드를 동작하게 만들 수도 있습니다.

하지만 만약 여러분이 처리해야하는 이미지가 몇장이 아니라 수십, 수백장을 넘어 수천장을 처리해야한다면 어떻게 될까요?

한 EC2 위에서 서비스를 제공하는 상황에서는 이런 경우라면 `for`문처럼 이미지 하나하나를 돌며 추론을 한다면 전체 이미지의 결과를 내려면 한참 시간이 걸리게 됩니다. 따라서 일종의 병렬 처리를 생각해 보아야 합니다.

즉, 이미지를 순서대로 하나씩 추론하는 대신, 추론하는 코어 함수만을 빼고 결과를 반환하도록 만들어 주면 됩니다.

물론 병렬 처리를 위해서 여러가지 방법들이 있습니다. 여러개의 GPU를 사용하고 있다면 각 GPU별로 작업을 진행하도록 할 수도 있고, 혹은 EC2를 여러개 띄워서 작업을 분산해 진행할 수도 있습니다. 하지만 이 방법보다 조금 더(혹은 상당히 많이) 빠르게 결과를 얻어낼 수 있는 방법이 있습니다.

바로 AWS Lambda를 이용하는 방법입니다.

AWS Lambda는 현재 각 실행별 최대 3GB메모리와 5분의 실행시간 내에서 원하는 코드를 실행해 한 리전에서 동시에 최대 1000개까지 병렬로 실행할 수 있습니다.

즉, 우리가 1만개의 이미지를 처리해야 한다면 한 리전에서만 1000개를 동시에 진행해 10개를 처리하는 시간 내 모든 작업을 마칠 수 있다는 것이죠. 그리고 작업이 끝나고 서버가 자동으로 끝나기 때문에 동작하지 않는 시간에도 돈을 내는 EC2와는 가격차이가 많이 나게됩니다.

이번 가이드는 다음과 같은 시나리오로 작성했습니다.

- 시나리오
    1. s3의 어떤 버킷의 특정한 폴더에 '이미지 파일'을 올린다.
    2. 이미지 파일이 '생성'될 때 AWS Lambda 함수가 실행이 트리거된다.
    3. (Lambda) 모델을 s3에서 다운받아 Tensorflow로 읽는다.
    4. (Lambda) 함수가 트리거 될때 발생한 `event` 객체를 받아 s3에 업로드된 파일의 정보(버킷, 버킷내 파일의 경로)를 가져온다.
    5. (Lambda) s3에 업로드된 이미지 파일을 `boto3`을 통해 가져와 Tensorflow로 Inference를 진행한다.
    6. (Lambda) Inference가 끝난 결과물을 s3에 저장하고 결과값을 json으로 반환한다.

위와같이 진행할 경우 s3에 파일 업로드를 1개를 하든, 1000개를 하든 업로드 자체에 필요한 시간을 제외하면 실행 시간 자체는 동일하게 유지할 수 있습니다. 

(마치 시간복잡도가 O(1)인 척 할 수 있는 것이죠!)

## 환경 준비하기 

AWS Lambda는 아마존에서 RedHat계열의 OS를 새로 만든 Amazon Linux위에서 동작합니다. 그렇기 때문에 만약 우리가 C의존적인 라이브러리를 사용해야한다면 우선 Amazon Linux에 맞게 pip로 설치를 해줘야 합니다. 그리고 간혹 빌드가 필요한 패키지의 경우 사용하고자 하는 OS에 맞춰 빌드작업 역시 진행해야 합니다. Tensorflow 역시 C의존적인 패키지이기 때문에 OS에 맞는 버전을 받아줘야 합니다. 우리가 사용하는 OS는 macOS혹은 windows이기 때문에 `docker`를 통해 Amazon Linux를 받아 그 안에서 빌드를 진행합니다.

도커를 사용하고있다면 그대로 진행해주시면 되고, 도커를 설치하지 않으셨다면 우선 도커를 먼저 설치해주세요.

도커는 [Docker Community Edition Download Page](https://store.docker.com/search?type=edition&offering=community)에서 받으실 수 있습니다.

![도커를 받아주세요](https://www.dropbox.com/s/kk1bu4ekb3jpnbh/%EC%8A%A4%ED%81%AC%EB%A6%B0%EC%83%B7%202017-12-07%2022.31.22.png?dl=1)

여러분이 다음부분을 진행하기 전, `docker`라는 명령어를 터미널 혹은 cmd상에서 입력시 도커가 실행되어야 합니다. 도커가 실행된다면, 우선은 실행할 준비를 마친 것이랍니다.

> 물론 여러분 각자의 모델파일이 있어야 합니다. 이번 가이드에서는 Tensorflow의 예시중 [Image Recognition(imagenet)](https://www.tensorflow.org/tutorials/image_recognition)으로 진행합니다.

## 도커 + Amazon Linux로 빌드 준비하기

이제 `docker`라는 명령어로 도커를 사용해봅시다.

우선 여러분이 작업할 폴더 하나를 만들어 주세요. 저는 지금 `tf_on_lambda`라는 폴더에서 진행하고 있습니다. 이 폴더 안에는 Lambda에서 실행할 python파일이 들어가게 되고, 도커와 이 폴더를 이어줄 것이기 때문에 새 폴더 하나를 만들어서 진행하시는 것을 추천합니다.

폴더를 만들고 들어가셨다면 다음 명령어를 입력해 AmazonLinux 이미지를 받아 도커로 띄워주세요.

```bash
docker run -v $(pwd):/outputs --name lambdapack -d amazonlinux:latest tail -f /dev/null
```

도커 컨테이너의 이름을 `lambdapack`으로 지정하고 현재 폴더(`$(pwd)`)를 도커의 `/outputs`폴더로 연결해줍니다.

![도커가 실행된 모습](https://www.dropbox.com/s/2hrngh6qafwm2s5/%EC%8A%A4%ED%81%AC%EB%A6%B0%EC%83%B7%202017-12-07%2022.48.48.png?dl=1)

성공적으로 받아졌다면 다음과 같이 임의의 난수 id가 생깁니다. 그리고 `docker ps`라는 명령어로 현재 실행중인 컨테이너들을 확인해보면 다음과 같이 `lambdapack`라는 이름을 가진 컨테이너가 생성된 것을 볼 수 있습니다.

![도커 ps](https://www.dropbox.com/s/v2x8mdracvjdxqj/%EC%8A%A4%ED%81%AC%EB%A6%B0%EC%83%B7%202017-12-07%2022.49.31.png?dl=1)

## 람다가 실행할 python 파일 작성하기

그러면 이제 람다가 실제로 **실행**할 python 파일을 만들어줍시다. 이번 가이드에서는 이 파일의 이름을 `index.py`라고 지어보았습니다.

> `index.py` 파일은 사실 어떤 이름으로 해도 상관없습니다만, AWS에 람다 함수를 만들 때 `handler`함수 위치 지정을 `파일이름.함수이름`, 즉 `index.handler`와 같이 적어줄 것이기 때문에 대표적인 이름을 가진 파일로 만들어 주시면 됩니다.

`index.py`안에는 다음과 같은 내용으로 작성해 봅시다. 중요한 부분은 `handler`함수입니다.

> 전체 코드를 바로 이용하시려면 [index.py on gist.github]()을 이용하세요.

제일 먼저 해줘야 하는 부분은 우리가 사용할 라이브러리를 import하는 것이죠.

```python
import boto3 # AWS S3 접근용
import numpy as np 
import tensorflow as tf
import argparse
import os # os.path / os.environ
import re
import urllib.request, urllib.parse, urllib.error # 파일받기 
```

여기서 `boto3` 라이브러리는 AWS Lambda의 python3내에 이미 설치되어있기 때문에 **특정 버전**의 `boto3`을 이용하시려는게 아니라면 도커 컨테이너에 설치하지 않아도 됩니다. (즉, Lambda에 올릴 패키지 zip파일에 boto3이 들어있지 않아도 괜찮습니다.)

import를 끝냈으니 코드를 작성해 봅시다. 우선 S3에서 파일을 다운로드/업로드하는 함수를 만들어줍시다.

```py
ACCESS_KEY = os.environ.get('ACCESS_KEY')
SECRET_KEY = os.environ.get('SECRET_KEY')

def downloadFromS3(strBucket, s3_path, local_path):
    s3_client = boto3.client(
        's3',
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
    )
    s3_client.download_file(strBucket, s3_path, local_path)

def uploadToS3(bucket, s3_path, local_path):
    s3_client = boto3.client(
        's3',
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
    )
    s3_client.upload_file(local_path, bucket, s3_path)
```

AWS 콘솔에서 람다 함수별로 환경변수를 설정해줄 수 있기 때문에, 위과 같이 `os.environ`을 통해 설정한 환경변수 값을 가져옵시다.

물론 여기에 설정한 Access Key와 Secret Key의 iam 유저는 당연히 해당 S3 버킷에 R/W권한이 있어야 합니다.

이 두가지 함수를 통해 S3에서 모델을 가져오고, 모델로 추론한 결과물을 S3에 넣어줄 수 있습니다.

> Note: s3 버킷과 람다 함수는 같은 Region에 있어야 데이터 전송시 비용이 발생하지 않습니다.

`NodeLookup`클래스, `create_graph`함수와 `run_inference_on_image`함수는 ImageNet에서 기본적으로 사용하는 함수이기 때문에 설명은 Tensorflow 홈페이지를 참고해주세요.

이제 가장 중요한 부분인 `handler`함수를 살펴봅시다.

`handler`함수는 기본적으로 `event`와 `context`를 인자로 전달받습니다. 이때 우리가 사용하는 인자는 `event`인자입니다.

우리의 사용 시나리오 중 'S3에 이미지 파일을 올린다', 이 부분이 바로 `event`의 내용이 됩니다.

```py
def handler(event, context):
    if not os.path.exists('/tmp/imagenet/'):
        os.makedirs('/tmp/imagenet/')

    if ('imagelink' in event):
        urllib.request.urlretrieve(event['imagelink'], '/tmp/imagenet/inputimage.jpg')
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--model_dir',
        type=str,
        default='/tmp/imagenet',
        help="""\
      Path to classify_image_graph_def.pb,
      imagenet_synset_to_human_label_map.txt, and
      imagenet_2012_challenge_label_map_proto.pbtxt.\
      """
    )
    parser.add_argument(
        '--image_file',
        type=str,
        default='',
        help='Absolute path to image file.'
    )
    parser.add_argument(
        '--num_top_predictions',
        type=int,
        default=5,
        help='Display this many predictions.'
    )
    FLAGS, unparsed = parser.parse_known_args()
    if os.path.exists(os.path.join('/tmp/imagenet/', 'inputimage.jpg')):
        image = os.path.join('/tmp/imagenet/', 'inputimage.jpg')
    else:
        image = '/tmp/imagenet/cropped_panda.jpg'
    strResult = run_inference_on_image(image)
    return strResult
```










