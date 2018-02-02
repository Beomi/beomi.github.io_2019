---
title: "django에 MSSQL 연결하기"
date: 2018-02-02
layout: post
categories:
- Django
- Tips
published: true
image: https://d1sr4ybm5bj1wl.cloudfront.net/img/MSSQL_LOGO.png
---

> 이번 글은 macOS에서 개발하는 경우입니다.

Django와 MSSQL, 그리고 개발 환경이 macOS라면 상당히 연결해 사용하기 어려운 조합입니다.

Django에서 MSSQL을 지원하는 라이브러리는 몇가지 있지만 [Django 공식 문서](https://docs.djangoproject.com/en/2.0/ref/databases/#third-party-notes)에서 MSSQL을 지원하는 ORM 라이브러리로 소개하는 `django-mssql`의 경우 django 1.8까지만 지원하는 문제가 있습니다.

하지만 현재(2018-02-02 기준) 가장 최신 장고 버전은 무려 `2.0.2`입니다. 상당히 오래된 버전만을 지원한다는 문제가 있습니다.

따라서 다른 라이브러리를 사용할 필요가 있습니다. 이번에는 Python3와 Django2.0을 모두 지원하는 `django-pyodbc-azure`를 사용합니다.

## django-pyodbc-azure 설치하기

django-pyodbc-azure는 pip를 통해 아래와 같이 설치할 수 있습니다.

```bash
pip install django-pyodbc-azure
```

django-pyodbc-azure는 `pyodbc`라이브러리를 기반으로 장고 ORM을 이용할 수 있도록 만들어주는데, ODBC는 Native 드라이버를 필요로 하기 때문에 다음과 같이 여러 라이브러리를 설치해줘야 합니다.

> 이번 설치는 HomeBrew를 사용합니다.

```bash
brew install unixodbc
brew install freetds --with-unixodbc

brew tap microsoft/msodbcsql https://github.com/Microsoft/homebrew-mssql-release
brew update
brew install --no-sandbox msodbcsql
brew install mssql-tools
brew install autoconf
```

이제 Django 프로젝트에 MSSQL을 연결해 사용할 수 있습니다.

## django settings.py 파일에 DB 설정하기

위에서 설치해준 django-pyodbc-azure는 `sql_server.pyodbc`라는 엔진 이름으로 django와 연동할 수 있습니다. 아래처럼 settings.py 파일 내 `DATABASE`부분을 수정해주세요.

```python
# settings.py 파일
# 앞뒤 코드 생략
DATABASES = {
    'default': {
        'NAME': 'DataBase이름',
        'ENGINE': 'sql_server.pyodbc',
        'HOST': 'DB의 IP',
        'USER': 'DB접근 ID',
        'PASSWORD': 'DB접근 PW',
    }
}
```

해당 DB에 정상적으로 액세스 할 수 있다면 `migrate`, `runserver`등 장고 명령어가 성공적으로 실행됩니다.
