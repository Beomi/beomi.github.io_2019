---
title: "Django에 Social Login 붙이기: Django세팅부터 Facebook/Google 개발 설정까지"
date: 2017-02-08
layout: post
categories:
- python
- django
published: true
image: https://d1sr4ybm5bj1wl.cloudfront.net/img/2017-02-08-Setup-SocialAuth-for-Django/social_login.png
---

Django등 웹 서비스를 제공하며 항상 다루게 되는 주제가 있습니다. 유저를 우리 서비스의 유저 모델을 통해 직접 가입시키느냐, 혹은 타사의 oAuth를 이용한 Social Login을 붙여 가입없이(혹은 최소화) 서비스를 이용할 수 있도록 유도 하느냐 등입니다.

Django에서 이러한 Social Login을 이용하기 위한 라이브러리는 여러개가 있었고, 대표적으로는 `django-social-auth`와 `python-social-auth`가 있었지만, 두 프로젝트 모두 현재(2017.02.08기준) Deprecated되었고 이 프로젝트들은 `python-social-auth`가 org자체로 이전해 `social-auth-app-django`로 바뀌었습니다.

한편 `-social-auth`들의 대체재로 `django-allauth`가 있는데, 올해 1월에도 새 버전 릴리즈가 있는만큼 활동적인 프로젝트입니다. (하지만 이번 글에서는 다루지 않습니다.)

이번 게시글에서는 `social-auth-app-django`을 이용해 Django 프로젝트에 social login을 붙여봅니다.

