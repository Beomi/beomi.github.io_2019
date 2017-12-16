---
title: "Django에 Social Login와 Email유저 함께 이용하기"
date: 2017-03-22
layout: post
categories:
- Python
- Django
published: true
image: https://beomi-tech-blog.s3.ap-northeast-2.amazonaws.com/img/2017-02-08-Setup-SocialAuth-for-Django/social_login.png
---

> `django-custom-user`와 `social-auth-app-django`(구 `python-social-auth`)를 이용해 이메일 기반 유저와 소셜 로그인으로 로그인 한 유저를 하나처럼 사용하는 방법입니다.

> 장고에 소셜 로그인을 붙이는 가이드는 [Django에 Social Login 붙이기: Django세팅부터 Facebook/Google 개발 설정까지](/2017/02/08/Setup-SocialAuth-for-Django/) 포스팅에서 찾으실 수 있습니다.

# Django + SocialLogin + Email as User

웹 서비스를 제공할 때 여러가지 로그인 방법을 구현할 수 있습니다. 아이디/패스워드 기반의 방식, 페이스북과 구글등의 OAuth를 이용한 소셜 로그인 방식 등이 있습니다.

장고 프로젝트를 만들 때 `django-custom-user`등의 패키지를 이용하면 이메일 주소를 Unique Key로 사용해 이메일 주소로 로그인을 할 수 있도록 만들어 줍니다.

> `django-custom-user`에 관한 문서는 [Django Custom User GitHub](https://github.com/jcugat/django-custom-user#django-custom-user)에서 확인하실 수 있습니다.

하지만, `social-auth-app-django`를 통해 유저를 생성 할 경우 OAuth Provider에 따라 다른 User를 생성합니다. 즉, 같은 이메일 주소를 가지고 있는 유저라 하더라도 페이스북을 통해 로그인 한 유저와 구글을 통해 로그인 한 유저는 다르게 다뤄진다는 뜻입니다.

> 사실 이메일 주소를 신뢰하지 않고 Provier마다 다른 유저로 생성하는 것이 기본으로 되어있는 이유는 Oauth Provier의 신뢰 문제입니다. 모든 Oauth Provier가 가입한 유저의 Email의 실 소유권을 확인하지는 않기 때문입니다.

이를 해결하고 같은 이메일을 통해 로그인한 유저는 모두 같은 유저로 취급하기 위해서는 장고 프로젝트 폴더의 `settings.py`파일 안에서 `social-auth-app-django`의 Pipeline설정을 변경해 줘야 합니다.

```python
SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',
    'social_core.pipeline.social_auth.associate_by_email',  # <--- 이 줄이 핵심입니다.
    'social_core.pipeline.user.create_user',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',
)
```

`SOCIAL_AUTH_PIPELINE`은 `settings.py`내에는 기본적으로 지정이 해제되어있습니다. 따라서 변수가 없는 경우 위 코드 전체를 `settings.py`파일 끝에 덧붙이시면 됩니다.

> 참고: [Python Social Auth: Associate users by Email](http://python-social-auth.readthedocs.io/en/latest/use_cases.html#associate-users-by-email)
