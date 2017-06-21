---
title: "Deploy Django to MS Azure with Fabric3"
date: 2017-06-09
layout: post
categories:
- Django
- Fabric
published: true
image: /img/azure.jpg
---

> This guide covers about deploying [DjangoGirls Tutorial](https://tutorial.djangogirls.org/en/) to MS Azure Virtual machine(Ubuntu 16.04 LTS) with Fabric3.

You're probably participant in [DjangoGirls Tutorial Workshop](https://tutorial.djangogirls.org/ko/) and you'll be now on 'deploy' step on it. 

Today we're going to deploy our django project to [Azure](http://azure.com) which is provided with MS.

If you didnt' register your `AzurePass` yet, please precede this guide first: [Register Azure and redeem AzurePass](/2017/06/09/Activate-MS-AzurePass/)

## (If Windows) Using `cmder`

You can't use linux commands like `git` or `ssh` on your `cmd`, so we're going to use great shell program which named `cmder`.

![](https://www.dropbox.com/s/j52a96l0gwln8xd/%EC%8A%A4%ED%81%AC%EB%A6%B0%EC%83%B7%202017-06-18%2010.30.18.png?dl=1)

First, click this link:[cmder.zip](https://github.com/cmderdev/cmder/releases/download/v1.3.2/cmder.zip) to download cmder. (It may take times.)

Second, unzip downloaded `cmder.zip` file. (It'll take some times too.) And then you got this!:

![](/img/azure_fabric/1-folder.PNG)

Execute `cmder.exe` in this folder. If you execute `cmder.exe` as a first time you'll be see Security Warning like this: just click `RUN`.

![](/img/azure_fabric/2-securityWarning.PNG)

And one time more, if you execute cmder for the first time, there will be another warning like this: click first option, "Unblock and continue".

![](/img/azure_fabric/3-UnblockBinaries.PNG)

It'll take some times when you run cmder first time. This wouln't appear next time, so please wait for a moment!

![](/img/azure_fabric/4-firstlook.PNG)

If you see this, you're ready to use `cmder` NOW!

![](/img/azure_fabric/5-final.PNG)


If you're following DjangoGirls Tutorial, you probably made folder named `djangogirls`. Let's get into it.

> `cd` is command to ender the folder! Let's get into `djangogirls` folder with `cd djangogirls`.

Let's start deploy then.

## Deploy Azure Virtual machine

You'll see this screen if you logged in to [Azure Portal](https://portal.azure.com/).

![Azure Portal Dashboard](https://www.dropbox.com/s/0qvl1n1jf37u4kg/%EC%8A%A4%ED%81%AC%EB%A6%B0%EC%83%B7%202017-06-10%2000.07.02.png?dl=1)

Let's make Virtual machine with clicking `VirtualComputer(가상 컴퓨터)` button.

![](https://www.dropbox.com/s/ojzxlu318jvqbz3/%EC%8A%A4%ED%81%AC%EB%A6%B0%EC%83%B7%202017-06-10%2000.10.34.png?dl=1)

Now let's add Virtual machine with '+Add' button.

![](https://www.dropbox.com/s/tdhwj54c7eumzbc/%EC%8A%A4%ED%81%AC%EB%A6%B0%EC%83%B7%202017-06-10%2000.11.19.png?dl=1)

If you click `+ Add` button, you'll see another options which provides many OS. But  we're going to use `Ubuntu Server` today.

![](https://www.dropbox.com/s/dggbbc2bp96xxpv/%EC%8A%A4%ED%81%AC%EB%A6%B0%EC%83%B7%202017-06-10%2000.12.02.png?dl=1)

If you clicked Ubuntu Server there'll be server lists like this: we'll use `Ubuntu Server 16.04 LTS`.

![](https://www.dropbox.com/s/bw34iuto0fr7gbf/%EC%8A%A4%ED%81%AC%EB%A6%B0%EC%83%B7%202017-06-10%2000.13.01.png?dl=1)

Then you'll see `Create` button. Click it!

![](https://www.dropbox.com/s/enyg7lnzq9vu4ah/%EC%8A%A4%ED%81%AC%EB%A6%B0%EC%83%B7%202017-06-10%2000.14.29.png?dl=1)

You'll see configure window when you click `Create` button. Fillout blanks like picture lower.

![](https://www.dropbox.com/s/2qpw0xq9koftras/%EC%8A%A4%ED%81%AC%EB%A6%B0%EC%83%B7%202017-06-10%2000.16.28.png?dl=1)

> Username should be `django` (surelly this is not critical but you may encounter issues.

> You may set your password on your own, but it shoud be longer/equal than 12. Please remember not to reset it later.

> Server location should be Korea Centeral(대한민국 중부).

Now we have to choose server size. We'll setup just one django server so we'll choose `DS1_V2`, the left one.

> Don't worry, you won't be charged :)

![](https://www.dropbox.com/s/9l2m2m2pxcophva/%EC%8A%A4%ED%81%AC%EB%A6%B0%EC%83%B7%202017-06-10%2000.19.53.png?dl=1)

Next step you have to setup storage settings. Just select `Manages Storage` to 'Yes'.

And then click `Firewall` settings. After click on it, you'll see pre-configured setting `SSH (TCP/22)`. We're going to add `HTTP (TCP/80)`

![](https://www.dropbox.com/s/yb6wpuf0or5mswx/%EC%8A%A4%ED%81%AC%EB%A6%B0%EC%83%B7%202017-06-10%2000.22.01.png?dl=1)

Click `+ Inbound Rule add` Button, and fillout blanks like this and click confirm button.

![](https://www.dropbox.com/s/xvnsivtytfn4cav/%EC%8A%A4%ED%81%AC%EB%A6%B0%EC%83%B7%202017-06-10%2000.24.23.png?dl=1)

Now default settings are finished! Just click confirm button.

![](https://www.dropbox.com/s/0ovj58iha5ok4pc/%EC%8A%A4%ED%81%AC%EB%A6%B0%EC%83%B7%202017-06-10%2000.24.54.png?dl=1)

And one more time, click confirm button.

![](https://www.dropbox.com/s/a0iqblorl3w1aor/%EC%8A%A4%ED%81%AC%EB%A6%B0%EC%83%B7%202017-06-10%2000.25.18.png?dl=1)

And lastly, click confirm button more! I know you're tired with confirm button, but this is process of Azure :)

![](https://www.dropbox.com/s/ez199b1djsguakz/%EC%8A%A4%ED%81%AC%EB%A6%B0%EC%83%B7%202017-06-10%2000.25.53.png?dl=1)

Please wait until your server is successfully installed!

![](https://www.dropbox.com/s/hufdkgxu3jps8d4/%EC%8A%A4%ED%81%AC%EB%A6%B0%EC%83%B7%202017-06-10%2000.28.15.png?dl=1)

> Server setup is finished when server's icon changes from  `Creating` to  `Running`.


## Get Azure Server Configurations

You can access to your server info with clicking server icon-which tells `Running`.

![](https://www.dropbox.com/s/78t18t15ow7ae2c/%EC%8A%A4%ED%81%AC%EB%A6%B0%EC%83%B7%202017-06-10%2000.30.25.png?dl=1)

You'll see 

애저에서 가상컴퓨터가 생기면 `공용 IP 주소`라는걸 하나 갖게 된답니다. `ip`라는 것은 서버나 컴퓨터가 인터넷에 접속할 수 있게 해주는 일련의 번호인데요, 우리는 이 `ip`를 통해 우리 장고 프로젝트를 서버에 올리는 작업을 진행할 수 있어요.

지금 화면에 보이는 가상컴퓨터의 ip는 `52.231.30.148`인데요, 이렇게 숫자로만 되어있으면 우리는 기억하기가 어려워요.

그래서 `djangogirls.com`와 같이 사람이 이해하고 외우기도 쉬운 `도메인`을 저 `ip`주소에 붙여줄거에요.

자, 우선 여러분의 가상 컴퓨터의 ip를 복사(Ctrl+C / CMD+C)해두세요!



## 무료 도메인 얻어 가상컴퓨터에 연결하기


`.com`, `.net`와 같이 유명한 도메인은 돈을 주고 사야한답니다.(1년에 만원정도 나가요) 하지만 우리는 오늘 무료 도메인을 연결해 볼 거에요.

우선 [Dot.tk](http://dot.tk/)로 들어오세요.

이 Dot.tk에서는 `.tk` 도메인을 무료로 제공하고 있어요. 우선 `djangogirls-seoul-tutorial`이라는 이름으로 찾아볼게요. 값을 입력하고 `Check Availability`를 눌러주세요!

> 여러분은 여러분이 원하는 주소를 검색해보세요! (ex: myfirstdjango 등등)

![](https://www.dropbox.com/s/4t4j65csac9jrgp/%EC%8A%A4%ED%81%AC%EB%A6%B0%EC%83%B7%202017-06-10%2000.36.35.png?dl=1)

오, 다행히 주소가 남아있어요. 이제 `Get it now!`버튼을 눌러 장바구니에 담아볼게요.

![](https://www.dropbox.com/s/fs7by196twoebu3/%EC%8A%A4%ED%81%AC%EB%A6%B0%EC%83%B7%202017-06-10%2000.38.28.png?dl=1)

장바구니에 담은 도메인을 `Checkout`버튼을 눌러주면 아래 화면으로 넘어올거에요. `Use DNS`버튼을 눌러주신 후에 IP address 칸에 아까 애저 가상컴퓨터의 ip를 입력해주신 후 `Continue`를 눌러주세요.

![](https://www.dropbox.com/s/sn09uyhvpdeapi6/%EC%8A%A4%ED%81%AC%EB%A6%B0%EC%83%B7%202017-06-10%2000.39.27.png?dl=1)

`Continue`를 누르면 로그인 화면이 나와요. 구글이나 페이스북의 소셜 로그인을 이용할 수 있어요!

> 페이스북은 가끔 오류가 나기도 해요. 그럴때는 구글이나 MS Live계정으로 다시한번 시도해주세요.

![](https://www.dropbox.com/s/p8k5u8qcovi9d2y/%EC%8A%A4%ED%81%AC%EB%A6%B0%EC%83%B7%202017-06-10%2000.40.52.png?dl=1)

로그인이 완료되면 아래와 같이 자신의 정보를 입력하는 부분이 나와요. 꼭 다 채울필요는 없어요!

![](https://www.dropbox.com/s/35pg5ktos06hgjq/%EC%8A%A4%ED%81%AC%EB%A6%B0%EC%83%B7%202017-06-10%2000.42.39.png?dl=1)

주문 거래 동의 체크상자를 클릭한 후 계속 버튼을 누르면 주문이 완료된답니다! 좋아요!

![](https://www.dropbox.com/s/whnk0lonj0qj0e4/%EC%8A%A4%ED%81%AC%EB%A6%B0%EC%83%B7%202017-06-10%2000.45.21.png?dl=1)


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


이제 [Fabfile for Django](https://gist.github.com/Beomi/0cc830bd5cda029c277cba648386b28c/archive/57f68d2cb2c466ab7bcf757a22cc47c6004aa98b.zip)를 클릭해 압축파일을 받아 풀어주세요.

안에 `deploy.json`와 `fabfile.py`가 보일거에요. 이 두 파일을 여러분의 장고 폴더(`manage.py`파일이 있는 곳)안에 넣어주세요.

`deploy.json`파일 안에는 우리 서버의 정보를 적어넣을 수 있어요. 

```json
{
  "REPO_URL":"깃헙Repo주소",
  "PROJECT_NAME":"프로젝트폴더(settings.py가있는 폴더)의 이름",
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
fab create_superuer
```

## 짜잔!

여러분은 이제 Azure에 올라간 **진짜** 웹 서비스 하나를 만들었어요! 이제 여러분은 장고로 웹 서비스를 만드는 것의 처음부터 끝까지를 모두 알게되었어요! 축하합니다 :D