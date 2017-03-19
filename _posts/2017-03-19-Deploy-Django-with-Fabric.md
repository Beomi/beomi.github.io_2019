---
title: "Fabric으로 Django 배포하기"
date: 2017-03-19 17:30:00+09:00
layout: post
categories:
- Python
- Fabric
- Django
published: false
image: /img/old_post/python-fabric-logo.jpg
---

> 이번 가이드는 완성된 상태의 Django 프로젝트가 있다고 가정합니다.

# Fabric으로 Django 배포하기

Django는 내장된 `runserver`라는 개발용 웹 서버가 있습니다. 하지만 개발용 웹 서버를 상용 환경에서 사용하는 것은 여러가지 문제를 가져옵니다. 메모리 문제등의 성능 이슈부터 Static file서빙의 보안 문제까지 다양한데요, 이 때문에 Django는 웹 서버(ex: `Apache2` `NginX`등)를 통해 배포하게 됩니다.

하지만 이러한 배포작업은 아마존 EC2등의 VPS나 리얼 서버에서 `Apache2`를 깔고, `python3`와 `mod_wsgi`등을 깔아야만 동작하기 때문에 배포 자체가 어려움을 갖게 됩니다. 또한 SSH에 접속히 직접 명령어를 치는 경우 오타나 실수등으로 인해 정상적으로 작동하지 않는 경우도 부지기수입니다.

따라서 이러한 작업을 자동화해주는 도구가 바로 Fabric이고, 이번 가이드에서는 Django 프로젝트를 Vultr VPS, Ubuntu에 올리는 방법을 다룹니다.

## Vultr VPS 생성하기

[Vultr](vultr.com)는 VPS(가상서버) 제공 회사입니다. 최근 가격 인하로 유사 서비스 대비 절반 가격에 이용할 수 있어 가성비가 좋습니다.

사용자가 많지 않은 (혹은 혼자 사용하는..) 서비스라면 최소 가격인 1cpu 512MB의 월 $2.5짜리를 이용하시면 됩니다.

Vultr는 일본 Region에 서버가 있어 한국에서 사용하기에도 핑이 25ms정도로 양호합니다.

## `django` 유저 만들기(sudo권한 가진 유저 만들기)

Fabric을 사용할 때 초기에 `apt`를 이용해 패키지를 설치해야 할 필요가 있습니다.

하지만 처음에 제공되는 `root`계정은 사용하지 않는 것을 보안상 추천합니다. 따라서 우리는 `sudo`권한을 가진 `django`라는 유저를 생성하고 Fabric으로 진행해 보겠습니다.

```bash
adduser django # `django`라는 유저를 만듭니다.
adduser django sudo # django유저를 `sudo`그룹에 추가합니다.
```

> 비밀번호를 만드는 것을 제외하면 나머지는 빈칸으로 만들어 두어도 무방합니다.

## Fabric 설치하기

`Fabric`은 기본적으로 서버가 아닌 클라이언트에 설치합니다. 개념상 로컬에서 SSH로 서버에 접속해 명령을 처리하는 것이기 때문에 당연히 SSH 명령을 입려하는 로컬에 설치되어야 합니다.

Fabric은 공식적으로는 Python2.7만을 지원합니다. 하지만 이 프로젝트를 Fork해서 Python3을 지원하는 프로젝트인 `Fabric3`이 있습니다. 이번 가이드에서는 이 `Fabric3`을 설치합니다.

```sh
pip3 install fabric3
# 혹은
python3 -m pip install fabric3
```

## fabfile 만들기

> 이번 가이드는 [https://gist.github.com/Beomi/945cd905175c3b21370f8f04abd57404](https://gist.github.com/Beomi/945cd905175c3b21370f8f04abd57404)의 예제를 설명합니다.

Fabric을 설치하시면 `fab`이라는 명령어를 사용할 수 있습니다. 이 명령어는 `fab some_func`라는 방식을 통해 `fabfile.py`파일 안의 함수를 실행할 수 있습니다.

fabfile은 기본적으로 `manage.py`파일와 같은 위치인 프로젝트 폴더에 두시는 것을 권장합니다.

```py
from fabric.contrib.files import append, exists, sed, put
from fabric.api import env, local, run, sudo
```

우선 fabric에서 사용하는 API들을 import해줍니다.

`fabric.contrib.files`에서는 원격(혹은 로컬)의 파일을 관리하는 API입니다. `fabric.api`는 Fabric에서 사용하는 환경이나, SSH로 연결한 원격 서버에서 명령어를 실행하는 API입니다.


