---
title: "AWS Lambda에 Tensorflow/Keras 배포하기"
date: 2017-12-07
layout: post
categories:
- python
- aws
- tensorflow
published: true
image: https://d1sr4ybm5bj1wl.cloudfront.net/img/lambda_n_tensorflow_updated.png
---

> Update @ 20190306: `amazonlinux:latest` 버전이 `2`버전이 latest로 변경됨에 따라 아래 코드를 `amazonlinux:1`로 변경

> 이번 글은 macOS을 기반으로 작성되었지만, `docker` 명령어를 사용할 수 있는 모든 플랫폼(윈도우/맥/리눅스)에서 따라올 수 있습니다.

## 들어가며

여러분이 이미지를 받아 텐서플로로 분류를 해 준 뒤 결과를 반환해주는 작업을 하는 모델을 만들었다고 가정해봅시다. 이때 가장 빠르고 간단하게 결과를 내는(Inference/추론을 하는)방법은 Cuda가속을 할 수 있는 고급 시스템 위에서 텐서플로 모델을 이용해 결과를 반환하도록 서비스를 구현할 수 있습니다. 혹은 조금 느리더라도 CPU를 사용하는 EC2와 같은 VM위에서 텐서플로 코드를 동작하게 만들 수도 있습니다.

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
    6. (Lambda) Inference가 끝난 결과물을 s3에 저장하거나 결과값을 DynamoDB에 저장하거나 혹은 API Gateway를 통해 json으로 반환한다.

위와같이 진행할 경우 s3에 파일 업로드를 1개를 하든, 1000개를 하든 업로드 자체에 필요한 시간을 제외하면 실행 시간 자체는 동일하게 유지할 수 있습니다. 

(마치 시간복잡도가 O(1)인 척 할 수 있는 것이죠!)

## 환경 준비하기 

