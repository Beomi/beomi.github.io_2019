---
title: '[DjangoTDDStudy] #01: 개발환경 세팅하기(Selenium / ChromeDriver)'
date: 2016-12-27
layout: post
categories:
- DjangoTDDStudy
- Python
image: https://beomi-tech-blog.s3.ap-northeast-2.amazonaws.com/img/old_post/big-logo.png
---


# Web을 직접 테스트한다고?

웹 서비스를 개발하는 과정에서 꼭 필요한 것이 있다. 바로 실제로 기능이 동작하는지 테스트 하는 것.
이 테스트를 개발자가 직접 할 수도 있고, 혹은 전문적으로 테스트만 진행하는 QA팀에서 진행할 수도 있다.
하지만 위의 두 방법은 '사람이 직접 해야한다'는 공통점이 있다. 이걸 자동화 할 수 있다면 어떨까?

## Selenium 설치하기

Selenium은 위의 질문에 대한 답변을 준다. 사람이 하기 귀찮은 부분을 자동화!

![]({{site.static_url}}/img/dropbox/2016-12-27%2001.19.12.png)

우선 Selenium을 설치해주자.
(단, Python3가 설치되어있다는 상황을 가정하며, Virtualenv / Pyvenv등의 가상환경 사용을 권장한다. 이 게시글에서는 tdd_study라는 이름의 가상환경을 이용한다.)

```sh
$ pip install selenium
```

PIP가 설치되어있다면 위 명령어 한줄만으로 Selenium이 설치된다.
Selenium의 설치가 완료되었다면, 우선 ChromeDriver를 받아준다.

## ChromeDriver 설치하기

Selenium은 기본적으로 Firefox 드라이버를 내장하고있다. 이 'Driver'들은 시스템에 설치된 브라우저들을 자동으로 동작하게 하는 API를 내장하고 있고, 우리는 각 브라우저별 드라이버를 다운받아 쉽게 이용할 수 있다.

