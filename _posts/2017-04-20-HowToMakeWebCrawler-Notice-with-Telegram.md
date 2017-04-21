---
title: "나만의 웹 크롤러 만들기(5): 웹페이지 업데이트를 알려주는 Telegram 봇"
date: 2017-04-20 12:00:00
layout: post
categories:
- Python
- HowToMakeWebCrawler
published: true
image: /img/telegram.png
---

> 이전게시글: [나만의 웹 크롤러 만들기(4): Django로 크롤링한 데이터 저장하기](/2017/03/01/HowToMakeWebCrawler-Save-with-Django/)

> 이번 가이드에서는 작업하는 컴퓨터가 아닌 원격 우분투16.04 서버(vps)에 올리는 부분까지 다룹니다. 테스트는 `crontab -e` 명령어를 사용할 수 있는 환경에서 가능하며, VISA/Master카드등 해외결제가 가능한 카드가 있다면 서비스 가입 후 실제로 배포도 가능합니다. 이 가이드에서는 Vultr VPS를 이용합니다.

앞서 `Django`를 이용해 크롤링한 데이터를 DB에 저장해 보았습니다.

하지만 크롤링을 할 때마다 동일한(중복된) 데이터를 DB에 저장하는 것은 바람직 하지 않은 일이죠.

또한, 크롤링을 자동으로 해 사이트에 변경사항이 생길 때 마다 내 텔레그램으로 알림을 받을 수 있다면 더 편리하지 않을까요?

이번 가이드에서는 클리앙 중고장터 등을 크롤링해 새 게시글이 올라올 경우 새글 알림을 텔레그램으로 보내는 것까지를 다룹니다.

다루는 내용:

  - Telegram Bot API
  - requests / BeautifulSoup
  - Crontab

## 시작하며
---

텔레그램은 REST API를 통해 봇을 제어하도록 안내합니다.

물론 직접 텔레그램 api를 사용할 수도 있지만, 이번 가이드에서는 좀 더 빠른 개발을 위해 `python-telegram-bot` 패키지를 사용합니다.

`python-telegram-bot`은 Telegram Bot API를 python에서 쉽게 이용하기 위한 wrapper 패키지입니다.

## python-telegram-bot 설치하기
---

`python-telegram-bot`은 pip로 설치 가능합니다.

```bash
pip install python-telegram-bot
```

> `requests`, `bs4` 역시 설치되어있어야 합니다!

## 텔레그램 봇 만들기 & API Key받기
---

