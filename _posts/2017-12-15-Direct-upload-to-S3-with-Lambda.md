---
title: "AWS S3에 서버없이 파일 업로드하기 with Lambda"
date: 2017-12-15
layout: post
categories:
- Python
- AWS
- Flask
published: false
image: /img/direct_s3_post_upload.png
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

하지만 이게 바로 이뤄진다면 문제가 생길 소지가 많습니다. 아무나 s3 버킷에 파일을 올린다면 악의적인 파일이 올라올 수도 있고, 기존의 파일을 덮어쓰기하게 될 수도 있기 때문입니다.

따라서 중간에 s3에 post 요청을 할 수 있도록 **인증(signing)**해주는 서버가 필요합니다. 다만 이 때 서버는 요청별로 응답을 해주면 되기 때문에 AWS Lambda를 이용해 제공할 수 있습니다.

따라서 다음과 같은 형태로 진행이 됩니다.

![전체 처리 과정 모식도](/img/direct_s3_post_upload.png)

S3에 POST 요청을 하기 전 Signing 서버에 업로드하는 파일 정보와 위치등을 보낸 뒤, Lambda에서 해당 POST 요청에 대한 인증 정보가 들어간 header를 반환하면 그 헤더 정보를 담아 실제 S3에 POST 요청을 하는 방식입니다.

## 버킷 만들기 & 권한 설정