현재 Selenium은 대다수의 모던 웹브라우저들(Chrome, Firefox, IE, Edge, Phantomjs, etc.)을 지원하고 있기 때문에, 일상적으로 사용하는 크롬드라이버를 사용하기로 했다.
(만약 Headless Browser를 이용해야 한다면 [Phantomjs](http://phantomjs.org/)를 이용해보자.)

크롬드라이버는 [크로미움의 ChromeDriver](https://sites.google.com/a/chromium.org/chromedriver/downloads)에서 최신 버전으로 받을 수 있고, 이번 스터디에서는 Chrome v54에서 v56까지를 지원하는 ChromeDriver 2.27버전을 이용하려 한다.

크롬드라이버는 어떤 파일을 설치하는 것이 아니라, Binary가 내장되어있는 하나의 실행파일이라고 보면 된다.

만약 MAC OS나 Linux계열을 사용한다면, 크롬드라이버를 받은 후 그 파일을 PATH에 등록해 주자.

예시)
위 사이트에서 받은 파일의 이름이 chromedriver 이고 받은 경로가 
/Users/beomi/bin 이라면,
사용하는 쉘(bash / zsh등)의 RC파일(유저 홈 디렉토리의 .bashrc / .zshrc)의 제일 아래에

```
export PATH=${PATH}:~/bin
```

위의 코드를 적고 저장한 후, 쉘을 재실행해준다.(터미널을 껐다가 켜주자.)

이렇게 하고나면, 아래 실습시 크롬드라이버의 위치를 지정하지 않고 파일 이름만으로 이용 할 수 있다는 장점이 있다.

## Django 설치하기

![]({{site.static_url}}/img/dropbox/2016-12-27%2001.20.45.png)

Django는 앞으로 우리가 스터디에 사용할 WebFramework다.

```sh
$ pip install django
```

위 명령어로 역시 쉽게 설치 가능하다.
(2016.12.27기준 1.10.4가 최신버전이며, 1.10.x버전으로 스터디를 진행할 예정이다.)

pip로 Django가 설치되고 나면 django-admin 이라는 명령어를 쉘에서 사용할 수 있다.

# 실습

### 0. 설치 잘 되었는지 확인해 보기

쉘에서

```
$ pip list --format=columns
```

라는 명령어를 쳤을 때 아래 스샷과 같이 Django와 selenium이 보인다면 정상적으로 설치가 진행 된 것이다.

![]({{site.static_url}}/img/dropbox/2016-12-27%2001.22.02.png)

설치가 잘 되었다면 다음으로 진행해 보자.

### 1. Selenium 이용해보기

```py
from selenium import webdriver

browser = webdriver.Chrome('chromedriver')
# chromedriver가 Python파일과 같은 위치에 있거나, 혹은 OS의 PATH에 등록되어 쉘에서 실행 가능한 경우 위와같이 한다.
# 혹은 browser = webdriver.Chrome('/path/to/chromedriver')의 절대경로로 해도 된다.
browser.get('http://localhost:8000')

assert 'Django' in browser.title
```

위 코드는 Chrome 브라우저를 작동시키는 WebDriver를 이용해 새 크롬 창을 띄우고 `http://localhost:8000`이라는 url로 들어간 후 브라우저의 title에 'Django'라는 글자가 들어가 있는지를 확인(Assert)해준다.

현재 상황에서는 django웹서버를 실행하지 않았기 때문에 당연하게도 AssertionError가 난다.

### 2. Django 서버 띄우기

이제 Django서버를 띄워보자. 

Django는 django-admin이라는 명령어를 통해 기본적인 뼈대가 구성된 프로젝트 폴더 하나를 만들어 준다.

```
$ django-admin startproject tdd_study_proj
```

위 명령어를 치면 다음과 같은 폴더 구조를 가진 프로젝트 폴더가 생긴다.

![]({{site.static_url}}/img/dropbox/2016-12-27%2001.25.13.png)

```sh
(tdd_study) ➜  tdd_study_proj tree
.
├── manage.py
└── tdd_study_proj
    ├── __init__.py
    ├── settings.py
    ├── urls.py
    └── wsgi.py

1 directory, 5 files
```

(유의: tree명령어는 Mac OS에서 HomeBrew를 통해 설치한 패키지다. 자신의 쉘에서 동작하지 않는다고 문제가 있는건 아니다.)

위 파일 구조를 보면 tdd_study_proj라는 큰 폴더(현재위치) 안에 manage.py파일과 현재위치 폴더이름과 같은 tdd_study_proj라는 프로젝트 폴더가 생겨있다.

이 상태에서 장고에 내장된 테스트 웹서버를 구동해 보자. 테스트용 웹서버는 runserver 라는 명령어로 실행할 수 있고, CTRL-C로 작동을 멈추게 할 수 있다.
manage.py파일이 있는 곳에서 아래의 명령어를 쳐주자.

```
$ python manage.py runserver
```

위 명령어를 치면 아래와 같이 테스트 서버가 http://127.0.0.1:8000 에서 실행되고 있다.
(참고: 127.0.0.1 주소는 localhost와 동일합니다. 즉, 127.0.0.1:8000은 localhost:8000입니다.)

![]({{site.static_url}}/img/dropbox/2016-12-27%2001.34.26.png)

위 URL로 들어갔을 때 아래와 같은 화면이 나온다면 Django가 정상적으로 설치되었고, 테스트 웹서버도 정상적으로 구동중인 것이다.

![]({{site.static_url}}/img/dropbox/2016-12-27%2001.36.09.png)

### 3. 다시한번 테스트!

Django서버가 켜져있는 상태로 둔 후, 새 쉘(혹은 cmd)창을 켜서 실습1. Selenium 이용해보기에서 만든 파일을 manage.py파일이 있는 폴더에 `selenium_test.py`라는 이름으로 만들어 주자.

```py
# selenium_test.py

from selenium import webdriver

browser = webdriver.Chrome('chromedriver')
browser.get('http://localhost:8000')

assert 'Django' in browser.title
``` 

![]({{site.static_url}}/img/dropbox/2016-12-27%2001.45.10.png)

이제는 에러가 나지 않고 테스트가 아무말(아무 에러)없이 끝나는걸 볼 수 있다 :)
