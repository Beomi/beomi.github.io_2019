---
title: "Django MS Azure에 Fabric으로 배포하기"
date: 2017-06-09
layout: post
categories:
- Django
- Fabric
published: true
image: https://beomi-tech-blog.s3.ap-northeast-2.amazonaws.com/img/azure.jpg
---

> If you looking for English version, goto [Deploy Django to MS Azure with Fabric3](/2017/06/10/Deploy-Django-to-MS-Azure-EN/).

> 이번 가이드에서는 [DjangoGirls Tutorial](https://tutorial.djangogirls.org/ko/)를 Fabric으로 Azure 가상 컴퓨터(Ubuntu16.04LTS)에 올리는 과정을 다룹니다.

지금 이 글을 읽고 있는 분들은 아마 장고걸즈 워크숍에 참가해 [DjangoGirls Tutorial](https://tutorial.djangogirls.org/ko/)을 따라가다 이제 `배포`를 해볼 단계에 도착하셨을거에요.

오늘 우리가 만들어본(만들고 있는) Django 프로젝트를 MS가 서비스하는 [Azure(애저)](http://azure.com)에 배포해보는 시간을 가져볼거에요.

만약 여러분이 `AzurePass`를 아직 계정에 등록하지 않았다면, [Azure 가입하고 AzurePass 등록하기](/2017/06/21/Activate-MS-AzurePass/)를 먼저 진행해 주세요.

## (윈도우의 경우) `cmder` 설치하기

윈도우에서는 `git`와 `ssh`등의 명령어를 `cmd`에서 바로 사용할 수 없어요. 그래서 우리는 `cmder`라는 멋진 프로그램을 사용할 거에요.

![]({{site.static_url}}/img/dropbox/2017-06-18%2010.30.18.png)

우선 [cmder.zip](https://github.com/cmderdev/cmder/releases/download/v1.3.2/cmder.zip)을 클릭해 cmder를 받아주세요. (84MB정도라 시간이 조금 걸릴거에요.)

다운받은 `cmder.zip` 파일의 압축을 풀어주세요.(이것도 시간이 조금 걸릴거에요.) 그러면 다음과 같은 내용이 보일거에요. 

![]({{site.static_url}}/img/azure_fabric/1-folder.PNG)

여기 있는 `cmder.exe` 파일을 실행해주세요. 실행하면 아래와 같은 Security Warning이 뜰 수 있어요. `RUN`을 눌러주세요.

![]({{site.static_url}}/img/azure_fabric/2-securityWarning.PNG)

만약 여러분이 cmder를 처음 실행하신다면 아래와 같은 워닝이 뜰거에요. 제일 첫번째 옵션인 "Unblock and continue"를 눌러주세요.

![]({{site.static_url}}/img/azure_fabric/3-UnblockBinaries.PNG)

첫 실행시 아래 화면에서 약간 시간이 걸릴 수 있어요. 다음번 실행부터는 뜨지 않을테니 잠시만 기다려주세요!

![]({{site.static_url}}/img/azure_fabric/4-firstlook.PNG)

아래 화면이 뜨면 여러분이 멋진 cmder를 쓸 준비를 마친거랍니다!

![]({{site.static_url}}/img/azure_fabric/5-final.PNG)

장고걸즈 튜토리얼을 따라오는 중이시라면 `djangogirls`라는 폴더를 만드셨을거에요.

> 폴더로 이동하는 명령어가 `cd`입니다! `cd djangogirls`라고 입력해주세요.

이제 배포를 진행해볼게요.

## Azure 가상컴퓨터 만들기


[Azure Portal](https://portal.azure.com/)에 들어가 로그인 하시면 아래와 같은 화면을 볼 수 있습니다.

![Azure Portal 초기 대시보드]({{site.static_url}}/img/dropbox/2017-06-10%2000.07.02.png)

이제 대시보드 왼쪽의 메뉴에서 `가상 컴퓨터`를 눌러보시면 아래와 같은 화면이 나옵니다.

![]({{site.static_url}}/img/dropbox/2017-06-10%2000.10.34.png)

이제 가상 컴퓨터를 추가해봅시다.

![]({{site.static_url}}/img/dropbox/2017-06-10%2000.11.19.png)

`+ 추가` 버튼을 눌러주시면 아래와 같은 수많은 선택지가 나오는데요, 우리는 그 중에서 `Ubuntu Server`(우분투 서버)를 사용할거랍니다. `Ubuntu Server`를 클릭해주세요.

![]({{site.static_url}}/img/dropbox/2017-06-10%2000.12.02.png)

우분투 서버를 클릭하면 아래와 같이 서버 버전들이 나옵니다. 우리는 오늘 `Ubuntu Server 16.04 LTS`를 사용할거에요.

![]({{site.static_url}}/img/dropbox/2017-06-10%2000.13.01.png)

우분투 서버 16.04를 선택하고 나면 아래와 같이 `만들기` 버튼이 나올거에요. 버튼을 눌러주세요.

![]({{site.static_url}}/img/dropbox/2017-06-10%2000.14.29.png)

만들기 버튼을 누르면 아래 사진처럼 기본 사항을 설정하는 창이 나올거에요. 내용을 화면 사진 그대로 채워주세요.

![]({{site.static_url}}/img/dropbox/2017-06-10%2000.16.28.png)

> 사용자 이름은 가이드 다음부분에서 이용할 `django`로 하셔야 합니다.

> 암호는 각자 사용하는 암호를 입력하시면 되는데요, 12자리 이상을 요구하기 때문에 약간 어려우실 수 있어요!

> 위치는 대한민국 중부/남부로 해주세요. (안되는 경우 아시아 남동부로 해주세요!)

이제 서버의 크기를 골라야 하는데요, 오늘 우리는 장고 서버만을 띄울 것이기 때문에 가장 왼쪽에 있는 `DS1_V2`를 이용할거에요.

> AzurePass를 등록하면 돈을 지불하지 않아도 되니 걱정하지 마세요!

![]({{site.static_url}}/img/dropbox/2017-06-10%2000.19.53.png)

이제 다음으로 넘어가면 저장소 설정을 해야 해요. 이부분에서는 '관리 디스크 사용'을 '예'로 클릭해주세요.

그 다음으로는 아래쪽의 `네트워크 보안 그룹(방화벽)`을 클릭해 주세요. 클릭하시면 아래와 같이 `SSH (TCP/22)`만 인바운드 규칙에 들어가 있는 것을 확인할 수 있어요. 우리는 여기서 `HTTP (TCP/80)`을 추가해 줄 거에요.

![]({{site.static_url}}/img/dropbox/2017-06-10%2000.22.01.png)

`+ 인바운드 규칙 추가` 버튼을 눌러주시고 사진과 같이 칸을 채워주시고 확인 버튼을 눌러주세요.

![]({{site.static_url}}/img/dropbox/2017-06-10%2000.24.23.png)

이제 설정이 모두 끝났어요! 아래쪽의 `확인`버튼을 눌러주세요.

![]({{site.static_url}}/img/dropbox/2017-06-10%2000.24.54.png)

다시 한번 확인 버튼을 눌러주세요.

![]({{site.static_url}}/img/dropbox/2017-06-10%2000.25.18.png)

이제 정말로 다음 `확인`버튼만 누르면 서버 설치가 끝나요!

![]({{site.static_url}}/img/dropbox/2017-06-10%2000.25.53.png)

이제 조금만 기다려주시면 서버 설치가 끝난답니다!

![]({{site.static_url}}/img/dropbox/2017-06-10%2000.28.15.png)

> 아이콘의 설명이 `Creating`에서 `Running`으로 바뀌면 설치가 끝난거에요.



## Azure 설정 확인하기


Running으로 바뀐 아이콘을 클릭해주시면 아래 화면으로 들어올 수 있어요.

![]({{site.static_url}}/img/dropbox/2017-06-10%2000.30.25.png)

애저에서 가상컴퓨터가 생기면 `공용 IP 주소`라는걸 하나 갖게 된답니다. `ip`라는 것은 서버나 컴퓨터가 인터넷에 접속할 수 있게 해주는 일련의 번호인데요, 우리는 이 `ip`를 통해 우리 장고 프로젝트를 서버에 올리는 작업을 진행할 수 있어요.

지금 화면에 보이는 가상컴퓨터의 ip는 `52.231.30.148`인데요, 이렇게 숫자로만 되어있으면 우리는 기억하기가 어려워요.

그래서 `djangogirls.com`와 같이 사람이 이해하고 외우기도 쉬운 `도메인`을 저 `ip`주소에 붙여줄거에요.

자, 우선 여러분의 가상 컴퓨터의 ip를 복사(Ctrl+C / CMD+C)해두세요!



## 무료 도메인 얻어 가상컴퓨터에 연결하기


`.com`, `.net`와 같이 유명한 도메인은 돈을 주고 사야한답니다.(1년에 만원정도 나가요) 하지만 우리는 오늘 무료 도메인을 연결해 볼 거에요.

우선 [Dot.tk](http://dot.tk/)로 들어오세요.

이 Dot.tk에서는 `.tk` 도메인을 무료로 제공하고 있어요. 우선 `djangogirls-seoul-tutorial`이라는 이름으로 찾아볼게요. 값을 입력하고 `Check Availability`를 눌러주세요!

> 여러분은 여러분이 원하는 주소를 검색해보세요! (ex: myfirstdjango 등등)

![]({{site.static_url}}/img/dropbox/2017-06-10%2000.36.35.png)

오, 다행히 주소가 남아있어요. 이제 `Get it now!`버튼을 눌러 장바구니에 담아볼게요.

![]({{site.static_url}}/img/dropbox/2017-06-10%2000.38.28.png)

장바구니에 담은 도메인을 `Checkout`버튼을 눌러주면 아래 화면으로 넘어올거에요. `Use DNS`버튼을 눌러주신 후에 IP address 칸에 아까 애저 가상컴퓨터의 ip를 입력해주신 후 `Continue`를 눌러주세요.

![]({{site.static_url}}/img/dropbox/2017-06-10%2000.39.27.png)

`Continue`를 누르면 로그인 화면이 나와요. 구글이나 페이스북의 소셜 로그인을 이용할 수 있어요!

> 페이스북은 가끔 오류가 나기도 해요. 그럴때는 구글이나 MS Live계정으로 다시한번 시도해주세요.

![]({{site.static_url}}/img/dropbox/2017-06-10%2000.40.52.png)

로그인이 완료되면 아래와 같이 자신의 정보를 입력하는 부분이 나와요. 꼭 다 채울필요는 없어요!

![]({{site.static_url}}/img/dropbox/2017-06-10%2000.42.39.png)

주문 거래 동의 체크상자를 클릭한 후 계속 버튼을 누르면 주문이 완료된답니다! 좋아요!

![]({{site.static_url}}/img/dropbox/2017-06-10%2000.45.21.png)


## Fabric3 설치하기


이제 여러분의 서버는 `여러분이입력한이름.tk`라는 인터넷 주소로 연결되었어요.

하지만 아직 여러분의 서버에는 아무것도 설치되어있지 않아요. 물론 장고도 설치되어있지 않아요.

이제 `Fabric3`이라는 멋진 자동화 도구를 통해 명령어 한 줄로(마치 startapp처럼) 진짜 서버에 배포하는 멋진 작업을 해볼거에요!

우선 여러분의 가상환경에 `fabric3`을 설치해줘야 해요. `fabric3`은 아래 명령어를 통해 설치할 수 있어요.

> `fabric`이 아니라 `fabric3`입니다! 3을 빼먹지 마세요. 그냥 `fabric`은 파이썬2용이랍니다.

```sh
pip install fabric3
```

## `deploy.json` 수정하기


이제 [Fabfile for Django](https://gist.github.com/Beomi/0cc830bd5cda029c277cba648386b28c/archive/0152df8617a63c6678b7b64c54892dc5b4ce19d8.zip)를 클릭해 압축파일을 받아 풀어주세요.

안에 `deploy.json`와 `fabfile.py`가 보일거에요. 이 두 파일을 여러분의 장고 폴더(`manage.py`파일이 있는 곳)안에 넣어주세요.

`deploy.json`파일 안에는 우리 서버의 정보를 적어넣을 수 있어요. 

```json
{
  "REPO_URL":"깃헙Repo주소",
  "PROJECT_NAME":"프로젝트폴더(settings.py가있는 폴더)의 이름(ex: mysite)",
  "REMOTE_HOST":"여러분이 만든 도메인주소(ex: djangogirls-seoul-tutorial.tk )",
  "REMOTE_USER":"django",
  "STATIC_ROOT":"static",
  "STATIC_URL":"static",
  "MEDIA_ROOT":"media"
}
```

파일에 있는 `REPO_URL`, `PROJECT_NAME`, `REMOTE_HOST` 부분을 채워주세요. 나머지 값은 우리가 따라한 튜토리얼에서 이미 설정되어있어요.

> 모든 값은 "큰 따옴표" 안에 들어가야 한다는 것을 주의하세요!

## Fabric으로 서버에 올리기

Fabric을 사용하기 위한 명령어는 `fab`이라는 명령어입니다. 이 `fab`뒤에 `new_server`, `deploy`, `createsuperuser`등을 덧붙여 실제로 원격 서버에 명령을 내리는거에요.

서버에 처음 올릴 때는 `fab new_server` 명령어를 이용하세요. 파이썬3 설치부터 Apache2설치와 `mod_wsgi`설치까지 완료해준답니다. 

```sh
fab new_server
```

만약 여러분이 장고 소스를 수정(커밋&푸시)후 서버에 올리고 싶으시다면 `fab deploy` 명령어를 이용하세요. 장고 앱을 새로 실행해주고 `manage.py migrate`, `manage.py collectstaticfiles`등의 명령을 서버에 실행해 준답니다.

```sh
fab deploy
```

우리가 진행하는 튜토리얼에서는 슈퍼유저 만들기 항목이 있어요. 여러분의 컴퓨터에서는 `manage.py createsuperuser`를 통해 만들었지만 서버에 띄운 장고에 슈퍼유저를 만들어 주려면 `fab create_superuser`를 이용해주세요.

```sh
fab create_superuser
```

## 짜잔!

여러분은 이제 Azure에 올라간 **진짜** 웹 서비스 하나를 만들었어요! 이제 여러분은 장고로 웹 서비스를 만드는 것의 처음부터 끝까지를 모두 알게되었어요! 축하합니다 :D