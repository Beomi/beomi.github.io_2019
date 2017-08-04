---
title: "나만의 웹 크롤러 만들기(7): 창없는 크롬으로 크롤링하기"
date: 2017-08-01
layout: post
categories:
- Python
- HowToMakeWebCrawler
published: false
image: /img/Crawling-with-HeadlessChrome.png
---

> 이번 가이드는 가이드 3편([Selenium으로 무적 크롤러 만들기](/2017/02/27/HowToMakeWebCrawler-With-Selenium/))의 확장편입니다. 아직 `selenium`을 이용해보지 않은 분이라면 먼저 저 가이드를 보고 오시는걸 추천합니다.

## HeadLess Chrome? 머리없는 크롬?

일전 가이드에서 `PhantomJS`(팬텀)라는 브라우저를 이용하는 방법에 대해 다룬적이 있습니다. 팬텀은 브라우저와 유사하게 동작하고 Javascript를 동작시켜주지만 성능상의 문제점과 크롬과 완전히 동일하게 동작하지는 않는다는 문제점이 있습니다.

> 하지만 여전히 팬텀이 가지는 장점이 있습니다. WebDriver Binary만으로 추가적인 설치 없이 환경을 만들 수 있다는 장점이 있습니다.

윈도우 기준 크롬 59, 맥/리눅스 기준 크롬 60버전부터 크롬에 `Headless Mode`가 정식으로 추가되어서 만약 여러분의 브라우저가 최신이라면 크롬의 Headless모드를 쉽게 이용할 수 있습니다.

## 크롬 버전 확인하기

크롬 버전 확인은 크롬 브라우저에서 [chrome://version/](chrome://version/)로 들어가 확인할 수 있습니다.

![](/img/dropbox/ScreenShot2017-08-0112.47.57.png)

