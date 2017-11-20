---
title: "나만의 웹 크롤러 만들기(4): Django로 크롤링한 데이터 저장하기"
date: 2017-03-01
layout: post
categories:
- Python
- HowToMakeWebCrawler
published: true
image: /img/2017-02-27-HowToMakeWebCrawler-Save-with-Django/python+django.jpg
---

> 좀 더 보기 편한 [깃북 버전의 나만의 웹 크롤러 만들기](https://beomi.github.io/gb-crawling/)가 나왔습니다!

> (@2017.03.18) 본 블로그 테마가 업데이트되면서 구 블로그의 URL은 https://beomi.github.io/beomi.github.io_old/로 변경되었습니다. 예제 코드에서는 변경을 완료하였지만 캡쳐 화면은 변경하지 않았으니 유의 바랍니다.

이전게시글: [나만의 웹 크롤러 만들기(3): Selenium으로 무적 크롤러 만들기](/2017/02/27/HowToMakeWebCrawler-With-Selenium/)

Python을 이용해 `requests`와 `selenium`을 이용해 웹 사이트에서 데이터를 크롤링해 보았습니다.

하지만 이러한 데이터를 체계적으로 관리하려면 DB가 필요하고, 이러한 DB를 만들고 관리하는 방법이 여러가지가 있지만 이번 가이드에서는 Python 웹 프레임워크인 `django`의 Database ORM을 이용해 DB를 만들고 데이터를 저장해 보려 합니다.

이번 가이드에서는 1회차 가이드였던 이 블로그를 크롤링해서 나온 결과물을 Django ORM으로 Sqlite DB에 저장해보는 것까지를 다룹니다.

> 이번 가이드는 기본적으로 Django의 `Model`에 대해 이해하고 있는 분들에게 추천합니다.

> 만약 django가 처음이시라면 [DjangoGirls Tutorial: DjangoTube](https://djangogirlsseoul.gitbooks.io/django-tube/content/)를 따라해보시면 기본적인 이해에 도움이 되시리라 생각합니다. 30분 내외로 따라가실 수 있습니다.

# Django 프로젝트 만들기
---

우선 크롤링 한 데이터를 저장할 Django 프로젝트와 앱을 만들고, Model을 통해 DB를 만들어야 합니다.

## Django 설치하기

Django는 pip로 간편하게 설치할 수 있습니다.

> 가상환경을 이용해 설치하는 것을 추천합니다. 가상환경은 python3.4이후부터는 `python3 -m venv 가상환경이름`으로 만드실 수 있습니다.

```bash
pip install django
```

![django install success](https://www.dropbox.com/s/nkesbxo0s5jkexs/%EC%8A%A4%ED%81%AC%EB%A6%B0%EC%83%B7%202017-02-28%2017.14.57.png?dl=1)

> 글 작성 시점인 2017.02.28 기준 1.10.5 버전이 최신버전입니다.

## Django Start Project | 프로젝트 만들기

django가 성공적으로 설치되면 `django-admin`이라는 명령어로 장고 프로젝트를 생성할 수 있습니다.

이번 가이드에서는 `websaver`라는 이름의 프로젝트를 만들어보겠습니다.

```bash
django-admin startproject websaver
```

![startproject websaver](https://www.dropbox.com/s/bayd1r5uddcf5n9/%EC%8A%A4%ED%81%AC%EB%A6%B0%EC%83%B7%202017-02-28%2017.15.47.png?dl=1)

> 성공적으로 생길 경우 어떠한 반응도 나타나지 않습니다.

위 명령어를 치면 명령어를 친 위치에 `websaver`라는 폴더가 생기고, 그 안의 구조는 아래와 같습니다.

> `cd websaver`로 `websaver`폴더 안으로 진입한 상태입니다.

![tree websaver](https://www.dropbox.com/s/md2vxw6ii9ahanc/%EC%8A%A4%ED%81%AC%EB%A6%B0%EC%83%B7%202017-02-28%2017.18.06.png?dl=1)

> tree 명령어는 mac에서 `brew install tree`로 설치한 명령어입니다. 기본적으로는 깔려있지 않습니다.

이와 같이 `manage.py`파일과 프로젝트 이름인 `websaver`라는 이름의 폴더가 함께 생성됩니다.

## Django Start App | 장고 앱 만들기

Django는 프로젝트와 그 안의 `앱`으로 관리됩니다. 이 `앱`은 하나의 기능을 담당하는 단위로 보시면 됩니다.

앱은 `manage.py`파일을 통해 `startapp`이라는 명령어로 생성 가능합니다. `parsed_data`라는 이름의 앱을 만들어보겠습니다.

```bash
python manage.py startapp parsed_data
```

> manage.py 파일이 있는 곳에서 실행합니다. django가 설치된 가상환경에 진입해 있는지 꼭 확인하세요!

이제 아래와 같은 구조로 앱이 생겼을 것인데, 이 앱을 Django가 관리하도록 `websaver`폴더 안의 `settings.py`파일의 `INSTALLED_APPS`에 추가해줘야 합니다.

![startapp parsed_data](https://www.dropbox.com/s/mbqsx8yjd6jee88/%EC%8A%A4%ED%81%AC%EB%A6%B0%EC%83%B7%202017-02-28%2017.32.06.png?dl=1)

> 유의: .pyc파일은 python실행시 생기는 캐싱 파일입니다. 없으셔도 전혀 문제는 발생하지 않습니다.

```py
# websaver/settings.py
...
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'parsed_data', # 앱을 추가해 줍시다.
]
...
```

## Django First Migration | 첫 마이그레이션
​
장고는 `python manage.py migrate`이라는 명령어로 DB를 migrate합니다.

```bash
python manage.py migrate
```

위 명령어를 입력하면 아래와 같이 Django에서 사용하는 기본적인 DB가 생성됩니다.

![First migrate](https://www.dropbox.com/s/nyyxwdmgmxer5zy/%EC%8A%A4%ED%81%AC%EB%A6%B0%EC%83%B7%202017-02-28%2017.37.23.png?dl=1)

## parsed_data App Model | parsed_data 앱 모델 만들기

이제 DB구조를 관리해주는 `Model`을 만들어 줘야 합니다.

Django에서 모델은 앱 단위로 만들어지고 구성됩니다. 따라서 앞서 만들어준 `parsed_data`앱 안의 `models.py`파일을 수정해줘야 합니다.

이 모델 파일은 크롤링해온 데이터를 필드별로 저장하는 것이 목적입니다. 따라서 크롤링한 데이터를 파이썬이 관리할 수 있는 객체로 만들어두는 것이 중요합니다.

이번 가이드에서는 [나만의 웹 크롤러 만들기 With Requests/BeautifulSoup](https://beomi.github.io/beomi.github.io_old/python/2017/01/19/HowToMakeWebCrawler.html)에서 만든 `parser.py`파일을 수정해 게시글의 title와 link를 DB에 저장해보겠습니다.

따라서 이번 앱의 모델에서는 title와 link라는 column을 가진 `BlogData`라는 이름의 Table을 DB에 만들면 됩니다.

> django models의 class는 DB의 Table이 됩니다.

```py
# parsed_data/models.py
from django.db import models


class BlogData(models.Model):
    title = models.CharField(max_length=200)
    link = models.URLField()
```

이와 같이 만들어주면 `title`은 200글자 제한의 CharField로, `link`는 URLField로 지정됩니다.

## parsed_data App Makemigrations & Migrate | 앱 DB 반영하기

이제 해야 할 일은 Django가 모델을 관리하도록 하려면 `makemigrations`를 통해 DB의 변경 정보를 정리하고, `migrate`를 통해 실제 DB에 반영하는 과정을 진행해야 합니다.

> django가 설치된 가상환경에서 실행하도록 합시다. 명령어의 실행 위치는 `manage.py`파일이 있는 곳입니다.

```bash
python manage.py makemigrations parsed_data
python manage.py migrate parsed_data
```

각 명령어 입력시 아래와 같이 결과가 나타난다면 성공적으로 DB에 반영된 것입니다.

![parsed_data app migration](https://www.dropbox.com/s/48twyrtrbxrj2cs/%EC%8A%A4%ED%81%AC%EB%A6%B0%EC%83%B7%202017-02-28%2017.58.01.png?dl=1)

# 크롤링 함수 만들기
---

[나만의 웹 크롤러 만들기 With Requests/BeautifulSoup](https://beomi.github.io/beomi.github.io_old/python/2017/01/19/HowToMakeWebCrawler.html)에서 만든 `parser.py`파일을 수정해보겠습니다.

이번 파일은 `manage.py`가 있는 위치에 `parser.py`라는 이름으로 저장해보겠습니다.

> 만약 `requests`와 `bs4`가 설치되어있지 않다면 pip로 설치해주세요!

```py
# parser.py
import requests
from bs4 import BeautifulSoup
import json
import os

# python파일의 위치
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

req = requests.get('https://beomi.github.io/beomi.github.io_old/')
html = req.text
soup = BeautifulSoup(html, 'html.parser')
my_titles = soup.select(
    'h3 > a'
    )

data = {}

for title in my_titles:
    data[title.text] = title.get('href')

with open(os.path.join(BASE_DIR, 'result.json'), 'w+') as json_file:
    json.dump(data, json_file)
```

이전의 `parser.py`파일은 위와 같습니다. 이제 이 파일을 `parse_blog`라는 함수로 만들고, {'블로그 글 타이틀': '블로그 글 링크'}로 이루어진 딕셔너리를 반환하도록 만들어 봅시다.

```py
# parser.py
import requests
from bs4 import BeautifulSoup

def parse_blog():
    req = requests.get('https://beomi.github.io/beomi.github.io_old/')
    html = req.text
    soup = BeautifulSoup(html, 'html.parser')
    my_titles = soup.select(
        'h3 > a'
        )
    data = {}
    for title in my_titles:
        data[title.text] = title.get('href')
    return data
```

이제 `parse_blog`라는 함수를 다른 파일에서 import해 사용할 수 있습니다.

또한, 현재 프로젝트 폴더의 구조는 아래와 같습니다.

![project folder tree](https://www.dropbox.com/s/72mil38qxny5kfn/%EC%8A%A4%ED%81%AC%EB%A6%B0%EC%83%B7%202017-02-28%2018.05.30.png?dl=1)

하지만 현재 `parse_blog`함수는 Django에 저장하는 기능을 갖고 있지 않습니다. 따라서 약간 더 추가를 해줘야 합니다.

## Django 환경 불러오기

```py
# parser.py
import requests
from bs4 import BeautifulSoup
# 아래 4줄을 추가해 줍니다.
import os
# Python이 실행될 때 DJANGO_SETTINGS_MODULE이라는 환경 변수에 현재 프로젝트의 settings.py파일 경로를 등록합니다.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "websaver.settings")
# 이제 장고를 가져와 장고 프로젝트를 사용할 수 있도록 환경을 만듭니다.
import django
django.setup()

def parse_blog():
    req = requests.get('https://beomi.github.io/beomi.github.io_old/')
    html = req.text
    soup = BeautifulSoup(html, 'html.parser')
    my_titles = soup.select(
        'h3 > a'
        )
    data = {}
    for title in my_titles:
        data[title.text] = title.get('href')
    return data
```

위 코드에서 아래 4줄을 추가해 줄 경우, 이 파일을 단독으로 실행하더라도 마치 `manage.py`을 통해 django를 구동한 것과 같이 django환경을 사용할 수 있게 됩니다.

## Django ORM으로 데이터 저장하기

```py
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "websaver.settings")
import django
django.setup()
```

> `python manage.py shell`을 실행하는 것과 비슷한 방법입니다.

이제 models에서 우리가 만든 `BlogData`를 import해 봅시다.

```py
# parser.py
import requests
from bs4 import BeautifulSoup
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "websaver.settings")
import django
django.setup()
# BlogData를 import해옵니다
from parsed_data.models import BlogData

def parse_blog():
    req = requests.get('https://beomi.github.io/beomi.github.io_old/')
    html = req.text
    soup = BeautifulSoup(html, 'html.parser')
    my_titles = soup.select(
        'h3 > a'
        )
    data = {}
    for title in my_titles:
        data[title.text] = title.get('href')
    return data

# 이 명령어는 이 파일이 import가 아닌 python에서 직접 실행할 경우에만 아래 코드가 동작하도록 합니다.
if __name__=='__main__':
    blog_data_dict = parse_blog()
    for t, l in blog_data_dict.items():
        BlogData(title=t, link=l).save()
```

위와 같이 `parser.py`를 수정한 후 터미널에서 `parser.py`파일을 실행해 봅시다.

```bash
python parser.py
```

아무런 에러가 나지 않는다면 성공적으로 저장된 것입니다.

## 저장된 데이터 Django Admin에서 확인하기

### SuperUser | 관리자계정 만들기

Django는 Django Admin이라는 강력한 기능을 제공합니다.

우선 Admin 계정을 만들어야 합니다. `createsuperuser` 명령어로 만들 수 있습니다.

![createsuperuser](https://www.dropbox.com/s/8w5s566ezu1cke3/%EC%8A%A4%ED%81%AC%EB%A6%B0%EC%83%B7%202017-02-28%2018.18.49.png?dl=1)

기본적으로 유저이름, 이메일, 비밀번호를 받습니다.

> 이메일은 입력하지 않아도 됩니다.

### 앱에 Admin 등록하기

Django가 어떤 앱을 admin에서 관리하도록 하려면 앱 폴더(`parsed_data`) 안의 `admin.py`파일을 수정해줘야 합니다.

```py
# parsed_data/admin.py
from django.contrib import admin
# models에서 BlogData를 import 해옵니다.
from .models import BlogData

# 아래의 코드를 입력하면 BlogData를 admin 페이지에서 관리할 수 있습니다.
admin.site.register(BlogData)
```

### Django Runserver | 장고 서버 실행하기

이제 `manage.py`가 있는 위치에서 `runserver`명령어로 장고 개발 서버를 실행해 봅시다.

```bash
python manage.py runserver
```

아래와 같이 나타난다면 성공적으로 서버가 실행된 것입니다.

![django runserver](https://www.dropbox.com/s/qhfk5bif82wfx4r/%EC%8A%A4%ED%81%AC%EB%A6%B0%EC%83%B7%202017-02-28%2018.26.07.png?dl=1)

이제 [http://localhost:8000/admin/](http://localhost:8000/admin/)로 들어가 봅시다.

![Django admin login page](https://www.dropbox.com/s/xdkorfb3x2i9mds/%EC%8A%A4%ED%81%AC%EB%A6%B0%EC%83%B7%202017-02-28%2018.27.23.png?dl=1)

아까 `createsuperuser`로 만든 계정으로 로그인 해 봅시다.

![django admin page](https://www.dropbox.com/s/8wdr128p2dv5o6h/%EC%8A%A4%ED%81%AC%EB%A6%B0%EC%83%B7%202017-02-28%2018.28.09.png?dl=1)

우리가 만든 `parsed_data`앱 안에 `BlogData`라는 항목이 나와있는 것을 볼 수 있습니다.

![blogdata admin list](https://www.dropbox.com/s/9e18fs87e3s8k5c/%EC%8A%A4%ED%81%AC%EB%A6%B0%EC%83%B7%202017-02-28%2018.28.54.png?dl=1)

`BlogData object`라는 이름으로 데이터들이 들어와 있는 것을 확인할 수 있습니다. 하나를 클릭해 들어가 보면 아래와 같이 title와 link가 성공적으로 들어와 있는 것을 볼 수 있습니다.

![blogdata specific data](https://www.dropbox.com/s/e4hf0d2si2y54ep/%EC%8A%A4%ED%81%AC%EB%A6%B0%EC%83%B7%202017-02-28%2018.29.43.png?dl=1)

# 약간 더 나아가기
---

위에서 Admin페이지에 들어갈 때 모든 데이터들의 이름이 `BlogData object`로 나와있는 것을 볼 수 있습니다.

우리가 만들어 준 `parsed_data/models.py`파일의 `BlogData` Class를 살펴보면 `models.Model`클래스를 상속받아 만들었고, 이 클래스는 기본적으로 `ClassName + object`라는 값을 반환하는 `__str__`함수를 내장하고 있습니다.

따라서 `models.Model`을 상속받은 `BlogData`의 `__str__`함수에서는 `BlogData object`라는 값을 반환합니다. 이 `__str__`함수를 오버라이딩해 사용하면 Admin에서 데이터의 이름을 좀 더 직관적으로 알 수 있습니다.

## __str__ 함수 오버라이딩하기

`parsed_data`앱 폴더 안의 `models.py`파일을 아래와 같이 수정해 봅시다.

```py
# parsed_data/models.py
from django.db import models


class BlogData(models.Model):
    title = models.CharField(max_length=200)
    link = models.URLField()

    def __str__(self):
    	return self.title
```

위 코드는 BlogData 데이터 객체의 `title` 값을 반환합니다.

이제 장고 서버를 다시 켜주고 [BlogData admin page](http://localhost:8000/admin/parsed_data/blogdata/)로 들어가면 타이틀 이름으로 된 데이터들을 볼 수 있습니다.

![title list admin page](https://www.dropbox.com/s/bamfziv55ff34fp/%EC%8A%A4%ED%81%AC%EB%A6%B0%EC%83%B7%202017-02-28%2018.38.11.png?dl=1)

> 현재 `models.py`파일을 수정했지만 DB에 반영되는 사항이 아니기 때문에 `makemigrations`나 `migrate`를 해줄 필요가 없습니다.

# 다음 가이드에서는..
---

다음 가이드는 **주기적**으로 데이터를 크롤링 해, **새로운** 데이터가 생기는 경우 텔레그램 봇으로 메시지 알림을 보내주는 과정을 다룰 예정입니다.

다음 가이드: [나만의 웹 크롤러 만들기(5): 웹페이지 업데이트를 알려주는 Telegram 봇](/2017/04/20/HowToMakeWebCrawler-Notice-with-Telegram/)
