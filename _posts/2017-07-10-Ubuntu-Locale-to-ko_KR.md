---
title: "Ubuntu Locale 한글로 바꾸기"
date: 2017-07-10
layout: post
categories:
- Ubuntu
published: true
image: /img/ubuntu_logo_512.png
---

> 이번 가이드는 Ubuntu 12/14/16에 적용되는 가이드입니다.

## Locale이란?

Locale이란 세계 각 나라에서 가지고 있는 언어, 날짜, 시간 등에 관해 i18n(국제화)를 통해 같은 프로그램이더라도 OS별로 설정되어있는 것에 따라 어떤 방식으로 출력할지 결정하게 되는 것을 말합니다.

Locale은 단순히 언어 번역뿐만 아니라 시간과 날짜등을 표시하는 형태도 결정하게 되는데요, 예를들어 한국에서 `2017년 7월 10일`이라고 표현한다면 미국에서 `07/10/2017`와 같은 형식으로 표현할 수도 있는 것이죠. 영국이라면 `10/07/2017`이라고 표현할 수 있는 것 처럼요.

이와 같이 프로그래머가 한 코드에서 각 국가와 언어권에 맞도록 출력 형태를 결정하도록 OS에서 안내해 주는 것이 Locale입니다.

## 한국의 Locale

한국의 Locale은 보통 `ko_KR.UTF-8`로 사용합니다. 만약 많이 오래된 서버라면 `ko_KR.EUC-KR`일 수도 있어요.

## Ubuntu의 기본 Locale

만약 여러분이 AWS나 Vultr등의 외국 회사에서 제공하는 우분투 이미지를 사용하고 있다면 아마 기본 설정은 `en-US.UTF-8`일 가능성이 큽니다. 그리고 만약 여러분이 미국권에서 사용하는 형식에 익숙하다면 (그리고 프로그램에서도 Locale이슈가 없다면) 이 설정을 굳이 한글로 바꾸실 필요는 없습니다. 하지만 가끔 업체마다 Locale정보를 공란으로 둔 이미지를 제공하는 경우가 있습니다. 그런 경우 기본값으로 한국어 UTF-8을 이용하는 것은 나쁘지 않은 선택입니다.

## Ubuntu에 Locale변경하기

우선 여러분의 우분투에 깔린 Locale을 확인하려면 아래와 같은 명령어를 입력하면 됩니다:

```bash
locale
```

그리고 한글 패키지를 설치해 줍시다.(이미 깔려있을수도 있습니다.)

```bash
sudo apt-get install language-pack-ko
```

우분투에서 Locale을 변경하는 방법에는 여러가지가 있습니다. 

그 중 첫 번째 방법은 `update-locale`을 사용하는 방법입니다.

```bash
sudo update-locale LANG=ko_KR.UTF-8 LC_MESSAGES=POSIX
```

이 방법을 사용하면 시스템에서 자동으로 LANG에 지정된 한국어 UTF-8로 Locale세팅을 마무리해 줍니다.

두번째 방법으로는 직접 시스템 파일을 수정해주는 방법이 있습니다.

`/etc/default/locale` 파일을 수정하는 것인데요, `nano`나 `vim`등으로 아래와 같이 내용을 수정해주시면 됩니다.

```bash
LANG=ko_KR.UTF-8
LC_MESSAGES=POSIX
```

세번째 방법으로는 `dpkg-reconfigure`을 이용하는 방법입니다. 아래와 같이 명령어를 쳐 주시고 나오는 화면에서 `ko_KR.UTF-8`을 스페이스로 선택(*모양이 뜨면 선택된 것입니다)후 엔터를 눌러 설정을 마무리 해 주세요.

```bash
dpkg-reconfigure locales
```

## 끝났어요!

이 세 가지 방법 모두 시스템에 로그아웃 후 SSH로 재 접속시 적용됩니다. (서버를 Reboot하는 것도 괜찮습니다.)