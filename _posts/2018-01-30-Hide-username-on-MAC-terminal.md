---
title: "macOS 터미널에서 사용자이름 숨기기"
date: 2018-01-30
layout: post
categories:
- macOS
- Tips
published: false
image: 
---

## Before

우리가 macOS를 사용하고 터미널을 켜면 다음과 같이 `username@computername`와 같은 형식으로 나타납니다.

![]({{site.static_url}}/img/2018-01-30-Hide-username-on-MAC-terminal/before.png)

이처럼 계정과 컴퓨터 이름이 나오는 경우 SSH와 같은 원격 접속시에는 어떤 계정으로 어떤 기기에 접속했는지 알 수 있기 때문에 편리하지만 로컬 개발 컴퓨터같은 경우에는 위와같은 정보가 터미널 앞에 붙어있으면 명령어가 길어질 경우 한 줄 내에 나오지 않을 수 있습니다.

> macOS의 터미널 기본 너비는 80자(영문)입니다.

## After

위의 이유로 아래와 같이 `~` 표시만 나오게 하면 좀 더 사용에 편리합니다.

![]({{site.static_url}}/img/2018-01-30-Hide-username-on-MAC-terminal/after.png)

## Solution

만약 여러분이 

