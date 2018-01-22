---
title: "간단한 node.js 앱 AWS Lambda에 배포하기"
date: 2017-08-26
layout: post
categories:
- tips
published: false
image: https://d1sr4ybm5bj1wl.cloudfront.net/img/2017-09-01-Deploy-simple-node-to-AWS-Lambda.png
---

## 들어가기 전

AWS Lambda(람다)는 서버리스 아키텍처를 구성하기 위해 종종 사용하는 AWS의 서비스입니다. Lambda는 서비스 아키텍쳐를 구성하는데 있어 고전적인 EC2나 VPS와 달리 서버 인스턴스가 매 요청시마다 새로 켜지고 응답을 보낸 후 꺼지는 방식으로 동작합니다.

따라서 Stateless라고 말할 수 있으며, 유저를 인증하는 방법도 세션이 아닌 토큰 등을 사용합니다.

Lambda에서는 Node 6버전(최신 LTS)을 지원하고 있으며 이에 따라 Node로 만들어진 앱을 바로 서버에 올릴 수 있습니다.

기본적으로 Lambda가 맡고있는 역할은 보통의 백엔드 프레임워크들이 갖고 있는 URL Routing기능이 기본적으로 들어가있으며 각 URL에 따라 다른 함수를 실행하고 그에 따른 결과물을 반환하는 형태로 동작합니다. 하지만 기존에 express등의 프레임워크를 사용한 앱을 서버에 올리고자 한다면 Proxy형태로 Url전체를 Lambda 앱에 전송해 진행을 해 주어야 합니다.

> 하지만 이렇게 하는 방법은 사실 Lambda를 무겁게 만드는 나쁜 요인입니다. Lambda와 