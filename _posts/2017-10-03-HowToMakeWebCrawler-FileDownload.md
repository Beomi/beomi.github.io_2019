---
title: "나만의 웹 크롤러 만들기(8): 로그인 유지하며 파일 다운로드받기"
date: 2017-10-03
layout: post
categories:
- Python
- HowToMakeWebCrawler
published: false
image: /img/download_files_with_python.jpg
---

## 들어가며

여러분이 앞선 크롤링 가이드를 보면서 떠오른 생각 중 아래와 같은 질문이 떠오른적이 있나요?

"복잡한 로그인이 필요한 사이트에 Selenium으로 로그인 하고나서 크롤링은 requests로 못하는 걸까?"

앞선 가이드에서 쿠키와 세션에 대해 이해하셨다면 이런 질문을 떠올릴 수도 있어요.

그래서 그 대답으로, 이번 가이드에서는 `Selenium`으로 로그인한 후 로그인 상태를 유지하며 `requests`를 통해 파일을 다루는 방법에 대해 다룹니다. (물론 동일한 방법으로 파일 다운로드 대신 HTML 크롤링을 할 수도 있어요!)

## 준비물

- 크롬 브라우저
- requests
- bs4 (BeautifulSoup4)
- Selenium

> 파이썬 패키지들은 `pip install -U requests bs4 selenium`로 설치(+업그레이드)할 수 있어요!

## 핵심 개념

앞선 가이드에서 다루었던 '쿠키'를 유지하는 부분이 로그인 상태를 유지하는데 가장 중요한 부분이라는 것은 이미 알고 계실거에요. 따라서 우리가 해줘야 하는 일은 다음과 같아요.

1. Selenium + 크롬으로 로그인하기
2. 로그인한 상태에서 쿠키 꺼내오기
3. requests의 세션 객체에 쿠키값 넣어주기
4. requests로 파일 다운로드 받기

자, 시작해봅시다!

## Selenium + Chrome으로 로그인하기

우선, 앞선 가이드에서 Selenium과 크롬으로 로그인을 했던 부분 기억하시나요?

자, 쉬운 예제부터 시작해볼게요.




