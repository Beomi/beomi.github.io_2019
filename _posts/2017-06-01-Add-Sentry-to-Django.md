---
title: "배포한 Django 서비스 Exception Sentry로 받아보기"
date: 2017-06-01
layout: post
categories:
- django
published: true
image: https://d1sr4ybm5bj1wl.cloudfront.net/img/Django/sentry.jpg
---

> 이번 포스팅은 `wsgi`기반으로 동작하는 `django`서비스를 대상으로 합니다.

Django 서비스를 실제 서버에 배포하면 보안을 위해 프로젝트 폴더의 `settings.py`파일 안의 `DEBUG`항목을 `False`로 두고 배포합니다. 이렇게 디버그모드를 끌 경우 장고에서 기본적인 보안을 제공해 줍니다. 그러나 만약 View나 Model에서 Exception이 발생했을 경우 클라이언트에 흰색의 500에러 화면만을 띄워줍니다.

이 경우 개발자에게도 장고의 에러 화면을 보여주지 않습니다. 따라서 Exception이 발생할 경우 개발자(혹은 운영자)에게 에러를 전송할 필요가 있습니다. `wsgi` 기반으로 서버를 구동할 경우 에러로그는 Apache2나 NginX등의 웹서버의 접근/에러로그가 있으며 Wsgi의 에러로그로 두가지가 있습니다.

장고서버의 경우에는 Wsgi의 에러로그에 로그를 쌓습니다. 그러나, Django 프로젝트에 `LOGGERS` 설정값을 추가해줘야 하며 에러 트래킹을 따로 설정해줘야 합니다.

이때 사용할 수 있는 것이 Sentry와 같은 서비스입니다.

> 이번 가이드는 [Sentry for Django](https://docs.sentry.io/clients/python/integrations/django/)를 기반으로 진행합니다.

## Sentry 설치하기

우선 `raven`을 설치해 줍니다. 

> `raven`은 Sentry를 위한 Python패키지입니다. 

```sh
pip install raven --upgrade
```

## Sentry `settings.py`에 설정하기

장고 프로젝트의 `settings.py`파일 안 `INSTALLED_APPS`에 아래 줄을 추가해줍니다.

```py
INSTALLED_APPS = [
    # 기존 앱 가장 아래에 추가해주세요.
    'raven.contrib.django.raven_compat',
]
```

이제 Sentry용 환경변수를 추가해 줍시다. 아래 `DSN_URL`은 Sentry에 로그인 하신 후 [Sentry for Django](https://docs.sentry.io/clients/python/integrations/django/#setup)의 코드 부분을 복사하면 알 수 있습니다.

```py
# settings.py 파일 import문 아래에 raven을 import해주세요.
import os
import raven

# import아래 환경변수를 설정해주세요. 이 URL은 위 Sentry for Django에서 바로 찾을 수 있습니다.
DSN_URL = 'https://sampleurl1234141534samplesample:somemoreurl12341235dfaetr@sentry.io/123456'

# 기타 설정들(생략...)

# settings.py 파일 가장 아래에 RAVEN_CONFIG를 추가해주세요.
RAVEN_CONFIG = {
    'dsn': '{}'.format(DSN_URL), # DSN_URL을 위에 적어주셔야 동작합니다.
    'release': raven.fetch_git_sha(BASE_DIR), # Django가 Git으로 관리되는 경우 자동으로 커밋 버전에 따른 트래킹을 해줍니다.
}
```

## Sentry `wsgi.py`에 설정하기

이제 장고 프로젝트 폴더 안의 `wsgi.py` 파일을 아래와 같이 수정해봅시다.

```py
import os

from django.core.wsgi import get_wsgi_application
from raven.contrib.django.raven_compat.middleware.wsgi import Sentry

# 이 부분은 여러분의 장고 프로젝트 이름을 쓰세요..
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "장고프로젝트이름.settings")

# get_wsgi_application을 Sentry()로 감싸주세요.
application = Sentry(get_wsgi_application())
```

자, 이제 Sentry 사용을 위한 기본적인 설정이 끝났습니다. 여러분의 서비스를 다시 원래 서버에 배포해보세요.

## Exception이 발생하면..

이제 여러분이 잡아주지 않은 Exception이 발생할 경우 아래와 같이 이메일이 옵니다.

![sentry django integrity error log mail]({{site.static_url}}/img/Django/sentry_mail.jpeg)

이메일의 Issue 링크를 클릭하면 아래와 같이 에러로그 페이지가 나옵니다.

![Sentry django integrity error log web page]({{site.static_url}}/img/Django/sentry_web.png)

## 조금 더 알아보기

이번 포스팅에서는 장고의 Wsgi에서 발생하는 에러(Exception)을 Sentry 미들웨어를 통해 관리합니다. 그러나 유저에게 500페이지를 보여주는것은 여전합니다.

만약 여러분이 미리 잡아준 상황을 Sentry로 보내고 싶으시다면 [Sentry를 logging와 함께 쓰기](https://docs.sentry.io/clients/python/integrations/django/#integration-with-logging)를 참고하세요.
