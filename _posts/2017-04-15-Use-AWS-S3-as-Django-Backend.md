---
title: "AWS에 Django Project 배포하기(1): EC2편"
date: 2017-04-15
layout: post
categories:
- Python
- Django
- AWS
published: false
image: https://d1sr4ybm5bj1wl.cloudfront.net/img/AWS/aws_icon.png
---

> 이번 가이드는 AWS에서 EC2/S3/RDS를 연결해 사용하는 것을 다룹니다.

## EC2에 우리가 바라는 것

EC2는 일반적으로 OS가 깔려있는 VPS라고 생각하면 됩니다.

따라서, Django 프로젝트를 배포하는 입장에서는 EC2에 `웹서버`와 `Django App`이 올라가면 된다고 볼 수 있습니다.

이번 가이드에서는 `Apache2`와 `mod-wsgi-py3`을 이용해 

### Django와 웹서버 연결