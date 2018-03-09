---
title: "Django: Truncated or oversized response headers received from daemon process 에러 해결법"
date: 2018-03-09
layout: post
categories:
- python
- django
- tips
published: true
image: https://d1sr4ybm5bj1wl.cloudfront.net/img/2018-03-09-Truncated_or_oversized_response_headers_received_from_daemon_process_django_wsgi.png
---

## 문제 발생 환경

- OS: Ubuntu 16.04 LTS
- Python 3.5.2
- Django 2.0.2
- Apache HTTPd 2.4
- numpy / Pandas / pymssql 등 사용중

## 문제의 발생

장고 배포를 마친 뒤 배포 서버에 접속시 화면이 뜨지 않고 `500`에러가 났던 상황.

```shell
Timeout when reading response headers from daemon process 'djangoproject': /home/ubuntu/djangoproject/djangoproject/wsgi.py
```

에러 로그로 살펴보면 위와 같이 "Timeout when reading response headers from daemon process"이라는 문제가 발생했다.

## 문제 원인

Numpy나 Pandas와 같은 C 의존 라이브러리들은 파이썬 인터프리터 중 메인 인터프리터에서 사용해야 한다. 만약 `mod_wsgi`등을 통해 생성된 서브 인터프리터를 사용할 경우 GIL로 인한 Deadlock이 발생하거나 정확하지 않은 결과, 혹은 파이썬 인터프리터의 예기치 못한 종료를 유발할 수 있다.

## 해결법

따라서 WSGI Application에서 사용할 파이썬 인터프리터에다 시스템의 메인 인터프리퍼를 지정해주면 된다.

`/etc/apache2/apache2.conf` 경로의 파일 제일 아래에 아래 코드를 추가해준다.

```
WSGIApplicationGroup %{GLOBAL}
```

코드를 추가해 준 뒤 Apache2를 재시작(`service apache2 restart`)한다.

## Refs

- [(Serverfault) WSGI : Truncated or oversized response headers received from daemon process](https://serverfault.com/questions/844761/wsgi-truncated-or-oversized-response-headers-received-from-daemon-process)
- [(Stackoverflow) Django Webfaction 'Timeout when reading response headers from daemon process'](https://stackoverflow.com/questions/40413171/django-webfaction-timeout-when-reading-response-headers-from-daemon-process/40414207#40414207)
- [(Serverfault) Non-responsive apache + mod_wsgi after installing scipy](https://serverfault.com/questions/514242/non-responsive-apache-mod-wsgi-after-installing-scipy/514251#514251)
- [(Google Code) summary Common problems with WSGI applications](https://code.google.com/archive/p/modwsgi/wikis/ApplicationIssues.wiki#Python_Simplified_GIL_State_API)
