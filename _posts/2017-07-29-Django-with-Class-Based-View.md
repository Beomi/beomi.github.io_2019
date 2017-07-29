---
title: "Class Based View로 빠른 장고 개발하기(1): CBV의 종류"
date: 2017-07-29
layout: post
categories:
- Django
published: false
image: /img/use-autoenv.jpg
---

> 

## Django에서의 `View`

장고에서 view는 MVC모델에서의 Controller에 해당합니다. 즉 HTTP request에 따라 어떤 데이터를 response로 해줄지 결정을 해주는 부분입니다.

장고가 파이썬 기반인 만큼 장고의 뷰를 Function(함수) 기반으로 작성할 수도 있고 Class(클래스) 기반으로 작성할 수도 있습니다. View가 '요청을 받는다 -> 처리한다 -> 요청의 답을 보내준다'라는 과정을 바탕으로 하는 것을 생각해보면 사실 함수의 입력값(요청 받기)을 함수의 결과(요청의 답)로 보내주는 과정과 거의 흡사하다고 볼 수 있습니다.

장고에서 `CBV`라고 불리는 뷰도 이와 동일한 과정을 거칩니다. 하지만 클래스라는 틀 안에서 `get`, `post`등의 내부 함수가 구현되어있고 