참조한 공식 docs는 [python-social-auth configuration django](http://python-social-auth.readthedocs.io/en/latest/configuration/django.html)에서 볼 수 있습니다.

> 참고: `social-auth-app-django`는 pip패키지 이름이며, 프로젝트 이름은 `python-social-auth`로 동일합니다.

## 설치하기
---

```sh
pip install social-auth-app-django
```

Django의 기본 ORM을 이용하고 있다면 `social-auth-app-django`를 pip로 설치하면 됩니다.

## settings.py 설정하기
---

### INSTALLED_APPS 추가하기

settings.py에 `social_django`를 추가해줍니다.

```py
INSTALLED_APPS = (
    ...
    'social_django',
    ...
)
```

앱 추가후 migrate를 해줘야 정상적으로 Social Auth용 DB Table이 생성됩니다.

```sh
python manage.py migrate
```

### AUTHENTICATION_BACKENDS 추가하기

Social Login은 기존 유저모델과 함께 사용이 가능합니다. 하지만 기본 유저 ModelBackend를 사용하지 않고 독자적인 ModelBackend를 사용하기 때문에 settings.py의 AUTHENTICATION_BACKENDS에 Social login용 Backends를 추가해줘야 합니다.

```py
AUTHENTICATION_BACKENDS = [
    'social_core.backends.google.GoogleOAuth2', # Google
    'social_core.backends.facebook.FacebookOAuth2', # Facebook
    ...
    'django.contrib.auth.backends.ModelBackend', # Django 기본 유저모델
]
```

> `django.contrib.auth.backends.ModelBackend`가 있어야 `createsuperuser`로 만들어진 계정의 로그인이 가능해집니다.

### Social Login용 URL Namespace 지정

최상위 프로젝트 `urls.py`에 지정할 social login의 namespace를 지정해줍니다. 또한, Login 후 어떤 URL로 장고가 유저를 Redirect시킬지 지정해 줍니다.

```py
SOCIAL_AUTH_URL_NAMESPACE = 'social'

LOGIN_REDIRECT_URL='/'
```

> 꼭 namespace가 'social'일 필요는 없습니다. 하지만 가이드에서는 'social'을 사용하기에 아래 urls.py 설정에서도 동일하게 사용할 예정입니다.

### Social Login을 위한 API Key/Secret 설정하기

우선 프로젝트 BASE_DIR(`manage.py`파일이 있는 폴더)에 `envs.json`이라는 이름의 환경변수를 담은 json 파일을 만들어 줍니다.

```json
{
  "FACEBOOK_KEY":"숫자숫자숫자들",
  "FACEBOOK_SECRET":"숫자영어숫자영어들",
  "GOOGLE_KEY":"숫자-영어.apps.googleusercontent.com",
  "GOOGLE_SECRET":"숫자영어대문자들"
}
```

당연하게도 위 파일은 실제 동작하는 Key와 Secret이 아닙니다.

Social Login을 사용하기 위해 Google에서는 [Google+ API](https://console.developers.google.com/apis/api/plus.googleapis.com)를 활성화 하고 [OAuth 2.0 클라이언트 ID](https://console.developers.google.com/apis/credentials)를 '웹 애플리케이션'으로 생성해 API Key/Secret을 발급받아야 합니다.

> Google Login은 Google+ API에 연결되어있기 때문에 다른 Login API는 없습니다.

Facebook의 경우에는 [Facebook for Developers](https://developers.facebook.com/)에서 새 앱 추가 후 'Facebook 로그인' 제품을 활성화 시킨 후 앱의 대시보드에서 앱 ID와 앱 시크릿 코드를 받아 이용하면 됩니다.

두 서비스 모두 지정된 url에서만 동작하기 때문에 Google의 경우에는 'OAuth 2.0 클라이언트 ID'에서 '승인된 리디렉션 URI'에 `http://localhost:8000/complete/google-oauth2/`을 추가해줘야 하며, Facebook의 경우에는 'Facebook 로그인'의 '클라이언트 OAuth 설정'에 있는 '유효한 OAuth 리디렉션 URI'에 `http://localhost:8000/`을 추가해주면 됩니다.

> 위 설정을 모두 하지 않을 경우 40x번대 에러가 발생합니다.

이제 위에서 만든 `envs.json`파일을 환경변수로 사용해야 합니다. `settings.py`파일 최상위에 이와 같은 코드를 적용해 줄 경우, 개발용 `envs_dev.json`와 배포용 `envs.json`, 그리고 환경변수로 관리되는 경우 모두 커버가 가능합니다.

```py
import os
import json

from django.core.exceptions import ImproperlyConfigured

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Env for dev / deploy
def get_env(setting, envs):
    try:
        return envs[setting]
    except KeyError:
        error_msg = "You SHOULD set {} environ".format(setting)
        raise ImproperlyConfigured(error_msg)

DEV_ENVS = os.path.join(BASE_DIR, "envs_dev.json")
DEPLOY_ENVS = os.path.join(BASE_DIR, "envs.json")

if os.path.exists(DEV_ENVS): # Develop Env
    env_file = open(DEV_ENVS)
elif os.path.exists(DEPLOY_ENVS): # Deploy Env
    env_file = open(DEPLOY_ENVS)
else:
    env_file = None

if env_file is None: # System environ
    try:
        FACEBOOK_KEY = os.environ['FACEBOOK_KEY']
        FACEBOOK_SECRET = os.environ['FACEBOOK_SECRET']
        GOOGLE_KEY = os.environ['GOOGLE_KEY']
        GOOGLE_SECRET = os.environ['GOOGLE_SECRET']
    except KeyError as error_msg:
        raise ImproperlyConfigured(error_msg)
else: # JSON env
    envs = json.loads(env_file.read())
    FACEBOOK_KEY = get_env('FACEBOOK_KEY', envs)
    FACEBOOK_SECRET = get_env('FACEBOOK_SECRET', envs)
    GOOGLE_KEY = get_env('GOOGLE_KEY', envs)
    GOOGLE_SECRET = get_env('GOOGLE_SECRET', envs)
```

이와 같이 사용할 경우, APACHE웹서버 등에서 시스템 환경변수를 불러오지 못하는 상황이거나, HEROKU나 PythonAnywhere와 같은 PaaS에서도 Django코드와 API키들을 완전히 분리해 사용할 수 있습니다.

위에서 지정한 FACEBOOK_KEY들을 SocialLogin에 할당해 줍니다.

```py
# SocialLogin: Facebook
SOCIAL_AUTH_FACEBOOK_KEY = FACEBOOK_KEY
SOCIAL_AUTH_FACEBOOK_SECRET = FACEBOOK_SECRET
SOCIAL_AUTH_FACEBOOK_SCOPE = ['email']
SOCIAL_AUTH_FACEBOOK_PROFILE_EXTRA_PARAMS = {
  'fields': 'id, name, email'
}

# SocialLogin: Google
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = GOOGLE_KEY
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = GOOGLE_SECRET
SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = ['email']
```

위 코드는 가장 기본적인 'email'을 유저 식별도구로 받아옵니다.

>  \_PROFILE_EXTRA_PARAMS를 이용해 다른 Field를 받아올 수도 있습니다. (필수 아님)

## project폴더의 urls.py 설정하기(최상위 urls.py)
---

이제 프로젝트 폴더의 urls.py에 Social Login이 사용할 url들을 등록하고 namespace를 지정해 Template에서 사용할 수 있도록 설정해야 합니다.

```py
from django.conf.urls import url, include # url뿐 아니라 include를 import해야 합니다.
from django.conf import settings
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url('', include('social_django.urls', namespace='social')), # 이 줄을 등록해주면 됩니다.
]
```

이와 같이 `social_django.urls`를 include하고 'social' namespace를 등록해 줍니다.

## Template에서 Social Login url 호출하기
---

위 코드들을 추가해주는 것 만으로도 기본적인 Social Login기능은 완성되었습니다. 이제 Template에서 호출을 해봅시다.

```html
{% raw %}<a href="{% url "social:begin" "google-oauth2" %}"><button class="btn btn-danger" style="width: 40%">G+ Login</button></a>
<a href="{% url "social:begin" "facebook" %}"><button class="btn btn-primary" style="width: 40%">FB Login</button></a>{% endraw %}
```

이와 같이 button을 등록해 호출할 수 있습니다.

위 버튼을 누를 경우 각각 Google/Facebook의 Social Login페이지로 넘어갑니다.

## 수고하셨습니다!
---

위 코드만으로도 약간의 조작을 통해 더 멋진 Social Login기능을 구현하실 수 있으리라 생각합니다.

Happy Coding!