> 오늘 사용한 예제는 [Github tf-keras-on-lambda Repo](https://github.com/Beomi/tf-keras-on-lambda)에서 확인할 수 있습니다.

AWS Lambda는 아마존에서 RedHat계열의 OS를 새로 만든 Amazon Linux위에서 동작합니다. 그렇기 때문에 만약 우리가 C의존적인 라이브러리를 사용해야한다면 우선 Amazon Linux에 맞게 pip로 설치를 해줘야 합니다. 그리고 간혹 빌드가 필요한 패키지의 경우 사용하고자 하는 OS에 맞춰 빌드작업 역시 진행해야 합니다. Tensorflow 역시 C의존적인 패키지이기 때문에 OS에 맞는 버전을 받아줘야 합니다. 우리가 사용하는 OS는 macOS혹은 windows이기 때문에 `docker`를 통해 Amazon Linux를 받아 그 안에서 빌드를 진행합니다.

도커를 사용하고있다면 그대로 진행해주시면 되고, 도커를 설치하지 않으셨다면 우선 도커를 먼저 설치해주세요.

도커는 [Docker Community Edition Download Page](https://store.docker.com/search?type=edition&offering=community)에서 받으실 수 있습니다.

![도커를 받아주세요]({{site.static_url}}/img/dropbox/2017-12-07%2022.31.22.png)

여러분이 다음부분을 진행하기 전, `docker`라는 명령어를 터미널 혹은 cmd상에서 입력시 도커가 실행되어야 합니다. 도커가 실행된다면, 우선은 실행할 준비를 마친 것이랍니다.

> 물론 여러분 각자의 모델파일이 있어야 합니다. 이번 가이드에서는 Keras 예시 중 Pre-trained squeezenet을 이용한 Image Classification(imagenet)으로 진행합니다.

## 결과 저장용 DynamoDB 만들기(Optional)

우리가 predict를 진행하고 나서 나온 결과물을 어딘가에 저장해둬야 합니다. AWS에는 DynamoDB라는 간단한 NoSQL DB가 있으니, 이걸 이용해 결과물을 저장해 봅시다.

우선 DynamoDB 메뉴에서 아래와 같이 새 테이블 하나를 만들어 줍시다.

![]({{site.static_url}}/img/dropbox/Screenshot%202017-12-14%2010.10.35.png)

기본키 정도만 문자열 필드 `filename`을 만들고 테이블을 생성해 줍시다.

이제 기본키만 지키면 나머지 필드는 자유롭게 올릴 수 있습니다. (물론 기본키와 정렬키만 인덱스가 걸리기 때문에, 빠른 속도가 필요하다면 인덱스를 건 뒤 데이터를 추가해줘야 합니다.)

## squeezenet ImageNet 모델 s3에 올리기

이번 글에서는 squeezenet Imagenet 모델을 이용해 predict를 진행합니다. `squeezenet_weights_tf_dim_ordering_tf_kernels.h5`파일이 필요한데, AWS Lambda에서 비용이 들지 않으며 빠른 속도로 모델을 받아오기 위해서는 같은 리전의 s3에 파일을 올려둬야 합니다. 

![keras-blog 버킷에 올린 모델 파일]({{site.static_url}}/img/dropbox/Screenshot%202017-12-13%2014.40.38.png)

이번 글에서는 `keras-blog`라는 s3 버킷의 `squeezenet` 폴더에 파일을 올려두었습니다.

각 파일은 아래 링크에서 받을 수 있습니다. 아래 두 파일을 받아 s3 버킷에 올려주세요.

- [squeezenet_weights_tf_dim_ordering_tf_kernels.h5](https://github.com/rcmalli/keras-squeezenet/releases/download/v1.0/squeezenet_weights_tf_dim_ordering_tf_kernels.h5)

## `squeezenet.py` 만들기

Keras의 squeezenet은 [squeezenet.py](https://github.com/rcmalli/keras-squeezenet/blob/master/keras_squeezenet/squeezenet.py)을 참조합니다. 하지만 이 파일에는 Pre-Trained Model의 경로를 바꿔주기 때문에 이 부분을 약간 수정한 커스텀 `squeezenet.py`를 만들어주었습니다.

이 파일을 다운받아 여러분의 `index.py` 옆에 놓아두세요.

- [수정된 squeezenet.py](https://github.com/Beomi/tf-keras-on-lambda/blob/master/squeezenet.py)

## 도커 + Amazon Linux로 빌드 준비하기

이제 `docker`라는 명령어로 도커를 사용해봅시다.

우선 여러분이 작업할 폴더 하나를 만들어 주세요. 저는 지금 `tf_on_lambda`라는 폴더에서 진행하고 있습니다. 이 폴더 안에는 Lambda에서 실행할 python파일이 들어가게 되고, 도커와 이 폴더를 이어줄 것이기 때문에 새 폴더 하나를 만들어서 진행하시는 것을 추천합니다.

폴더를 만들고 들어가셨다면 다음 명령어를 입력해 AmazonLinux 이미지를 받아 도커로 띄워주세요.

```bash
docker run -v $(pwd):/outputs --name lambdapack -d amazonlinux:1 tail -f /dev/null
```

도커 컨테이너의 이름을 `lambdapack`으로 지정하고 현재 폴더(`$(pwd)`)를 도커의 `/outputs`폴더로 연결해줍니다.

![도커가 실행된 모습]({{site.static_url}}/img/dropbox/2017-12-07%2022.48.48.png)

성공적으로 받아졌다면 다음과 같이 임의의 난수 id가 생깁니다. 그리고 `docker ps`라는 명령어로 현재 실행중인 컨테이너들을 확인해보면 다음과 같이 `lambdapack`라는 이름을 가진 컨테이너가 생성된 것을 볼 수 있습니다.

![도커 ps]({{site.static_url}}/img/dropbox/2017-12-07%2022.49.31.png)

## 람다가 실행할 python 파일 작성하기

그러면 이제 람다가 실제로 **실행**할 python 파일을 만들어줍시다. 이번 가이드에서는 이 파일의 이름을 `index.py`라고 지어보았습니다.

> `index.py` 파일은 사실 어떤 이름으로 해도 상관없습니다만, AWS에 람다 함수를 만들 때 `handler`함수 위치 지정을 `파일이름.함수이름`, 즉 `index.handler`와 같이 적어줄 것이기 때문에 대표적인 이름을 가진 파일로 만들어 주시면 됩니다.

`index.py`안에는 다음과 같은 내용으로 작성해 봅시다. 중요한 부분은 `handler`함수입니다.

> 전체 코드를 바로 이용하시려면 [index.py on GIST](https://github.com/Beomi/tf-keras-on-lambda/blob/master/index.py)을 이용하세요.

제일 먼저 해줘야 하는 부분은 우리가 사용할 라이브러리를 import하는 것이죠.

```python
import boto3 # AWS S3 접근용
from tensorflow.python import keras # Keras!
from tensorflow.python.keras.preprocessing import image
from tensorflow.python.keras.applications.resnet50 import preprocess_input, decode_predictions
import numpy as np
import io # File 객체를 메모리상에서만 이용하도록
import os # os.path / os.environ
from PIL import  Image # Image 객체 
import urllib.request # 파일받기 

# (.h5경로변경추가, 레포의 squeezenet.py를 확인하세요.)
from squeezenet import Squeezenet # 커스텀한 squeezenet 
```

이 중 `boto3` 라이브러리는 AWS Lambda의 python3내에 이미 설치되어있기 때문에 **특정 버전**의 `boto3`을 이용하시려는게 아니라면 도커 컨테이너에 설치하지 않아도 됩니다. (즉, Lambda에 올릴 패키지 zip파일에 boto3이 들어있지 않아도 괜찮습니다.)

import를 끝냈으니 코드를 작성해 봅시다. 우선 S3에서 파일을 다운로드/업로드하는 함수를 만들어줍시다.

```python
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

> Note: s3 버킷과 람다 함수는 같은 Region에 있어야 데이터 전송 비용이 발생하지 않습니다.

이제 가장 중요한 부분인 `handler`함수를 살펴봅시다.

`handler`함수는 기본적으로 `event`와 `context`를 인자로 전달받습니다. 이때 우리가 사용하는 인자는 `event`인자입니다.

우리의 사용 시나리오 중 'S3에 이미지 파일을 올린다', 이 부분이 바로 `event`의 내용이 됩니다.

### S3 Event의 내용

AWS에서 Lambda 실행이 트리거 될 때 전달되는 `event`는 파이썬의 딕셔너리 형태로 전달됩니다.

만약 여러분이 `s3`에 **파일이 추가**되는 이벤트를 Lambda에 연결해두셨다면 파일이 업로드 될 때 마다 아래와 같은 딕셔너리가 전달됩니다.

아래 예시는 `csv_icon.png`를 `keras-blog`라는 버킷내 `wowwow` 폴더에 올렸을때 발생한 `event` 객체입니다.

```python
# event 객체
{
    'Records': [
        {
            'eventVersion': '2.0',
            'eventSource': 'aws:s3',
            'awsRegion': 'ap-northeast-2', # 버킷 리전
            'eventTime': '2017-12-13T03:28:13.528Z', # 업로드 완료 시각 
            'eventName': 'ObjectCreated:Put',
            'userIdentity': {'principalId': 'AFK2RA1O3ML1F'},
            'requestParameters': {'sourceIPAddress': '123.24.137.5'},
            'responseElements': {
                'x-amz-request-id': '1214K424C14C384D',
                'x-amz-id-2': 'BOTBfAoB/gKBbn412ITN4t2psTW499iMRKZDK/CQTsjrkeSSzSdsDUMGabcdnvHeYNtbTDHoHKs='
            },
            's3': {
                's3SchemaVersion': '1.0', 'configurationId': 'b249eeda-3d48-4319-a7e2-853f964c1a25',
                'bucket': {
                    'name': 'keras-blog', # 버킷 이름 
                    'ownerIdentity': {
                        'principalId': 'AFK2RA1O3ML1F'
                    },
                    'arn': 'arn:aws:s3:::keras-blog'
                },
                'object': {
                    'key': 'wowwow/csv_icon.png', # 버킷 내 파일의 절대경로
                    'size': 11733, # 파일 크기
                    'eTag': 'f2d12d123aebda1cc1fk17479207e838',
                    'sequencer': '125B119E4D7B2A0A48'
                }
            }
        }
    ]
}
```

여기서 봐야 하는 것은 `bucket` 내 `name`와 `object`내 `key`입니다. 각각 업로드된 버킷의 이름과 버킷 내 파일이 업로드된 경로를 알려주기 때문에 S3 내 업로드된 파일의 절대경로를 알 수 있습니다.

따라서 `handler`함수 내 다음과 같이 버킷이름과 버킷 내 파일의 경로를 얻을 수 있습니다.

```python
# 윗부분 생략
def handler(event, context):
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    # bucket_name은 'keras-blog' 가 됩니다.
    file_path = event['Records'][0]['s3']['object']['key']
    # file_path는 'wowwow/csv_icon.png'가 됩니다.
```

이를 통해 파일 업로드 이벤트 발생시마다 어떤 파일을 처리해야할 지 알 수 있습니다.

### s3에서 이미지 파일 받아오기

이제 어떤 파일을 처리해야 할지 알 수 있게 되었으니 `downloadFromS3` 함수를 통해 실제로 파일을 가져와봅시다.

```python
# 윗부분 생략
def handler(event, context):
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    file_path = event['Records'][0]['s3']['object']['key']
    file_name = file_path.split('/')[-1] # csv_icon.png
    downloadFromS3(bucket_name, file_path, '/tmp/'+file_name)
```

위 코드를 보면 s3에 올라간 파일을 `/tmp`안에 받는 것을 볼 수 있습니다. AWS Lambda에서는 '쓰기' 권한을 가진 것은 오직 `/tmp`폴더뿐이기 때문에 우리가 파일을 받아 사용하려면 `/tmp`폴더 내에 다운받아야 합니다. (혹은 온메모리에 File 객체로 들고있는 방법도 있습니다.)

### Prediction Model 다운받기 (Optional)

> 만약 여러분이 그냥 사용한다면 Github에서 파일을 다운받게 됩니다. 이때 속도가 굉장히 느려 lambda비용이 많이 발생하기 때문에 여러분의 s3 버킷에 실제 파일을 올리고 s3에서 파일을 받아 사용하시는 것을 추천합니다.

우리는 위에서 squeezenet모델을 사용했는데, 이때 모델 가중치를 담은 `.h5`파일을 먼저 받아야 합니다. `handler` 함수 내 다음 두 파일을 더 받아줍시다.

```python
def handler(event, context):
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    file_path = event['Records'][0]['s3']['object']['key']
    file_name = file_path.split('/')[-1]
    downloadFromS3(bucket_name, file_path, '/tmp/'+file_name)
    downloadFromS3(
        'keras-blog', 
        'squeezenet/squeezenet_weights_tf_dim_ordering_tf_kernels.h5',
        '/tmp/squeezenet_weights_tf_dim_ordering_tf_kernels.h5'
    ) # weights용 h5를 s3에서 받아오기 
```

### squeezenet 모델로 Predict 하기 

이제 s3에 올라간 이미지 파일을 Lambda내 `/tmp`폴더에 받았으니 Predict를 진행해봅시다. `predict`라는 함수를 아래와 같이 이미지 경로를 받아 결과를 반환하도록 만들어 줍시다.

```python
# index.py 파일, handler함수보다 앞에 
def predict(img_local_path):
    model = Squeezenet(weights='imagenet')
    img = image.load_img(img_local_path, target_size=(224, 224))
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x)
    preds = model.predict(x)
    res = decode_predictions(preds)
    return res

def handler(event, context):
    # 내용 생략 ...
```

`predict`함수는 `squeezenet`의 Pre-trained 모델을 이용해 이미지 예측을 진행합니다.

그러면 실제 `handler`함수에서 `predict`함수를 실행하도록 수정해줍시다.

```python
def predict(img_local_path):
    # 내용 생략 ...

def handler(event, context):
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    file_path = event['Records'][0]['s3']['object']['key']
    file_name = file_path.split('/')[-1]
    downloadFromS3(bucket_name, file_path, '/tmp/'+file_name)
    downloadFromS3(
        'keras-blog', 
        'squeezenet/squeezenet_weights_tf_dim_ordering_tf_kernels.h5',
        '/tmp/squeezenet_weights_tf_dim_ordering_tf_kernels.h5'
    )
    result = predict('/tmp/'+file_name) # 파일 경로 전달 
    return result
```

완성이네요!

## DynamoDB에 결과 올리기(Optional)

위 predict의 결과는 단순히 결과가 생기기만 하고 결과를 저장하거나 알려주는 부분은 없습니다. 이번 글에서는 간단한 예시로 AWS DynamoDB에 쌓아보는 부분을 추가해보겠습니다.

`predict`함수를 통해 생성된 `result`는 다음과 같은 모습이 됩니다.

```python
# result[0]의 내용, tuples in list
[('n02099712', 'Labrador_retriever', 0.68165195), ('n02099601', 'golden_retriever', 0.18365686), ('n02104029', 'kuvasz', 0.12076716), ('n02111500', 'Great_Pyrenees', 0.0042763283), ('n04409515', 'tennis_ball', 0.002152696)]
```

따라서 `map`을 이용해 다음과 같이 바꿔줄 수 있습니다.

```python
_tmp_dic = {x[1]:{'N':str(x[2])} for x in result[0]}
dic_for_dynamodb = {'M': _tmp_dic}
```

그러면 `dic_for_dynamodb`는 아래와 같은 형태로 나오게 됩니다. 

> NOTE: 숫자는 `float`나 `int`가 아닌 `str`로 바꾸어 전달해야 오류가 나지 않습니다. DynamoDB의 제약입니다.

```python
{
    'M':{
            'Labrador_retriever': {'N': '0.68165195'}, 
            'golden_retriever': {'N': '0.18365686'}, 
            'kuvasz': {'N': '0.12076716'}, 
            'Great_Pyrenees': {'N': '0.0042763283'}, 
            'tennis_ball': {'N': '0.002152696'}
        }
}
```

데이터를 넣기 위해서는 `dict`타입으로 만든 객체를 `put`할수 있는데, 이때 각각의 키에 대해 타입을 알려줘야 합니다. `M`은 이 객체가 `dict`타입이라는 것을, `N`은 이 타입이 숫자라는 것을, `S`는 문자열이라는 것을 의미합니다.

> 더 상세한 내용은 [DynamoDB에 데이터 넣기](https://boto3.readthedocs.io/en/latest/reference/services/dynamodb.html#DynamoDB.Client.put_item)를 참고하세요.

이제 이 방식을 이용해 `result`를 반환하기 전 DynamoDB에 데이터를 넣어줄 수 있습니다.

```python
def handler(event, context):
    # 중간 생략 ...
    result = predict('/tmp/'+file_name)
    _tmp_dic = {x[1]:{'N':str(x[2])} for x in result[0]}
    dic_for_dynamodb = {'M': _tmp_dic}
    dynamo_client = boto3.client(
        'dynamodb', 
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
        region_name='ap-northeast-2' # DynamoDB는 리전 이름이 필요합니다.
    )
    dynamo_client.put_item(
        TableName='keras-blog-result', # DynamoDB의 Table이름
        Item={
            'filename': {
                'S': file_name,
            },
            'predicts': dic_for_dynamodb,
        }
    )
    return result
```

## 도커로 Lambda에 올릴 `pack.zip`파일 만들기 

AWS Lambda에 함수를 올리려면 AmazonLinux에 맞게 pip패키지들을 `index.py` 옆에 같이 설치해준 뒤 압축파일(.zip)으로 묶어 업로드해야 합니다.

이때 약간의 제약이 있는데, AWS콘솔에서 Lambda로 바로 업로드를 하려면 .zip파일이 50MB보다 작아야 하고, S3에 .zip파일을 올린 뒤 Lambda에서 가져와 사용하려면 압축을 푼 크기가 250MB보다 작아야 합니다.

문제는 Tensorflow나 기타 라이브러리를 모두 설치하면 용량이 무지막지하게 커진다는 점인데요, 이를 해결하기 위해 사용하지 않는 부분을 strip하는 방법이 들어갑니다.

앞서만든 AmazonLinux 기반 컨테이너인 `lambdapack`를 이용해 패키지들을 설치하고 하나의 압축파일로 만들어줍시다.

아래 내용의 `buildPack.sh`파일을 `index.py` 옆에 만들어 주세요.

```sh
# buildPack.sh
dev_install () {
    yum -y update
    yum -y upgrade
    yum install -y \
    wget \
    gcc \
    gcc-c++ \
    python36-devel \
    python36-virtualenv \
    python36-pip \
    findutils \
    zlib-devel \
    zip
}

pip_rasterio () {
    cd /home/
    rm -rf env
    python3 -m virtualenv env --python=python3
    source env/bin/activate
    text="
    [global]
    index-url=http://ftp.daumkakao.com/pypi/simple
    trusted-host=ftp.daumkakao.com
    "
    echo "$text" > $VIRTUAL_ENV/pip.conf
    echo "UNDER: pip.conf ==="
    cat $VIRTUAL_ENV/pip.conf
    pip install -U pip wheel
    pip install --use-wheel "h5py==2.6.0"
    pip install "pillow==4.0.0"
    pip install protobuf html5lib bleach --no-deps
    pip install --use-wheel tensorflow --no-deps
    deactivate
}


gather_pack () {
    # packing
    cd /home/
    source env/bin/activate

    rm -rf lambdapack
    mkdir lambdapack
    cd lambdapack

    cp -R /home/env/lib/python3.6/site-packages/* .
    cp -R /home/env/lib64/python3.6/site-packages/* .
    cp /outputs/squeezenet.py /home/lambdapack/squeezenet.py
    cp /outputs/index.py /home/lambdapack/index.py
    echo "original size $(du -sh /home/lambdapack | cut -f1)"

    # cleaning libs
    rm -rf external
    find . -type d -name "tests" -exec rm -rf {} +

    # cleaning
    find -name "*.so" | xargs strip
    find -name "*.so.*" | xargs strip
    rm -r pip
    rm -r pip-*
    rm -r wheel
    rm -r wheel-*
    rm easy_install.py
    find . -name \*.pyc -delete
    echo "stripped size $(du -sh /home/lambdapack | cut -f1)"

    # compressing
    zip -FS -r1 /outputs/pack.zip * > /dev/null
    echo "compressed size $(du -sh /outputs/pack.zip | cut -f1)"
}

main () {
    dev_install
    pip_rasterio
    gather_pack
}

main
```

`dev_install` 함수에서는 운영체제에 Python3/pip3등을 설치해 주고, `pip_rasterio` 함수에서는 가상환경에 들어가 tensorflow등 pip로 패키지들을 설치해 주고, `gather_pack` 함수에서는 가상환경에 설치된 패키지들과 `index.py`파일을 한 폴더에 모은 뒤 `pack.zip`파일로 압축해줍니다.

> 중간에 `pip.conf`를 바꾸는 부분을 통해 느린 pip global cdn대신 kakao의 pip 미러서버로 좀 더 패키지들을 빠르게 받을 수 있습니다. 이 방법은 여러분의 pip에도 바로 적용할 수 있습니다.

이 sh 파일을 도커 내에서 실행하기 위해서 다음 명령어를 사용해 실행해주세요.

```sh
docker exec -it lambdapack /bin/bash /outputs/buildPack.sh
```

이 명령어는 `lambdapack`이라는 컨테이너에서 `buildPack.sh`파일을 실행하게 됩니다.

실행하고 나면 약 50MB안팎의 `pack.zip`파일 하나가 생긴것을 볼 수 있습니다.

![]({{site.static_url}}/img/dropbox/Screenshot%202017-12-13%2017.27.11.png)

하지만 앞서 언급한 것처럼, AWS 콘솔에서 'ZIP 파일 올리기'로 한번에 올릴수 있는 압축파일의 용량은 50MB로 제한됩니다. 따라서 이 zip 파일을 s3에 올린 뒤 zip파일의 HTTP주소를 넣어줘야 합니다.

## zip파일 s3에 올리고 AWS Lambda 트리거 만들기 

이제 AWS 콘솔을 볼 때가 되었습니다.

지금까지 작업한 것은 Lambda에 올릴 패키지/코드를 압축한 파일인데요, 이 부분을 약간 수정해 이제 실제로 AWS Lambda의 이벤트를 통해 실행해 봅시다.

![s3에 파일 업로드하기]({{site.static_url}}/img/dropbox/Screenshot%202017-12-13%2017.31.32.png)

S3에 파일을 올린 뒤 파일의 HTTPS주소를 복사해주세요.

![s3의 pack.zip HTTP주소]({{site.static_url}}/img/dropbox/Screenshot%202017-12-13%2017.32.11.png)

여기에서는 `https://s3.ap-northeast-2.amazonaws.com/keras-blog/pack.zip`가 주소가 됩니다.

이제 진짜로 AWS Lambda 함수를 만들어봅시다.

[Lambda 콘솔 함수만들기](https://ap-northeast-2.console.aws.amazon.com/lambda/home?region=ap-northeast-2#/create)에 들어가 "새로 작성"을 선택 후 아래와 같이 내용을 채운 뒤 함수 생성을 눌러주세요.

![]({{site.static_url}}/img/dropbox/Screenshot%202017-12-13%2017.34.39.png)

함수가 생성되고 나면 화면 아래쪽 '함수 코드'에서 다음과 같이 AWS s3에서 업로드를 선택하고 런타임을 Python3.6으로 잡은 뒤 핸들러를 `index.handler`로 바꾸고 S3링크를 넣어준 뒤 '저장'을 눌러주세요.

![]({{site.static_url}}/img/dropbox/Screenshot%202017-12-13%2017.38.45.png)

그 뒤, '기본 설정'에서 메모리를 1500MB 이상으로, 그리고 제한시간은 30초 이상으로 잡아주세요. 저는 테스트를 위해 3000MB/5분으로 잡아주었습니다.

![]({{site.static_url}}/img/dropbox/Screenshot%202017-12-14%2015.22.39.png)

이제 s3에서 파일이 추가될때 자동으로 실행되도록 만들어 주기 위해 다음과 같이 '구성'에서 s3를 선택해주세요.

![트리거에서 s3 선택하기]({{site.static_url}}/img/dropbox/Screenshot%202017-12-13%2017.40.23.png)

이제 화면 아래에 '트리거 구성' 메뉴가 나오면 아래 스크린샷처럼, 파일을 올릴 s3, 그리고 어떤 이벤트(파일 업로드/삭제/복사 등)를 탐지할지 선택하고, 접두사에서 폴더 경로를 `폴더이름/`으로 써 준 뒤, 필요한 경우 접미사(주로 파일 확장자)를 써 주면 됩니다.

![S3 트리거 구성]({{site.static_url}}/img/dropbox/Screenshot%202017-12-14%2009.55.57.png)

이번에는 `keras-blog`라는 버킷 내 `uploads`폴더 내에 어떤 파일이든 생성되기만 하면 모두 람다 함수를 실행시키는 것으로 만들어 본 것입니다.

> NOTE: 접두사/접미사에 `or` 조건은 AWS콘솔에서 지원하지 않습니다.

추가버튼을 누르고 난 뒤 저장을 눌러주면 됩니다.

![함수 저장하기]({{site.static_url}}/img/dropbox/Screenshot%202017-12-14%2010.00.00.png)

트리거가 성공적으로 저장 되었다면 다음과 같은 화면을 볼 수 있을거에요.

![람다 함수 다 만든 모습]({{site.static_url}}/img/dropbox/Screenshot%202017-12-14%2010.01.52.png)

## Lambda 환경변수 추가하기 

우리가 앞서 `index.py`에서 `os.environ`을 통해 시스템의 환경변수를 가져왔습니다. 이를 정상적으로 동작하게 하기 위해서는 `ACCESS_KEY`와 `SECRET_KEY`을 추가해주어야 합니다. 아래 스크린샷처럼 각각 값을 입력하고 저장해주세요.

![환경변수 추가하기]({{site.static_url}}/img/dropbox/Screenshot%202017-12-14%2011.21.21.png)

> 이 키는 AWS `iam`을 통해 가져올 수 있습니다. 해당 iam계정은 s3 R/W권한, DynamoDB write 권한이 있어야 합니다.

## Lambda 내 테스트 돌리기(Optional)

AWS Lambda 콘솔에서도 테스트를 돌릴 수 있습니다.

아래와 같이 event 객체를 만들어 전달하면 실제 이벤트처럼 동작합니다.

![예제 테스트]({{site.static_url}}/img/dropbox/Screenshot%202017-12-14%2015.16.35.png)

```json
{
    "Records": [
        {
            "s3": {
                "bucket": {"name": "keras-blog"},
               "object": {"key": "uploads/kitten.png"}
           }
        }
    ]
}
```

> 유의: 실제로 `keras-blog`버킷 내 `uploads`폴더 내 `kitten.png`파일이 있어야 테스트가 성공합니다! (인터넷의 아무 사진이나 넣어두세요.)

테스트가 성공하면 다음과 같이 `return`된 결과가 json으로 보입니다.

![람다콘솔 테스트 성공]({{site.static_url}}/img/dropbox/Screenshot%202017-12-14%2015.15.44.png)

## 마무리: 파일 업로드하고 DB에 쌓이는지 확인하기

이제 s3에 가서 파일을 업로드 해 봅시다.

![s3에 파일 업로드]({{site.static_url}}/img/dropbox/Screenshot%202017-12-14%2015.19.34.png)

`keras-blog` 버킷 내 `uploads`폴더에 고양이 사진 몇 개를 올려봅시다.

몇초 기다리면 DynamoDB에 다음과 같이 파일 이름과 Predict된 결과가 쌓이는 것을 볼 수 있습니다.

![DynamoDB에 쌓인 결과]({{site.static_url}}/img/dropbox/Screenshot%202017-12-14%2015.20.04.png)

이제 우리는 파일이 1개가 올라가든 1000개가 올라가든 모두 동일한 속도로 결과를 얻을 수 있습니다.
