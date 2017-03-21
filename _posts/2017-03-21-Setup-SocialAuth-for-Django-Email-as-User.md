---
title: "Django에 Social Login와 Email유저 함께 이용하기"
date: 2017-03-21 15:45:00
layout: post
categories:
- Python
- Django
published: true
image: /img/2017-02-08-Setup-SocialAuth-for-Django/social_login.png
---

# Django + SocialLogin + Email as User

웹 서비스를 제공할 때 여러가지 로그인 방법을 구현할 수 있습니다. 아이디/패스워드 기반의 방식, 페이스북과 구글등의 OAuth를 이용한 소셜 로그인 방식 등이 있습니다.

장고 프로젝트를 만들 때 `django-custom-user`등의 패키지를 이용하면 


http://python-social-auth.readthedocs.io/en/latest/use_cases.html#associate-users-by-email