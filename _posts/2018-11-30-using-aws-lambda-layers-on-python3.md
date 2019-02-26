---
title: "AWS Lambda Layers로 함수 공통용 Python 패키지 재사용하기"
date: 2018-11-30
layout: post
categories:
- aws
- python
published: true
image: https://d1sr4ybm5bj1wl.cloudfront.net/img/2018-11-30-using-aws-lambda-layers-on-python3.jpg
---

## 들어가며

올해 AWS Re:Invent에서 새로 발표된 기능 중 AWS Lambda에 새로운 전환점을 가져오는 기능이 발표되었습니다. 

바로 [Custom Runtime 지원과 Layers 지원이 추가](https://aws.amazon.com/ko/about-aws/whats-new/2018/11/aws-lambda-now-supports-custom-runtimes-and-layers/)된 것인데요, 
이번 글에서는 두가지 기능 중 "Layers" 기능에 대해 알아봅니다.

## Lambda Layers가 무엇인가요?

사실 아직까지 많은 정보가 나오지는 않았는데요, [Lambda Layers 추가 소개 문서](https://aws.amazon.com/ko/about-aws/whats-new/2018/11/aws-lambda-now-supports-custom-runtimes-and-layers/)를 살펴보면 
어떤 방식으로 동작하는지 대략적인 감을 잡을 수 있습니다.

아래 글은 위 링크 내용 중 Lambda Layers에 대한 간략한 소개 부분입니다.

> Lambda Layers are **a new type of artifact that can contain arbitrary code and data**, and may be referenced by zero, one, or more functions at the same time. Lambda functions in a serverless application typically share common dependencies such as SDKs, frameworks, and now runtimes. With layers, you can centrally **manage common components across multiple functions** enabling better code reuse. To use layers, you simply put your common code in a zip file, and upload it to Lambda as a layer. You then configure your functions to reference it. When a function is invoked, the layer contents become available to your function code. We are also providing a layer which includes the popular NumPy and SciPy scientific libraries for Python. ... Read more about Lambda Layers in the [AWS Lambda documentation](https://docs.aws.amazon.com/lambda/latest/dg/configuration-layers.html).

핵심적인 부분을 **bold** 처리 해 두었는데요, 위 내용은 다음과 같이 요약할 수 있습니다.

> "Lambda에 코드 만들어 올릴 때 매번 패키지(pip 패키지 등) 세트 만들어 올리는거 귀찮았지? 같은 Dependency 가지는 함수라면 코드만 따로 빼고 의존성 패키지는 Layers라는 곳으로 빼서 사용해!"

즉, 굉장히 편리해진 요소가 추가된 것이죠. 그렇다면 Layers는 어떻게 동작할까요?

## 그래서 뭐가 바뀐건가요?

### 기존 Lambda Packaging의 한계 

AWS에 익숙한 분이시라면 이미 아시겠지만 AWS Lambda는 굉장히 많은 제약을 가지고 있습니다. 서버리스라는 인프라 구조적 한계부터 시작해, **코드 용량(현재 max 250MB)의 압박, I/O의 제약(/tmp에만 500MB)**, 그리고 Ram용량(3G)의 한계와 실행시간(15분)의 한계까지 굉장히 많은 한계가 있습니다. 

방금 언급한 부분 중 **코드 용량(현재 max 250MB)의 압박, I/O의 제약(/tmp에만 500MB)**으로 인해 `pip`를 이용한 패키지 설치 등이 불가능하고, 동시에 운영체제에 의존해 빌드가 필요한 패키지 등의 경우는 사용이 굉장히 까다롭기까지 합니다. 그렇다면 지금까지는 어떻게 이 문제를 회피해 왔을까요?

지금까지는 아래 과정을 통해 문제를 피해왔습니다.

- 한 폴더를 지정하고, 해당 폴더 내에 모든 패키지를 넣어본다. (`pip`로 설치한 `site-packages`폴더를 통으로 프로젝트에 넣는다.) 단, 250MB 이내여야 한다.
- 만약 실패할 경우(C의존 라이브러리 등) Docker나 EC2를 이용해 AmazonLinux 운영체제에서 빌드한 뒤 해당 의존성 패키지들을 한 폴더에 같이 넣는다.
- 위 상황에서 압축 해제시 250MB가 넘는다면 strip등을 이용해 필요없는 파일을 제거하거나 파일 용량을 압축하는 등 용량을 줄인다.
- 그래도 용량이 넘친다면 패키지를 반으로 쪼개고, Lambda 함수가 실행될 때 s3에서 두번째 패키지를 다운받아 `/tmp`에 압축을 풀어 사용한다.

사실 AWS Lambda Layers가 추가된 지금도 여전히 위 제약들은 그대로 살아있습니다. ㅠㅠ

하지만 위 과정에서 필요했던 여러 과정을 줄일 수 있게 됩니다. 예를들어 한 함수에서 `requests`라는 라이브러리를 사용하고 있었고, 다른 함수에서도 해당 라이브러리를 사용하려고 한다고 가정해 봅시다. 
기존에는 Lambda 함수를 만들 때 마다 해당 라이브러리 코드와 의존성 모듈들을 소스코드와 함께 묶어 업로드를 진행해야 했습니다. 상당히 귀찮은 일이죠.

그런데 Lambda Layers가 나오면서 이런 이슈가 엄청나게 줄어들었습니다. 그렇다면 Lambda Layers가 대체 어떤 일을 해주기에 일이 줄어든 걸까요?

### Lambda Layers는 어떻게 작동하나요?

[공식 문서: Lambda Layers 설정하기](https://docs.aws.amazon.com/lambda/latest/dg/configuration-layers.html)에서는 Lambda Layers가 아래와 같이 작동한다고 말합니다.

> **Layers are extracted to the /opt directory** in the function execution environment. Each runtime looks for libraries in a different location under /opt, depending on the language. Structure your layer so that function code can access libraries without additional configuration.

가장 중요한 부분은 "Layers가 하나의 '압축 파일'이며, `/opt` 폴더에 압축해제되는 것"입니다. 즉, Layers가 뭔가 특별한 것이 아니라 압축파일 하나를 `/opt` 폴더에 풀어준다는 것 뿐입니다. 이렇게 말만 들으면 기존 방식가 뭐가 다르지? 하는 의문이 생길 수 있습니다. 하지만 앞서 나온 소개와 맞물리며 이야기가 조금 달라집니다.

> Layers let you keep your deployment package small, which makes development easier. You can avoid errors that can occur when you install and package dependencies with your function code. For Node.js, Python, and Ruby functions, **you can develop your function code in the Lambda console as long as you keep your deployment package under 3 MB**.

작년 Amazon이 `c9.io` 서비스를 인수하며 Lambda 서비스 업데이트에 추가되었던 기능 중 하나가 바로 **Lambda 콘솔에서 곧바로 코드 수정이 가능**해졌다는 것입니다. 
하지만 이 방식으로 코드를 수정하려면 해당 Lambda 함수의 패키지 크기가 3MB 이하여야 했다는 점인데요, 
기존 방식으로 모든 의존성 패키지들을 압축해서 사용한다면 3MB는 정말 작고도 작은 크기입니다. 
단순히 typo 하나 수정을 위해서 패키지를 빌드하는 과정을 다시 반복해야 하는 것은 개발자에게 굉장한 고통으로 다가오는 것인데,
용량을 조금 많이 사용하기 위해서 패키징을 했더니 Lambda console에서 코드 수정이 불가능해진 것이죠.

심지어 기존에는 코드와 모듈들을 합쳐서 압축한 zip파일 크기가 50MB가 넘어가는 경우에는 AWS Console상에서 업로드 하는 것도 불가능해서 S3에 올린 뒤 해당 S3의 경로를 Lambda 콘솔에 붙여넣기 해주어야 했습니다. 
(심지어 자동완성도 불가능해서 매번 해당 `s3://~~~`하는 주소를 복사-붙여넣기 해야 했죠!)

그렇다면 Lambda Layers가 등장하면 어떻게 바뀌는 것일까요?

우선 의존성 패키지를 압축하는 것은 동일합니다. 단, 기존에는 **소스코드를 함께 패키징**했다면 이제는 **의존성 모듈만 패키징**하게 된다는 것이 가장 달라지는 점입니다.

이렇게 되면 소스코드는 처음 업로드 할 때만 zip파일로 압축해 업로드하고 이후 수정시에는 AWS Lambda Console에서 곧바로 수정 가능합니다.

## Lambda Layers는 어떻게 사용하나요?

### Lambda 함수로 만들 코드 작성하기

아주아주 간단하고 심플한 크롤링 코드를 Lambda에 올려 사용한다고 가정해봅시다. 해당 코드는 `requests`와 `bs4`라는 모듈을 사용합니다. 
이 블로그를 긁어 `h1`태그 하나의 글자를 가져와봅시다.

```python
import json
import requests
from bs4 import BeautifulSoup as bs

def lambda_handler(event, context):
    # TODO implement
    res = requests.get('https://beomi.github.io')
    soup = bs(res.text, 'html.parser')
    blog_title = soup.select_one('h1').text
    return {
        'statusCode': 200,
        'body': json.dumps(blog_title)
    }
```

로컬에서 `requests`, `bs4`가 설치된 상태에서 `lambda_handler` 함수를 실행시 결과는 다음과 같습니다.

```json
{
  "statusCode": 200,
  "body": "\"Beomi's Tech Blog\""
}
```

하지만 아무런 준비 없이 AWS Lambda 콘솔에서 위 코드를 저장하고 실행하면 아래와 같은 `No module named 'requests'` 에러가 납니다.

```bash
Response:
{
  "errorMessage": "Unable to import module 'lambda_function'"
}

...

Unable to import module 'lambda_function': No module named 'requests'
```

위 에러 메시지는 `requests`라는 모듈을 찾을 수 없다는 파이썬 에러입니다. 당연히 설치되어있지 않기 때문에 에러가 발생합니다. Lambda Layers를 이용해 이 이슈를 해결해봅시다.


### 크롤링 의존 패키지들 Lambda Layers로 만들기 

이제 AWS Lambda Console을 켜 줍시다. Lambda 서비스 항목 중 "계층" 혹은 Layers를 누르고 "계층 생성"을 눌러줍시다.

![]({{site.static_url}}/img/dropbox/2018-11-30%2018.03.49.png)

아래와 같이 새로운 Lambda Layer를 생성하는 창이 뜹니다.

![]({{site.static_url}}/img/dropbox/2018-11-30%2018.13.12.png)

이제 `requests`와 `bs4`가 들어있는 zip 압축파일을 업로드해야 하는데요, 크롤링을 위한 패키지가 아래 Github Repo에 준비되어 있습니다. 아래 Direct Download 링크를 통해 `pack.zip`파일을 받아 업로드 해주세요.

> Github Repo: [https://github.com/Beomi/aws-lambda-py3](https://github.com/Beomi/aws-lambda-py3)
> - `requests` + `bs4` + `lxml` ; [Direct Download](https://media.githubusercontent.com/media/Beomi/aws-lambda-py3/master/requests_bs4_lxml/pack.zip)

그리고 Runtime으로 `python3.6`/`python3.7`를 선택해 줍시다. (여러분이 Layer를 만들때는 해당 Layer가 사용될 환경을 모두 선택해주세요.)

업로드가 성공하면 아래와 같이 새로운 Lambda Layer가 생성됩니다. 참고로 각각의 Layer는 버전별로 수정이 불가능하고 만약 수정이 필요하다면 zip파일을 다시 올리고 새로운 리비전이 생성됩니다.

![]({{site.static_url}}/img/dropbox/2018-11-30%2018.13.59.png)

### Lambda Function 생성 + Layers 붙이기

아래와 같은 방식으로 함수를 만들었다고 가정해 봅시다. 

![]({{site.static_url}}/img/dropbox/2018-11-30%2018.17.49.png)

함수 생성이 성공하면 다음과 같은 화면이 나옵니다. 

![]({{site.static_url}}/img/dropbox/2018-11-30%2018.18.37.png)

아래와 같이 `Layers`를 누르고 `계층 추가`를 눌러줍시다.

![]({{site.static_url}}/img/dropbox/2018-11-30%2018.19.21.png)

계층 추가를 진행시 다음과 같이 '런타임 호환'에서 선택한 뒤 방금 만들어준 Layer의 이름 + 버전(첫 버전이라 1)을 선택하고 연결을 눌러줍시다.

![]({{site.static_url}}/img/dropbox/2018-11-30%2018.22.37.png)

Layer를 추가한 뒤에는 Console의 우측 상단의 저장 버튼을 눌러야만 Lambda Function이 저장됩니다.

이제 Lambda 함수 코드를 수정해봅시다.

![]({{site.static_url}}/img/dropbox/2018-11-30%2018.25.45.png)

기존에는 아래와 같은 샘플 코드가 들어있습니다.

```python
import json

def lambda_handler(event, context):
    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
```

당연히 실행은 잘 되지만, 우리가 원하는 코드는 위에서 사용한 크롤링 코드입니다. 하지만 아래 버전은 제대로 동작하지 않습니다. `No module ~~`이라고 하는 에러가 발생하게 되죠. 파이썬 모듈들을 `import` 해줍시다.

```python
import json
import requests
from bs4 import BeautifulSoup as bs

def lambda_handler(event, context):
    # TODO implement
    res = requests.get('https://beomi.github.io')
    soup = bs(res.text, 'html.parser')
    blog_title = soup.select_one('h1').text
    return {
        'statusCode': 200,
        'body': json.dumps(blog_title)
    }
```

파이썬은 기본적으로 현재 폴더, 그리고 실행하는 파이썬이 참고하는 PYTHON PATH들을 참고해 여러 패키지와 라이브러리를 `import`합니다. 
Lambda Layers가 압축 해제된 `/opt`폴더는 해당 PATH에 들어있지 않아 `import`할 때 Python이 탐색하는 대상에 포함되지 않습니다.
대신, 우리가 방금 다운받은 패키지지 안의 `python` 폴더가 `/opt/python`에 압축이 해제되고 해당 폴더는 `PYTHONPATH` 환경변수 내에 포함되게 됩니다.

이제 다시 더미 테스트를 실행해보면 다음과 같이 결과가 잘 나오는 것을 볼 수 있습니다.

![테스트성공]({{site.static_url}}/img/dropbox/2018-11-30%2018.35.13.png)

## 맺으며

이번 글에서는 굉장히 가벼운 패키지들만 사용했지만 당장 `selenium`을 이용하기 위해 PhantomJS 바이너리를 포함하는 경우 총 패키지 크기가 13MB를 넘어가게 됩니다. 
또한 AWS Lambda의 '250MB' 크기 제약은 여전히 "한 함수의 소스코드 크기 + Layers 크기 합"으로 되어있기 때문에 Layer를 쪼개더라도 총 합이 '250MB'로 걸린다는 점은 아쉽습니다. (얼른 용량을 늘려라 AWS 일해라 AWS)

다만 일상적인 수정이 필요한 경우, 그리고 Proof of concept 같은 상황에서 Lambda 환경을 테스트하기 위해서는 이 글에서 소개한 AWS Lambda Layers를 적극 활용해 보는 것이 좋을 것 같습니다. :)
