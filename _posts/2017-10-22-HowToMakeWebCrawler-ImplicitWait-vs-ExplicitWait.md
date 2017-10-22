---
title: "Selenium Implicitly wait vs Explicitly wait"
date: 2017-10-22
layout: post
categories:
- HowToMakeWebCrawler
published: false
image: /img/Selenium_Implicitly_wait_vs_Explicitly_wait.png
---

## 들어가며

> 결론만 보고싶으신 분은 [TL;DR](#tldr)을 참고하세요.

Selenium WebDriver를 이용해 실제 브라우저를 동작시켜 크롤링을 진행할 때 가끔가다보면 `NoSuchElementException`라는 에러가 나는 경우를 볼 수 있습니다.

가장 대표적인 사례가 바로 JS를 통해 동적으로 HTML 구조가 변하는 경우인데요, 만약 사이트를 로딩한 직후에(JS처리가 끝나지 않은 상태에서) JS로 그려지는 HTML 엘리먼트를 가져오려고 하는 경우가 대표적인 사례입니다. (즉, 아직 그리지도 않은 요소를 가져오려고 했기 때문에 생기는 문제인 것이죠.)

![](https://www.dropbox.com/s/sindoea08j0ahgx/%EC%8A%A4%ED%81%AC%EB%A6%B0%EC%83%B7%202017-10-22%2023.39.57.png?dl=1)

그래서 크롤링 코드를 작성할 때 크게 두가지 방법으로 브라우저가 HTML Element를 기다리도록 만들어 줄 수 있습니다.

## Implicitly wait



## Explicitly wait



## <a name='tldr'></a>TL;DR

Implicitly wait은 되도록 쓰지 마시고 Explicitly wait을 아래와 같은 코드를 통해 사용하세요.

