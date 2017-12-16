---
title: "Django에 Custom인증 붙이기"
date: 2017-02-02
layout: post
categories:
- Python
- Django
published: true
image: https://beomi-tech-blog.s3.ap-northeast-2.amazonaws.com/img/2017-02-02-Django-CustomAuth/authentication.png
---


## 들어가기 전
---

Django는 기본적으로 authentication을 내장하고 있고, User Model을 장고 자체가 가지고 있다.

UserModel의 경우 `settings.py`에서 `AUTH_USER_MODEL`을 커스텀 유저 모델로 지정해주면 프로젝트 전역에서 사용 가능하지만, 이번 글에서는 이 부분이 아니라 `AUTH` 처리를 추가할 수 있는지에 대해 알아볼 것이다.

프로젝트 폴더 구조는 아래와 같다. (`django-admin startproject sample_project`로 생성한 것과 같다. `my_user`라는 폴더를 만들고 안에 `custom_auth.py`와 `my_auth.py`파일을 만든다.)

```sh
.
├── manage.py
├── my_user # 유저 모델을 다룰 곳
│   ├── custom_auth.py
│   └── my_auth.py
└── sample_project # 프로젝트 디렉토리
    ├── __init__.py
    ├── settings.py # 장고 프로젝트 settings
    ├── urls.py
    └── wsgi.py
```


## 사용하는 경우
---

예를들어, "OO커뮤니티 소속이라면, 우리 서비스에서도 커뮤니티 id와 pw로 로그인이 가능하게 하자"가 대표적인 예시가 될 수 있다.

위 문장을 좀더 풀어쓴다면 "OO커뮤니티에 로그인이 가능한 ID"를 받아 "OO커뮤니티의 인증"으로 "우리 서비스에도 로그인" 할 수 있게 하는 것이다.


## 만들어봅시다
---

### 1. check_if_user 함수 만들기

우선 "OO커뮤니티 사이트에 로그인이 가능한 유저인지"를 확인해야 한다.
예를들어 "community-dummy"라는 사이트에 로그인하는 url이 `/login`이고, 유저만 볼 수 있는 페이지가 `/login_requited_page`라고 가정하자.
이 사이트에서는 `/login_requited_page`에 접속시 로그인된 상태라면 HTTP `200`코드를, 로그인 되어있지 않다면 HTTP `401`등의 에러코드를 전송한다고 가정하자.

그렇다면 우리는 파이썬의 `requests`모듈을 이용해 `/login`에 로그인 정보를 `POST`방식으로 전송하고 `/login_requited_page`에 `GET`방식으로 접근해 HTTP코드를 `.status_code`를 통해 확인해보면 된다.
아래 코드를 확인해보자.

> 참고: requests는 `pip install requests`로 설치 가능하다.


```py
# custom_auth.py
import requests

def check_if_user(user_id, user_pw):
    payload = {
        'user_id': str(user_id),
        'user_pw': str(user_pw)
    }
    with requests.Session() as s:
        s.post('https://community-dummy.com/login', data=payload)
        auth = s.get('https://community-dummy.com/login_requited_page')
        if auth.status_code == 200: # 성공적으로 가져올 때
            return True
        else: # 로그인이 실패시
            return False
```

우리는 이제 이 코드를 통해 유저가 우리 사이트에 입력한 id와 pw가 정확한(OO커뮤니티에 로그인 가능한)것인지를 확인할 수 있다.

### 2. 커스텀 UserBackend 만들기

우선 django 프로젝트가 사용하는 User모델을 가져오자.

```py
# my_auth.py
from django.contrib.auth import get_user_model

UserModel = get_user_model()
```

위 방식으로 사용할 경우 Django의 기본 UserModel인 `django.contrib.auth.models.User` 뿐 아니라 `settings.py`에 따로 지정한 `AUTH_USER_MODEL` 클래스를 가져오게 된다.

> 참고: `get_user_model`와 `AUTH_USER_MODEL`은 다르다.
> `django.contrib.auth`의 `get_user_model`은 유저모델 class를 반환하는 반면,
> `django.conf.settings`의 `AUTH_USER_MODEL`은 유저모델 지정을 str로 반환한다.

그리고 위에서 만든 `custom_auth.py`에서 `check_if_user`를 import해주자.

```py
# my_auth.py
from django.contrib.auth import get_user_model
from .custom_auth import check_if_user # custom Auth성공시 True 아니면 False

UserModel = get_user_model() # django.contrib.auth.models.User대신 사용
```

이제 장고가 `AUTHENTICATION_BACKENDS`로서 추가적으로 사용할 `UserBackend` class를 만들어보자.

`UserBackend`클래스는 최소한 `authenticate`, `user_can_authenticate`, `get_user`라는 함수는 있어야 동작한다.

`authenticate`함수는 `self`, `username`, `password`를 인자로 받은 후, 정상적으로 인증된 경우 `user 객체`를 '하나' 반환해야 하고, 없는 경우 `None`값을 반환해야 한다.

