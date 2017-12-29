---
title: "Direct S3 Upload with Lambda"
date: 2017-12-15
layout: post
categories:
- Python
- AWS
published: true
image: /img/direct_s3_post_upload.png
---

## 들어가며

이전 글인 [AWS Lambda에 Tensorflow/Keras 배포하기](/2017/12/07/Deploy-Tensorflow-Keras-on-AWS-Lambda/)에서 Lambda 함수가 실행되는 트리거는 s3버킷에 파일이 **생성**되는 것이었습니다.

물론 파일을 올릴 수 있는 방법은 여러가지가 있습니다. 아주 단순하게 POST 폼 전송 요청을 받고 `boto3`등을 이용해 서버에서 s3으로 파일을 전송할 수도 있고, 더 단순하게는 AWS s3 콘솔을 이용해 파일을 올리라고 할 수도 있습니다.

하지만 이런 부분에는 약간의 단점이 함께 있습니다.

첫 번째 방법처럼 파일을 수신해 다시 s3에 올린다면 그 과정에서 서버 한대가 상시로 켜져있어야 하고 전송되는 속도 역시 서버에 의해 제약을 받습니다. 한편 두 번째 방법은 가장 단순하지만 제3자에게서 파일을 받기 위해서 AWS 계정(비록 제한된 권한이 있다 하더라도)을 제공한다는 것 자체가 문제가 됩니다.

따라서 이번 글에서는 사용자의 브라우저에서 바로 s3으로 POST 요청을 전송할 수 있도록 만드는 과정을 다룹니다.

## 시나리오

![](/img/dropbox/Screenshot%202017-12-15%2018.15.38.png)

사용자는 아주 일반적인 Form 하나를 보게 됩니다. 여기에서 드래그-드롭 혹은 파일 선택을 이용해 일반적으로 파일을 올리게 됩니다. 물론 이 때 올라가는 주소는 AWS S3의 주소가 됩니다.

하지만 이게 바로 이뤄진다면 문제가 생길 소지가 많습니다. 아무나 s3 버킷에 파일을 올린다면 악의적인 파일이 올라올 수도 있고, 기존의 파일을 덮어쓰기하게 될 수도 있기 때문입니다.

따라서 중간에 s3에 post 요청을 할 수 있도록 **인증(signing)**해주는 서버가 필요합니다. 다만 이 때 서버는 요청별로 응답을 해주면 되기 때문에 AWS Lambda를 이용해 제공할 수 있습니다.

따라서 다음과 같은 형태로 진행이 됩니다.

![전체 처리 과정 모식도](/img/direct_s3_post_upload.png)

S3에 POST 요청을 하기 전 Signing 서버에 업로드하는 파일 정보와 위치등을 보낸 뒤, Lambda에서 해당 POST 요청에 대한 인증 정보가 들어간 header를 반환하면 그 헤더 정보를 담아 실제 S3에 POST 요청을 하는 방식입니다.

만약 Signing하는 과정 없이 업로드가 이뤄진다면 s3 버킷을 누구나 쓸 수 있는 Public Bucket으로 만들어야 하는 위험성이 있습니다. 하지만 이와 같이 제한적 권한을 가진 `iam` 계정을 생성하고 Signing하는 과정을 거친다면 조금 더 안전하게 사용할 수 있습니다.

> **Note:** 이번 글에서는 API Gateway + Lambda 조합으로 Signing서버를 구성하기 때문에 만약 추가적인 인증 과정을 붙인다면 API Gateway단에서 이뤄지는 것이 좋습니다.

## 버킷 만들기 & 권한 설정

