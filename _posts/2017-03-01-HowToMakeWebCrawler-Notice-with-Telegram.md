---
title: "나만의 웹 크롤러 만들기(5): Telegram으로 웹페이지 변경 알림 받기"
date: 2017-03-01 10:00:00+09:00
layout: post
categories:
- Python
- HowToMakeWebCrawler
published: false
image: /img/2017-03-01-HowToMakeWebCrawler-Notice-with-Telegram/telegram_bot.png
---

앞서 `Django`를 이용해 크롤링한 데이터를 DB에 저장해 보았습니다.

하지만 크롤링을 할 때마다 동일한(중복된) 데이터를 DB에 저장하는 것은 바람직 하지 않은 일이죠.

또한, 크롤링을 자동으로 해 사이트에 변경사항이 생길 때 마다 내 텔레그램으로 알림을 받을 수 있다면 더 편리하지 않을까요?

이번 가이드에서는 네이버 중고나라 등에서 **특정 키워드** 검색 페이지를 크롤링해 새 게시글이 올라올 경우 새 글의 제목과 링크를 텔레그램으로 보내는 것까지를 다룹니다.

다루는 내용:
  - Telegram Bot API
  - Selenium + BeautifulSoup
  - Crontab
  - 깃헙 이용한 배포(서버에 올리기)
  - Django이용한 DB

# Telegram Bot API
---

텔레그램은 REST API를 통해 봇을 제어하도록 안내합니다.

물론 직접 텔레그램 api를 사용할 수도 있지만, 이번 가이드에서는 좀 더 빠른 개발을 위해 `python-telegram-bot` 패키지를 사용합니다.

`python-telegram-bot`은 Telegram Bot API를 python에서 쉽게 이용하기 위한 wrapper 패키지입니다.

## python-telegram-bot 설치하기

`python-telegram-bot`은 pip로 설치 가능합니다.

```bash
pip install python-telegram-bot
```

## 텔레그램 봇 만들기 & API Key받기

텔레그램 봇을 만들고 API키를 받아 이용하는 기본적인 방법은 [python에서 telegram bot 사용하기](https://blog.psangwoo.com/2016/12/08/python%EC%97%90%EC%84%9C-telegram-bot-%EC%82%AC%EC%9A%A9%ED%95%98%EA%B8%B0/)에 차근차근 설명되어있습니다.

> 이번 가이드는 텔레그램 봇을 다루는 내용보다는 Cron으로 크롤링을 하고 변화 발견시 텔레그램 메시지를 보내는 것에 초점을 맞췄습니다.

텔레그램 봇 API키를 받아왔다면 아래와 같이 