텔레그램 봇을 만들고 API키를 받아 이용하는 기본적인 방법은 [python에서 telegram bot 사용하기](https://blog.psangwoo.com/coding/2016/12/08/python-telegram-bot-1.html)에 차근차근 설명되어있습니다.


위 가이드에서 텔레그램 봇의 토큰을 받아오세요. 토큰은 `aaaa:bbbbbbbbbbbbbb`와 같이 생긴 문자열입니다.

> 이번 가이드는 텔레그램 봇을 다루는 내용보다는 Cron으로 크롤링을 하고 변화 발견시 텔레그램 메시지를 보내는 것에 초점을 맞췄습니다.

텔레그램 봇 API키를 받아왔다면 아래와 같이 크롤링을 하는 간단한 python파일을 작성해 봅시다. 클리앙에 새로운 글이 올라오면 "새 글이 올라왔어요!"라는 메시지를 보내는 봇을 만들어 보겠습니다.

## 클리앙 새글 탐지코드 만들기
---

![clien marcket web page list](https://www.dropbox.com/s/0o4q6bd0xgqc8o7/%EC%8A%A4%ED%81%AC%EB%A6%B0%EC%83%B7%202017-04-21%2000.46.01.png?dl=1)

우선 게시판의 글 제목중 첫번째 제목을 가져오고 txt파일로 저장하는 코드를 만들어 봅시다.

회원 장터 주소는 `http://clien.net/cs2/bbs/board.php?bo_table=sold`이고, 첫 게시글의 CSS Selector는 `#content > div.board_main > table > tbody > tr:nth-child(3) > td.post_subject > a`임을 알 수 있습니다. 따라서 아래와 같이 `latest` 변수에 담아 같은 폴더의 `latest.txt` 파일에 써 줍시다.


```python
# clien_market_parser.py
import requests
from bs4 import BeautifulSoup
import os

# 파일의 위치
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

req = requests.get('http://clien.net/cs2/bbs/board.php?bo_table=sold')
req.encoding = 'utf-8' # Clien에서 encoding 정보를 보내주지 않아 encoding옵션을 추가해줘야합니다.

html = req.text
soup = BeautifulSoup(html, 'html.parser')
posts = soup.select('td.post_subject')
latest = posts[1].text # 0번은 회원중고장터 규칙입니다.

with open(os.path.join(BASE_DIR, 'latest.txt'), 'w+') as f:
    f.write(latest)
```

위와 같이 코드를 구성하면 `latest.txt`파일에 가장 최신 글의 제목이 저장됩니다.

크롤링 이후 새로운 글이 생겼는지의 유무를 알아보려면 크롤링한 최신글의 제목과 파일에 저장된 제목이 같은지를 확인하면 됩니다.

만약 같다면 패스, 다르다면 텔레그램으로 메시지를 보내는거죠!

```python
# clien_market_parser.py
import requests
from bs4 import BeautifulSoup
import os

# 파일의 위치
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

req = requests.get('http://clien.net/cs2/bbs/board.php?bo_table=sold')
req.encoding = 'utf-8'

html = req.text
soup = BeautifulSoup(html, 'html.parser')
posts = soup.select('td.post_subject')
latest = posts[1].text

with open(os.path.join(BASE_DIR, 'latest.txt'), 'r+') as f_read:
    before = f_read.readline()
    if before != latest:
        # 같은 경우는 에러 없이 넘기고, 다른 경우에만
        # 메시지 보내는 로직을 넣으면 됩니다.
    f_read.close()

with open(os.path.join(BASE_DIR, 'latest.txt'), 'w+') as f_write:
    f_write.write(latest)
    f_write.close()
```

## 새글이라면? 텔레그램으로 메시지 보내기!
---

이제 메시지를 보내볼게요. `telegram`을 import하신 후 `bot`을 선언해주시면 됩니다. token은 위에서 받은 토큰입니다.

```python
# clien_market_parser.py
import requests
from bs4 import BeautifulSoup
import os

import telegram

# 토큰을 지정해서 bot을 선언해 줍시다! (물론 이 토큰은 dummy!)
bot = telegram.Bot(token='123412345:ABCDEFgHiJKLmnopqr-0StUvwaBcDef0HI4jk')
# 우선 테스트 봇이니까 가장 마지막으로 bot에게 말을 건 사람의 id를 지정해줄게요.
# 만약 IndexError 에러가 난다면 봇에게 메시지를 아무거나 보내고 다시 테스트해보세요.
chat_id = bot.getUpdates()[-1].message.chat.id

# 파일의 위치
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

req = requests.get('http://clien.net/cs2/bbs/board.php?bo_table=sold')
req.encoding = 'utf-8'

html = req.text
soup = BeautifulSoup(html, 'html.parser')
posts = soup.select('td.post_subject')
latest = posts[1].text

with open(os.path.join(BASE_DIR, 'latest.txt'), 'r+') as f_read:
    before = f_read.readline()
    if before != latest:
        bot.sendMessage(chat_id=chat_id, text='새 글이 올라왔어요!')
    else: # 원래는 이 메시지를 보낼 필요가 없지만, 테스트 할 때는 봇이 동작하는지 확인차 넣어봤어요.
        bot.sendMessage(chat_id=chat_id, text='새 글이 없어요 ㅠㅠ')
    f_read.close()

with open(os.path.join(BASE_DIR, 'latest.txt'), 'w+') as f_write:
    f_write.write(latest)
    f_write.close()
```

이제 `clien_market_parser.py`파일을 실행할 때 새 글이 올라왔다면 "새 글이 올라왔어요!"라는 알림이, 새 글이 없다면 "새 글이 없어요 ㅠㅠ"라는 알림이 옵니다.

> 지금은 자동으로 실행되지 않기 때문에 `python clien_market_parser.py`명령어로 직접 실행해 주셔야 합니다.


## 자동으로 크롤링하고 메시지 보내기
---

### 가장 쉬운방법: `while` + `sleep`

가장 쉬운 방법은 python의 `while`문을 쓰는 방법입니다. 물론, 가장 나쁜 방법이에요. 안전하지도 않고 시스템의 메모리를 좀먹을 수도 있어요.

하지만 테스트에서는 가장 쉽게 쓸 수 있어요.

```python
# clien_market_parser.py
import requests
from bs4 import BeautifulSoup
import os
import time

import telegram

bot = telegram.Bot(token='123412345:ABCDEFgHiJKLmnopqr-0StUvwaBcDef0HI4jk')
chat_id = bot.getUpdates()[-1].message.chat.id

# 파일의 위치
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

while True:
    req = requests.get('http://clien.net/cs2/bbs/board.php?bo_table=sold')
    req.encoding = 'utf-8'

    html = req.text
    soup = BeautifulSoup(html, 'html.parser')
    posts = soup.select('td.post_subject')
    latest = posts[1].text

    with open(os.path.join(BASE_DIR, 'latest.txt'), 'r+') as f_read:
        before = f_read.readline()
        if before != latest:
            bot.sendMessage(chat_id=chat_id, text='새 글이 올라왔어요!')
        else:
            bot.sendMessage(chat_id=chat_id, text='새 글이 없어요 ㅠㅠ')
        f_read.close()

    with open(os.path.join(BASE_DIR, 'latest.txt'), 'w+') as f_write:
        f_write.write(latest)
        f_write.close()

    time.sleep(60) # 60초(1분)을 쉬어줍니다.
```

> 파이썬 동작중에는 CTRL+C로 빠져나올수 있습니다.

### 추천: 시스템의 cron/스케쥴러를 이용하기

이번 가이드에서 핵심인 부분인데요, 이 부분은 이제 우분투 16.04 기준으로 진행할게요.

우선 Ubuntu 16.04가 설치된 시스템이 필요합니다. 이번 강의에서는 Vultr VPS를 이용합니다.

![add deploy new vps](https://www.dropbox.com/s/49pacgspaxag8vr/%EC%8A%A4%ED%81%AC%EB%A6%B0%EC%83%B7%202017-04-21%2001.31.34.png?dl=1)

Vultr는 가상 서버 회사인데, Tokyo리전의 VPS를 제공해줘 빠르게 이용이 가능합니다. 트래픽도 굉장히 많이주고요.

가이드를 만드는 지금은 월 2.5달러 VPS는 아쉽게도 없어서, 월5달러 VPS로 진행하지만 월2.5달러 VPS로도 충분합니다!

아래의 Deploy Now를 누르면 새 Cloud Instance(VPS)가 생성되는데요, 서버가 생성된 후 들어가 보면 다음과 같이 id와 pw가 나와있습니다. 패스워드는 눈 모양을 누르면 잠시 보입니다.

![](https://www.dropbox.com/s/ucteu8j3dpgam43/%EC%8A%A4%ED%81%AC%EB%A6%B0%EC%83%B7%202017-04-21%2001.43.54.png?dl=1)

이 정보로 ssh에 접속해 봅시다. (윈도는 putty이나 Xshell등을 이용해주세요.)

![](https://www.dropbox.com/s/8dps1f3ttwdgdpd/%EC%8A%A4%ED%81%AC%EB%A6%B0%EC%83%B7%202017-04-21%2001.46.08.png?dl=1)

우분투 16.04버전에는 이미 Python3.5버전이 설치되어있기 때문에 `pip3`, `setuptools`을 설치해 주고 Ubuntu의 Locale을 설정해줘야 합니다. 아래 명령어를 한줄씩 순차적으로 치시면 완료됩니다.

```bash
sudo apt install python3-pip python3-setuptools build-essential
sudo locale-gen "ko_KR.UTF-8"
pip3 install requests bs4 python-telegram-bot
```

![](https://www.dropbox.com/s/bcvpfyme1emykst/%EC%8A%A4%ED%81%AC%EB%A6%B0%EC%83%B7%202017-04-21%2001.48.11.png?dl=1)

설치를 하신 후 코드를 테스트 해보려면 위 파일을 `vi`등으로 열어 위 코드들을 입력하시면 됩니다.

이제 코드를 약간 바꿔볼게요. 새 글이 올라올때만 파일을 다시 쓰도록 해요.

```python
# clien_market_parser.py
import requests
from bs4 import BeautifulSoup
import os

import telegram

bot = telegram.Bot(token='123412345:ABCDEFgHiJKLmnopqr-0StUvwaBcDef0HI4jk')
chat_id = bot.getUpdates()[-1].message.chat.id

# 파일의 위치
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

req = requests.get('http://clien.net/cs2/bbs/board.php?bo_table=sold')
req.encoding = 'utf-8'

html = req.text
soup = BeautifulSoup(html, 'html.parser')
posts = soup.select('td.post_subject')
latest = posts[1].text

with open(os.path.join(BASE_DIR, 'latest.txt'), 'r') as f_read:
    before = f_read.readline()
    f_read.close()
    if before != latest:
        bot.sendMessage(chat_id=chat_id, text='새 글이 올라왔어요!')
        with open(os.path.join(BASE_DIR, 'latest.txt'), 'w+') as f_write:
            f_write.write(latest)
            f_write.close()
```

이제 이 `clien_market_parser.py` 파일을 `python3`으로 실행해야 하기 때문에, `python3`이 어디 설치되어있는지 확인 해 봅시다.(아마 `/usr/bin/python3`일거에요!)

```bash
root@vultr:~# which python3
/usr/bin/python3
```

이제 Crontab에 이 파이썬으로 우리 파일을 매 1분마다 실행하도록 만들어 봅시다.

> crontab 수정은 `crontab -e`명령어로 사용 가능합니다. 만약 에디터를 선택하라고 한다면 초보자는 Nano를, vi를 쓰실수 있으시다면 vi를 이용하세요.

이 한줄을 crontab 마지막에 추가해 주세요.

```bash
* * * * * /usr/bin/python3 /root/clien_market_parser.py
```

> 힌트: 매 12분마다로 하시려면 `*/12 * * * * /usr/bin/python3 /root/clien_market_parser.py`로 하시면 됩니다.

![](https://www.dropbox.com/s/s3h1gzbrjg3lv3o/%EC%8A%A4%ED%81%AC%EB%A6%B0%EC%83%B7%202017-04-21%2002.03.23.png?dl=1)

이제 여러분의 휴대폰으로 새 글이 올라올 때 마다 알람이 올라올 거랍니다 :)



## 마무리
---

이번편 가이드는 DB를 이용하지 않고 단순하게 새로운 글이 왔다는 사실만을 메시지로 알려주는 봇을 만들어서 뭔가 아쉬움이 있을겁니다. 

다음 가이드에서는 실제 명령어를 받아 사용자들의 정보를 저장하고 사용자들에게 실제로 유용한 정보(예: 글 제목과 링크)를 보내주는 내용으로 진행합니다.
