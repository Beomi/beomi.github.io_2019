---
title: "Celery로 TelegramBot 알림 보내기"
date: 2016-12-28
layout: post
published: true
categories:
- Python
- Celery
image: /img/old_post/celery_512.png
---

# Celery는 비동기 큐이지만 주기적 Task도 잘한다

Celery는 async/비동기적으로 특정한 작업을 돌리기 위해 자주 사용한다. 특히, django와는 찰떡궁합이라고 알려져있다.
하지만 이 celery는 설정이 어렵다면 어렵고, 쉽다면 쉬운편이다.

먼저 Celery를 "쓰려면" 어떤 것들이 필요한지 체크해보자.

## Celery 준비물

- pip를 통해 설치된 Celery가 필요하다.

```
$ pip install celery
```

- RabbitMQ나 Redis등의 큐 중간 저장소가 필요하다. RabbitMQ를 설치해보자.

```
$ brew install rabbitmq
```

- 이후 `.bashrc`나 `.zshrc`의 마지막 줄에 아래 코드를 추가해준다.

```
export PATH=$PATH:/usr/local/sbin
```

이로서 rabbitmq-server라는 명령어로 rabbitmq를 실행할 수 있다.

## 셀러리가 돌아갈 파이썬 파일 만들기

아래와 같이 코드를 작성해 보자. (celery_parser.py)

```py
# celery_parser.py
from celery import Celery

# Celery Setup
app = Celery()
app.conf.timezone = 'Asia/Seoul'

@app.on_after_configure.connect
def periodic_parser(sender, **kwargs):
    sender.add_periodic_task(5.0, hello(), name='hello?')

@app.task
def hello():
    print('hello!')
```

위 코드를 작성한 후, 쉘을 두 창을 켠 후 각각 아래 코드를 입력해 준다. (celery_parser.py와 같은 폴더에서)

```
celery worker -A celery_parser --loglevel=info

<이용법>
celery worker -A 파이썬파일이름 --loglevel=info
```

위 코드는 Celery의 get_url함수, 즉 app의 Task함수가 실제로 구동될 `worker`이며,
아래 코드는 periodic_parser함수 안에서 정의된 sender.add_periodic_task에 의해 첫번째 인자로 전달된 5.0초, 두번째 인자로 전달된 hello 함수를 실행하게 하는 Celery의 `beat`이다.

```
celery beat -A celery_parser  --loglevel=info

<이용법>
celery beat -A 파이썬파일이름 --loglevel=info
```

# TelegramBot 설정하기

## python에서 telegram bot 사용 가이드

텔레그램 봇을 Python에서 이용하는 좋은 가이드가 있다. 

[python에서 telegram bot 사용하기](https://blog.psangwoo.com/2016/12/08/python%EC%97%90%EC%84%9C-telegram-bot-%EC%82%AC%EC%9A%A9%ED%95%98%EA%B8%B0/)

위 링크를 참고해서 pip로 `python-telegram-bot`을 설치하고, 새 봇을 만든 후 token과 id값을 받아오자.

## requests를 이용해 site의 변화 유무 체크하기

우선 파이썬 파일을 수정하기 전에 `target.json`라는 환경변수용 json파일을 아래와 같이 만들어 주자.

```json
{
  "BOT_TOKEN":"위에서 받은 숫자9자리:영문+숫자+특수문자 긴것",
  "URL":"변화유무를 체크할 URL",
  "CHAT_ID":"위에서 받은 id"
}
```

이제 `celery_parser.py`에서 `target.json`파일을 불러온 후, 변수로 등록해주고, telegram bot 객체를 만들어 준 후 sendMessage를 이용해 보자.

```py
# celery_parser.py
from celery import Celery

import requests
import json
import os
import datetime

import telegram

# Celery Setup
app = Celery()
app.conf.timezone = 'Asia/Seoul'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Parsing/Telegram Environ loads
with open(os.path.join(BASE_DIR, "target.json")) as f:
    env = json.loads(f.read())
    BOT_TOKEN = env['BOT_TOKEN']
    URL = env['URL']
    CHAT_ID = env['CHAT_ID']

bot = telegram.Bot(token=BOT_TOKEN)

bot.sendMessage(chat_id=CHAT_ID, text='Started!')

@app.on_after_configure.connect
def periodic_parser(sender, **kwargs):
    sender.add_periodic_task(5.0, get_url.s(URL), name='send working time')

@app.task
def get_url(url):
    req = requests.get(url)
    f = open('temp/req.txt', 'w+')
    previous_html = f.read()
    new_html = req.text
    bot.sendMessage(chat_id=CHAT_ID, text='Working/{}'.format(datetime.datetime.now()))

    if previous_html == new_html:
        bot.sendMessage(chat_id=CHAT_ID, text='working...')
    else:
        #TODO: BOT NOTICE
        bot.sendMessage(chat_id=CHAT_ID, text='{} 에 변경이 있습니다.'.format(url))
```

위 코드는 URL에 접속해 html로 저장 후 5초 후 다음 접속 시 사이트에 변동사항이 있으면 변동이 있다는 Telegram 알림을 보내준다.
