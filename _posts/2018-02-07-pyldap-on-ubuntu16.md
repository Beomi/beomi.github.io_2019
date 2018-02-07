---
title: "ubuntu16에 pyldap 설치하기"
date: 2018-02-07
layout: post
categories:
- Ubuntu
- Tips
- LDAP
published: true
image: https://d1sr4ybm5bj1wl.cloudfront.net/img/pyldap_on_ubuntu.png
---

## Problem

`pyldap`라이브러리를 이용해 AD Proxy/LDAP서버에 연결하기 위해서는 단순히 `pip`로만 설치하는 것 외에 사전으로 설치해야 하는 항목이 있다.

만약 설치가 되어있지 않으면 아래와 같이 에러가 난다.

```sh
In file included from Modules/LDAPObject.c:8:0:
Modules/errors.h:7:18: fatal error: lber.h: No such file or directory
compilation terminated.
error: command 'x86_64-linux-gnu-gcc' failed with exit status 1
```

## Solution

```sh
sudo apt install python3-dev # python3
sudo apt install python3-pip # python3 pip3
sudo apt install build-essential # for c/cpp build
sudo apt install libsasl2-dev
sudo apt install libldap2-dev
sudo apt install libssl-dev
```

`apt`로 위 라이브러리 설치 후 아래와 같이 `pip3`으로 `pyldap`을 설치하면 된다.

```sh
pip3 install pyldap
```