> 새로운 버킷은 [https://s3.console.aws.amazon.com/s3/home](https://s3.console.aws.amazon.com/s3/home)에서 추가할 수 있습니다.

새로운 버킷을 하나 만들어주세요. 이번 글에서는 `s3-signature-dev-py3`라는 이름으로 만들어 진행해 보았습니다.

<!-- 그리고 버킷의 권한 -> 버킷 정책으로 들어가 아래와 같이 json 형태로 권한을 설정해 줍시다. 웹을 통해 업로드 가능한 권한을 열어주기 위해 다음과 같이 권한을 설정해 줍시다.

이번에는 버킷 내 `page`폴더에만 '읽기'권한을 열어 사용자들이 접근 할 수 있게 만들어 줍니다.(업로드용 Form 페이지를 이 폴더에 올려줍니다.)

> **Note:** 이번에는 간단하게 구현하기 위해 익명쓰기/읽기 권한을 폴더별로 제한적으로 열어주었지만 만약 여러분이 좀 더 안전하게 버킷을 관리하려면 [AWS Docs: 버킷 정책 예제](https://docs.aws.amazon.com/ko_kr/AmazonS3/latest/dev/example-bucket-policies.html)를 참고해 좀 더 상세한 제한을 걸어주는 것이 좋습니다.

![](/img/dropbox/Screenshot%202017-12-18%2020.42.17.png)

```json
{
    "Version": "2008-10-17",
    "Id": "policy",
    "Statement": [
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
``` -->

<!-- 그리고  -->

버킷에 GET/POST 요청을 하기 위해 CORS 설정을 해줘야 합니다.(`localhost:8000`와 같은 제 3의 URL에서 s3 버킷의 주소로 POST 요청을 날리기 위해서는 CORS 설정이 필수입니다.)

아래 스크린샷과 같이 CORS 설정을 진행해 주세요.

![](/img/dropbox/Screenshot%202017-12-18%2020.55.31.png)

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

> **Note:** 만약 여러분이 여러분의 프론트 서비스에서만 이 요청을 허용하려면 `AllowedOrigin`부분을 여러분이 사용하는 프론트 서비스의 도메인으로 변경해주세요.

이제 s3을 사용할 준비는 마쳤습니다.

## 버킷 액세스 iam 계정 만들기

> 새로운 iam 계정은 [https://console.aws.amazon.com/iam/home?region=ap-northeast-2#/users$new?step=details](https://console.aws.amazon.com/iam/home?region=ap-northeast-2#/users$new?step=details)에서 만들 수 있습니다.

다음으로는 앞서 만들어준 버킷에 액세스를 할 수 있는 `iam` 계정을 만들어야 합니다. 이번에 사용할 유저 이름도 `s3-signature-dev-py3`로 만들어 줍시다. 아래 스크린샷처럼 `Programmatic access`를 위한 사용자를 만들어 줍시다.

![](/img/dropbox/Screenshot%202017-12-18%2021.03.31.png)

우리는 버킷내 `uploads`폴더에 파일을 '업로드만 가능'한, `PutObject`와 `PutObjectAcl`이라는 아주 제한적인 권한을 가진 계정을 만들어 줄 것이기 때문에 다음과 같이 Create Policy를 눌러 json 기반으로 계정 정책을 새로 생성해 줍시다.

![](/img/dropbox/Screenshot%202017-12-18%2021.05.01.png)

새 창이 뜨면 아래와 같이 `arn:aws:s3:::s3-signature-dev-py3/uploads/*` 리소스에 대해 `PutObject`와 `PutObjectAcl`에 대해 Allow를 해 주는 json을 입력하고 저장해줍시다.

![](/img/dropbox/Screenshot%202017-12-18%2021.16.41.png)

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

![](/img/dropbox/Screenshot%202017-12-18%2021.18.22.png)

저장해주고 창을 끈 뒤 이전 페이지로 돌아와 Refresh를 누르면 다음과 같이 앞서 만들어준 Policy가 나오는 것을 볼 수 있습니다. 체크박스에 체크를 누른 뒤 다음을 눌러주세요.

![](/img/dropbox/Screenshot%202017-12-18%2021.20.29.png)

이제 마지막 확인을 눌러주세요.

![](/img/dropbox/Screenshot%202017-12-18%2021.21.35.png)

확인을 누르면 다음과 같이 Access key ID와 Secret access key가 나옵니다. 이 키는 지금만 볼 수 있으니 csv로 받아두거나 따로 기록해 두세요. 그리고 글 아래부분에서 이 키를 사용하게 됩니다.

![](/img/dropbox/Screenshot%202017-12-18%2021.22.05.png)

## Signing Lambda 함수 만들기

이제 POST 요청을 받아 인증을 해줄 AWS Lambda함수를 만들어 줍시다.

아래 코드를 받아 AWS Lambda 새 함수를 만들어주세요. (역시 `s3-signature-dev-py3`라는 이름으로 만들었습니다.)

[Github Gist: index.py](https://gist.github.com/Beomi/ac9d34dbfa9a6bdaf4a0426e8b83b4e3)

![](/img/dropbox/Screenshot%202017-12-18%2020.22.26.png)

이번 함수는 python3의 내장함수만을 이용하기 때문에 따로 zip으로 만들 필요없이 AWS 콘솔 상에서 인라인 코드 편집으로 함수를 생성하는 것이 가능합니다.

아래 스크린샷처럼 `lambda_function.py` 파일을 위의 gist 코드로 덮어씌워주세요. 그리고 `Handler`부분을 `lambda_function.index`로 바꿔 `index`함수를 실행하도록 만들어 주세요. 그리고 저장을 눌러야 입력한 코드가 저장됩니다.

![](/img/dropbox/Screenshot%202017-12-18%2020.25.34.png)

코드를 조금 뜯어보면 아래와 같이 `ACCESS_KEY`와 `SECRET_KEY`를 저장하는 부분이 있습니다.


```python
ACCESS_KEY = os.environ.get('ACCESS_KEY')
SECRET_KEY = os.environ.get('SECRET_KEY')
```

AWS Lambda에서 함수를 실행할 때 아래 환경변수를 가져와 s3 버킷에 액세스하기 때문에 위 두개 값을 아래 스크린샷처럼 채워줍시다. 입력을 마치고 저장을 눌러주면 환경변수가 저장됩니다.

![](/img/dropbox/Screenshot%202017-12-18%2020.32.57.png)

> **Note:** 각 키의 값은 앞서 iam 계정 생성시 만든 값을 넣어주세요!

## API Gateway 연결하기

> API Gateway는 [https://ap-northeast-2.console.aws.amazon.com/apigateway/home?region=ap-northeast-2#/apis/create](https://ap-northeast-2.console.aws.amazon.com/apigateway/home?region=ap-northeast-2#/apis/create)에서 만들 수 있습니다.

이렇게 만들어 준 AWS Lambda 함수는 각각은 아직 외부에서 결과값을 받아올 수 있는 형태가 아닙니다. 람다 함수를 트리거해주고 결과값을 받아오기 위해서는 AWS API Gateway를 통해 웹 URL로 오는 요청에 따라서 람다 함수가 실행되도록 구성해야 합니다. 또한, CORS역시 활성화 해줘야 합니다.

### API Gateway 만들고 Lambda와 연결하기

![](/img/dropbox/Screenshot%202017-12-18%2022.01.23.png)

Resources에서는 Api URL의 하위 URL에 대해 

![](/img/dropbox/Screenshot%202017-12-18%2022.15.35.png)

여기서 새 메소드 중 `POST`를 선택해 줍시다.

![](/img/dropbox/Screenshot%202017-12-18%2022.16.38.png)

메소드에 Lambda 함수를 연결해 주기 위해 다음과 같이 `Lambda Function`을 선택하고 `Proxy`는 체크 해제한 뒤, `Region`은 `ap-northeast-2`(서울)리전을 선택하고, 아까 만들어준 함수 이름을 입력한 뒤 `Save`를 눌러줍시다.

> **Tip:** Lambda Proxy를 활성화 시킬 경우 HTTP 요청이 그대로 들어오는 대신, AWS에서 제공하는 event 객체가 대신 Lambda함수로 넘어가게 됩니다. 우리는 HTTP 요청을 받아 Signing해주는 과정에서 Header와 Body를 유지해야하기 때문에 Proxy를 사용하지 않습니다.

![](/img/dropbox/Screenshot%202017-12-28%2013.24.50.png)

`Save`를 누르면 다음과 같이 API Gateway에 Lambda함수를 실행할 권한을 연결할지 묻는 창이 뜹니다. 가볍게 OK를 눌러줍시다.

![](/img/dropbox/Screenshot%202017-12-28%2013.28.28.png)

연결이 완료되면 API Gateway가 아래 사진처럼 Lambda 함수와 연결 된 것을 볼 수 있습니다.

![](/img/dropbox/Screenshot%202017-12-28%2013.33.11.png)

### CORS 활성화하기 

조금만 더 설정을 해주면 API Gateway를 배포할 수 있게 됩니다. 지금 해줘야 하는 작업이 바로 `CORS` 설정인데요, 우리가 나중에 만들 프론트 페이지의 URL와 s3의 URL이 다르기 때문에 브라우저에서는 보안의 이유로 `origin`이 다른 리소스들에 대해 접근을 제한합니다. 따라서 `CORS`를 활성화 해 타 URL(프론트 URL)에서도 요청을 할 수 있도록 설정해줘야 합니다.

`Actions`에서 `Enable CORS`를 눌러주세요.

![](/img/dropbox/Screenshot%202017-12-28%2013.34.06.png)

다음과 같이 `Access-Control-Allow-Headers`의 값을 `'*'`로 설정한 뒤 Enable CORS 버튼을 눌러 저장해주세요.

![](/img/dropbox/Screenshot%202017-12-28%2015.30.42.png)

다시한번 Confirm을 눌러주시면...

![](/img/dropbox/Screenshot%202017-12-28%2015.33.45.png)

CORS가 활성화되고 Options 메소드가 새로 생기게 됩니다.

![](/img/dropbox/Screenshot%202017-12-28%2015.35.30.png)

이제 API Gateway를 '배포'해야 실제로 사용할 수 있습니다.

### API Gateway 배포하기

API Gateway의 설정을 모두 마치고나서는 배포를 진행해야 합니다. 아래와 같이 `Actions`에서 `Deploy API`를 눌러주세요.

![](/img/dropbox/Screenshot%202017-12-28%2015.39.46.png)

API Gateway는 `Deployment Stage`를 필요로 합니다. `Stage name`을 `live`로 설정하고 `Deploy`를 눌러줍시다.

> **Tip:** `Deployment Stage`는 API Gateway의 URL 뒤 `/stagename`의 형식으로 추가 URL을 지정해줍니다. 이를 통해 API를 개발 버전과 실 서비스 버전을 분리해 제공할 수 있습니다.

![](/img/dropbox/Screenshot%202017-12-28%2015.43.03.png)

배포가 완료되면 아래와 같이 API Gateway를 사용할 수 있는 URL을 받을 수 있습니다.

![](/img/dropbox/Screenshot%202017-12-28%2015.48.42.png)

이번에는 `https://9n2qae2nak.execute-api.ap-northeast-2.amazonaws.com/live`가 Signing Lambda 함수를 실행할 수 있는 API Gateway URL이 됩니다.

## 파일 업로드 프론트 만들기

이제 파일을 업로드할 form이 있는 Static 웹 사이트를 만들어봅시다.

이번 글에서는 이미 만들어진 파일 업로더인 VanillaJS용 [Fine Uploader](https://github.com/FineUploader/fine-uploader)를 이용해 최소한의 업로드만 구현합니다.

> React용 [React Fine Uploader](https://github.com/FineUploader/react-fine-uploader)와 Vue용 [Vue Fine Uploader](https://github.com/FineUploader/vue-fineuploader)도 있습니다.

[https://github.com/Beomi/s3-direct-uploader-demo](https://github.com/Beomi/s3-direct-uploader-demo) 깃헙 레포를 clone받아 `app.js`를 열어 아래 목록을 수정해주세요.

- request/endpoint: 여러분이 사용할 s3 버킷 이름 + .s3.amazonaws.com
- request/accessKey: 앞서 만든 iam 계정의 Access Key
- objectProperties/region: s3 버킷의 리전
- objectProperties/key/prefixPath: s3 버킷 내 올릴 폴더 이름(putObject 권한을 부여한 폴더)
- signature/endpoint: 앞서 만든 AWS Lambda의 API Gateway URL

```js
var uploader = new qq.s3.FineUploader({
    debug: false, // defaults to false
    element: document.getElementById('fine-uploader'),
    request: {
        // S3 Bucket URL
        endpoint: 'https://s3-signature-dev-py3.s3.amazonaws.com', 
        // iam ACCESS KEY
        accessKey: 'AKIAIHUAMKBO27EZQ6RA' 
    },
    objectProperties: {
        region: 'ap-northeast-2',
        key(fileId) {
            var prefixPath = 'uploads'
            var filename = this.getName(fileId)
            return prefixPath + '/' + filename
        }
    },
    signature: {
        // version
        version: 4,
        // AWS API Gate URL
        endpoint: 'https://9n2qae2nak.execute-api.ap-northeast-2.amazonaws.com/live'
    },
    retry: {
        enableAuto: true // defaults to false
    }
});
```

그리고나서 `index.html` 파일을 열어보시면 아래 사진과 같은 업로더가 나오게 됩니다.

> **DEMO:** [https://beomi.github.io/s3-direct-uploader-demo/](https://beomi.github.io/s3-direct-uploader-demo/)

![](/img/dropbox/Screenshot%202017-12-28%2017.59.46.png)

## 맺으며

이제 여러분은 Serverless하게 파일을 s3에 업로드 할 수 있게 됩니다. 권한 관리와 같은 부분은 API Gateway에 접근 가능한 부분에 제약을 걸어 업로드에 제한을 걸어 줄 수도 있습니다.

ec2등을 사용하지 않고도 간단한 signing만 갖춰 s3에 파일을 안전하게 업로드 하는 방식으로 전체 프로세스를 조금씩 Serverless한 구조로 바꾸는 예시였습니다.

## Reference

- [Browser-Based Upload using HTTP POST (Using AWS Signature Version 4)](http://docs.aws.amazon.com/ko_kr/AmazonS3/latest/API/sigv4-post-example.html)

- [How to access HTTP headers using AWS API Gateway and Lambda](https://kennbrodhagen.net/2015/12/02/how-to-access-http-headers-using-aws-api-gateway-and-lambda/)