> 새로운 버킷은 [https://s3.console.aws.amazon.com/s3/home](https://s3.console.aws.amazon.com/s3/home)에서 추가할 수 있습니다.

새로운 버킷을 하나 만들어주세요. 이번 글에서는 `s3-signature-dev-py3`라는 이름으로 만들어 진행해 보았습니다.

그리고 버킷의 권한 -> 버킷 정책으로 들어가 아래와 같이 json 형태로 권한을 설정해 줍시다. 웹을 통해 업로드 가능한 권한을 열어주기 위해 다음과 같이 권한을 설정해 줍시다.

이번에는 버킷 내 `uploads`폴더에만 '쓰기' 권한을 열고, `page`폴더에만 '읽기'권한을 열어 사용자들이 접근 할 수 있게 만들어 줍니다.(즉, 업로드 자체는 가능하지만 파일에 액세스 하는 것은 불가능해집니다.)

> NOTE: 이번에는 간단하게 구현하기 위해 익명쓰기/읽기 권한을 폴더별로 제한적으로 열어주었지만 만약 여러분이 좀 더 안전하게 버킷을 관리하려면 [AWS Docs: 버킷 정책 예제](https://docs.aws.amazon.com/ko_kr/AmazonS3/latest/dev/example-bucket-policies.html)를 참고해 좀 더 상세한 제한을 걸어주는 것이 좋습니다.

![](https://www.dropbox.com/s/yld0mvute7usw3g/Screenshot%202017-12-18%2020.42.17.png?dl=1)

```json
{
    "Version": "2008-10-17",
    "Id": "policy",
    "Statement": [
        {
            "Sid": "allow-public-put",
            "Effect": "Allow",
            "Principal": {
                "AWS": "*"
            },
            "Action": "s3:PutObject",
            "Resource": "arn:aws:s3:::s3-signature-dev-py3/uploads/*"
        },
        {
            "Sid": "allow-public-get",
            "Effect": "Allow",
            "Principal": {
                "AWS": "*"
            },
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::s3-signature-dev-py3/page/*"
        }
    ]
}
```

이처럼 버킷을 만들고 s3에 `uploads`폴더와 `page`폴더를 각각 만들어 줍시다.

그리고 버킷에 GET/POST 요청을 하기 위해 CORS 설정을 추가적으로 해줘야 합니다.(`localhost:8000`에서 s3 버킷의 주소로 POST 요청을 날리기 위해서는 CORS 설정이 필수입니다.)

아래 스크린샷과 같이 CORS 설정을 진행해 주세요.

![](https://www.dropbox.com/s/4kjybjuc78xp78q/Screenshot%202017-12-18%2020.55.31.png?dl=1)

```xml
<CORSConfiguration>
    <CORSRule>
        <AllowedOrigin>*</AllowedOrigin>
        <AllowedMethod>GET</AllowedMethod>
        <MaxAgeSeconds>3000</MaxAgeSeconds>
        <AllowedHeader>Authorization</AllowedHeader>
    </CORSRule>
    <CORSRule>
        <AllowedOrigin>*</AllowedOrigin>
        <AllowedMethod>POST</AllowedMethod>
        <MaxAgeSeconds>3000</MaxAgeSeconds>
        <AllowedHeader>Authorization</AllowedHeader>
    </CORSRule>
</CORSConfiguration>
```

이처럼 구성해주면 모든 도메인(*)에서 요청한 GET/POST 요청을 정상적인 크로스-도메인 요청으로 받아들입니다.

> NOTE: 만약 여러분이 여러분의 프론트 서비스에서만 이 요청을 허용하려면 `AllowedOrigin`부분을 여러분이 사용하는 프론트 서비스의 도메인으로 변경해주세요.

이제 s3을 사용할 준비는 마쳤습니다.

## 버킷 액세스 iam 계정 만들기

> 새로운 iam 계정은 [https://console.aws.amazon.com/iam/home?region=ap-northeast-2#/users$new?step=details](https://console.aws.amazon.com/iam/home?region=ap-northeast-2#/users$new?step=details)에서 만들 수 있습니다.

다음으로는 앞서 만들어준 버킷에 액세스를 할 수 있는 `iam` 계정을 만들어야 합니다. 이번에 사용할 유저 이름도 `s3-signature-dev-py3`로 만들어 줍시다. 아래 스크린샷처럼 `Programmatic access`를 위한 사용자를 만들어 줍시다.

![](https://www.dropbox.com/s/skrihsk85zn1zkf/Screenshot%202017-12-18%2021.03.31.png?dl=1)

우리는 버킷내 폴더에 `PutObject`와 `PutObjectAcl`이라는 아주 제한적인 권한을 가진 계정을 만들어 줄 것이기 때문에 다음과 같이 Create Policy를 눌러 json 기반으로 계정 정책을 새로 생성해 줍시다.

![](https://www.dropbox.com/s/kxyaprtybbawkls/Screenshot%202017-12-18%2021.05.01.png?dl=1)

새 창이 뜨면 아래와 같이 `arn:aws:s3:::s3-signature-dev-py3/uploads/*` 리소스에 대해 `PutObject`와 `PutObjectAcl`에 대해 Allow를 해 주는 json을 입력하고 저장해줍시다.

![](https://www.dropbox.com/s/c6ezskeuw4f02eu/Screenshot%202017-12-18%2021.16.41.png?dl=1)

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "s3UploadsGrant",
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:PutObjectAcl"
            ],
            "Resource": [
                "arn:aws:s3:::s3-signature-dev-py3/uploads/*"
            ]
        }
    ]
}
```

이제 policy의 name을 입력하고 저장해줍시다.

![](https://www.dropbox.com/s/rbnvcdvpt9m0ym8/Screenshot%202017-12-18%2021.18.22.png?dl=1)

저장해주고 창을 끈 뒤 이전 페이지로 돌아와 Refresh를 누르면 다음과 같이 앞서 만들어준 Policy가 나오는 것을 볼 수 있습니다. 체크박스에 체크를 누른 뒤 다음을 눌러주세요.

![](https://www.dropbox.com/s/o42a2ulucjreu8z/Screenshot%202017-12-18%2021.20.29.png?dl=1)

이제 마지막 확인을 눌러주세요.

![](https://www.dropbox.com/s/as39msuonxqns8p/Screenshot%202017-12-18%2021.21.35.png?dl=1)

확인을 누르면 다음과 같이 Access key ID와 Secret access key가 나옵니다. 이 키는 지금만 볼 수 있으니 csv로 받아두거나 따로 기록해 두세요. 그리고 글 아래부분에서 이 키를 사용하게 됩니다.

![](https://www.dropbox.com/s/tzapi4x7t7uiiuv/Screenshot%202017-12-18%2021.22.05.png?dl=1)

## Signing Lambda 함수 만들기

이제 POST 요청을 받아 인증을 해줄 AWS Lambda함수를 만들어 줍시다.

아래 코드를 받아 AWS Lambda 새 함수를 만들어주세요. (역시 `s3-signature-dev-py3`라는 이름으로 만들었습니다.)

[Github Gist: index.py](https://gist.github.com/Beomi/ac9d34dbfa9a6bdaf4a0426e8b83b4e3)

![](https://www.dropbox.com/s/g7r4wulcsy46f0u/Screenshot%202017-12-18%2020.22.26.png?dl=1)

이번 함수는 python3의 내장함수만을 이용하기 때문에 따로 zip으로 만들 필요없이 AWS 콘솔 상에서 인라인 코드 편집으로 함수를 생성하는 것이 가능합니다.

아래 스크린샷처럼 `lambda_function.py` 파일을 위의 gist 코드로 덮어씌워주세요. 그리고 `Handler`부분을 `lambda_function.index`로 바꿔 `index`함수를 실행하도록 만들어 주세요. 그리고 저장을 눌러야 입력한 코드가 저장됩니다.

![](https://www.dropbox.com/s/4hzsjxptcxqn4hg/Screenshot%202017-12-18%2020.25.34.png?dl=1)

코드를 조금 뜯어보면 아래와 같이 `ACCESS_KEY`와 `SECRET_KEY`를 저장하는 부분이 있습니다.


```python
ACCESS_KEY = os.environ.get('ACCESS_KEY')
SECRET_KEY = os.environ.get('SECRET_KEY')
```

AWS Lambda에서 함수를 실행할 때 아래 환경변수를 가져와 s3 버킷에 액세스하기 때문에 위 두개 값을 아래 스크린샷처럼 채워줍시다. 입력을 마치고 저장을 눌러주면 환경변수가 저장됩니다.

![](https://www.dropbox.com/s/m6cegtxdp1mcx7d/Screenshot%202017-12-18%2020.32.57.png?dl=1)

> NOTE: 각 키의 값은 앞서 iam 계정 생성시 만든 값을 넣어주세요!

## API Gateway 연결하기

> API Gateway는 [https://ap-northeast-2.console.aws.amazon.com/apigateway/home?region=ap-northeast-2#/apis/create](https://ap-northeast-2.console.aws.amazon.com/apigateway/home?region=ap-northeast-2#/apis/create)에서 만들 수 있습니다.

이렇게 만들어 준 AWS Lambda 함수는 각각은 아직 외부에서 결과값을 받아올 수 있는 형태가 아닙니다. 람다 함수를 트리거해주고 결과값을 받아오기 위해서는 AWS API Gateway를 통해 웹 URL로 오는 요청에 따라서 람다 함수가 실행되도록 구성해야 합니다. 또한, CORS역시 활성화 해줘야 합니다.

![](https://www.dropbox.com/s/7rsqctl80du404a/Screenshot%202017-12-18%2022.01.23.png?dl=1)

Resources에서는 Api URL의 하위 URL에 대해 

![](https://www.dropbox.com/s/e1ucid2stzl5ulv/Screenshot%202017-12-18%2022.15.35.png?dl=1)

여기서 새 메소드 중 `POST`를 선택해 줍시다.

![](https://www.dropbox.com/s/oq93c4oyl1v3561/Screenshot%202017-12-18%2022.16.38.png?dl=1)

## 파일 업로드 프론트 만들기

이번 글에서는 이미 만들어진 파일 업로더인 

## Reference

- [Browser-Based Upload using HTTP POST (Using AWS Signature Version 4)](http://docs.aws.amazon.com/ko_kr/AmazonS3/latest/API/sigv4-post-example.html)

- [How to access HTTP headers using AWS API Gateway and Lambda](https://kennbrodhagen.net/2015/12/02/how-to-access-http-headers-using-aws-api-gateway-and-lambda/)