`user_can_authenticate`함수는 `user`객체를 인자로 받아서 `is_active`값을 가져와 활성화된 유저인지를 체크한다. (유저가 없거나 활성화된 경우 `True`, 비활성화된 경우 `False`)

`get_user`함수는 `user_id`를 인자로 받아 User객체를 `pk`로 참조해 `user`객체를 반환한다. 없는경우 `None`을 반환한다.

위 함수들을 작성하면 아래와 같다.

```py
# my_auth.py
from django.contrib.auth import get_user_model
from .custom_auth import check_if_user # custom Auth성공시 True 아니면 False

UserModel = get_user_model()

class UserBackend(object):
    def authenticate(self, username=None, password=None):
        if check_if_user(username, password): # OO커뮤니티 사이트 인증에 성공한 경우
            try: # 유저가 있는 경우
                user = UserModel.objects.get(username=username)
            except UserModel.DoesNotExist: # 유저 정보가 없지만 인증 통과시 user 생성
                user = UserModel(username=username)
                user.is_staff = False
                user.is_superuser = False
                user.save()
                # 여기서는 user.password를 저장하는 의미가 없음.(장고가 관리 못함)
            return user
        else: # OO 커뮤니티 사이트 인증에 실패한 경우, Django기본 User로 감안해 password검증
            try:
                user = UserModel.objects.get(username=username)
                if user.check_password(password) and self.user_can_authenticate(user):
                    return user
            except:
                return None

    def user_can_authenticate(self, user):
        is_active = getattr(user, 'is_active', None) # 유저가 활성화 되었는지
        return is_active or is_active is None # 유저가 없는 경우 is_active는 None이므로 True

    def get_user(self, user_id):
        try:
            return UserModel.objects.get(pk=user_id) # 유저를 pk로 가져온다
        except UserModel.DoesNotExist:
            return None
```

### 3. settings.py에 AUTHENTICATION_BACKENDS 추가하기

장고에서 기본적으로 관리해주는 `AUTHENTICATION_BACKENDS`에는 `django.contrib.auth.backends.ModelBackend`가 있다. 하지만 위에서 우리가 만든 UserBackend를 추가해줘야 한다.

`AUTHENTICATION_BACKENDS`는 기본적으로 list로 구성되어있으며, 적혀진 순서대로 위에서부터 Auth을 진행한다.(실패시 다음 auth backend를 이용)

아래 코드와 같이 `settings.py` 파일 아래에 추가해 주자.

```py
# settings.py
AUTHENTICATION_BACKENDS = [
    'my_user.my_auth.UserBackend', # 우리가 만든 AUTH를 먼저 검사
    'django.contrib.auth.backends.ModelBackend', # Django가 관리하는 AUTH
]
```

이렇게 추가해 줌으로서 django는 우리의 `UserBackend`를 이용해 유저를 관리하게 된다.


## 마무리 코드
---

custom_auth 파일(진짜 OO커뮤니티 유저인가?)

```py
# custom_auth.py
import requests

def check_if_user(user_id, user_pw):
    payload = {
        'user_id': str(user_id),
        'user_pw': str(user_pw)
    }
    with requests.Session() as s:
        s.post('https://community-dummy.com/login', data=payload)
        auth = s.get('https://community-dummy.com/login_requited_page')
        if auth.status_code == 200: # 성공적으로 가져올 때
            return True
        else: # 로그인이 실패시
            return False
```

my_auth 파일 (우리가 만든 UserBackend)

```py
# my_auth.py
from django.contrib.auth import get_user_model
from .custom_auth import check_if_user # custom Auth성공시 True 아니면 False

UserModel = get_user_model()

class UserBackend(object):
    def authenticate(self, username=None, password=None):
        if check_if_user(username, password): # OO커뮤니티 사이트 인증에 성공한 경우
            try: # 유저가 있는 경우
                user = UserModel.objects.get(username=username)
            except UserModel.DoesNotExist: # 유저 정보가 없지만 인증 통과시 user 생성
                user = UserModel(username=username)
                user.is_staff = False
                user.is_superuser = False
                user.save()
                # 여기서는 user.password를 저장하는 의미가 없음.(장고가 관리 못함)
            return user
        else: # OO 커뮤니티 사이트 인증에 실패한 경우, Django기본 User로 감안해 password검증
            try:
                user = UserModel.objects.get(username=username)
                if user.check_password(password) and self.user_can_authenticate(user):
                    return user
            except:
                return None

    def user_can_authenticate(self, user):
        is_active = getattr(user, 'is_active', None) # 유저가 활성화 되었는지
        return is_active or is_active is None # 유저가 없는 경우 is_active는 None이므로 True

    def get_user(self, user_id):
        try:
            return UserModel.objects.get(pk=user_id) # 유저를 pk로 가져온다
        except UserModel.DoesNotExist:
            return None
```

장고의 프로젝트 settings.py파일

```py
# settings.py
AUTHENTICATION_BACKENDS = [
    'my_user.my_auth.UserBackend', # 우리가 만든 AUTH를 먼저 검사
    'django.contrib.auth.backends.ModelBackend', # Django가 관리하는 AUTH
]
```
