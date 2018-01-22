---
title: "[번역]셀러리 입문하기"
date: 2017-03-19
layout: post
categories:
- Python
- Celery
- CeleryDocs
- Translation
published: true
image: https://d1sr4ybm5bj1wl.cloudfront.net/img/2017-03-19-Celery-Getting-Started/celery.jpg
---

> 글 작성 시점 최신 버전 `v4.0.2`의 문서입니다.

원문: [http://docs.celeryproject.org/en/latest/getting-started/introduction.html](http://docs.celeryproject.org/en/latest/getting-started/introduction.html)

# 셀러리 입문하기
---

- 태스크 큐란 무엇인가? (What’s a Task Queue?)

- 뭐가 필요한가요? (What do I need?)

- 시작하기 (Get Started)

- 셀러리는.. (Celery is..)

- 셀러리의 기능들 (Features)

- 프레임워크와 함께 이용하기 (Framework Integration)

- 셀러리 설치하기 (Installation)


## 태스크 큐란 무엇인가?

태스크 큐는 스레드간 혹은 기계 간 업무를 분산하는 목적으로 만들어진 메커니즘입니다.

태스크 큐에 들어가는 일거리들은 태스크(Task)라고 불리고 각각 독립된 워커(Worker)프로세스들은 새로운 일거리(Task)가 없는지 지속적으로 태스크 큐를 감시합니다.

셀러리는 메시지(message)를 통해 통신하는데요, 보통 브로커(Broker)가 클라이언트와 워커 사이에서 메시지를 중계해줍니다. 브로커는 클라이언트가 큐에 새로 추가한 태스크를 메시지로 워커에 전달해줍니다.

셀러리 시스템에서는 여러개의 워커와 브로커를 함께 사용할 수 있는데요, 이 덕분에 높은 가용성과 Scaling이 가능합니다.

셀러리는 Python으로 짜여져 있습니다. 하지만 어떤 언어를 통해서도 프로토콜을 통해 셀러리를 사용할 수 있습니다. 예를들어, Node나 PHP를 위한 [node-celery](https://github.com/mher/node-celery)나 [PHP client](https://github.com/gjedeer/celery-php)도 있답니다.

또, HTTP endpoint를 통해 webhook으로 태스크를 요청하는 것도 가능하답니다.

## 뭐가 필요한가요?

셀러리를 사용하려면 메시지를 주고받아주는 브로커 등이 필요합니다. RabbitMQ나 Redis같은 브로커가 가장 좋은 선택이지만, 개발환경에서는 Sqlite와 같이 수많은 실험적인 대안도 있습니다.

셀러리는 단일 머신, 복수 머신, 혹은 데이터센터간에서도 사용 가능합니다.

## 시작하기

만약 여러분이 셀러리를 처음 이용하시거나 3.1버전 같은 이전 버전을 이용했다면, [셀러리 한 발자국 내밀기]()나 [더 알아보기]() 튜토리얼을 먼저 해보세요.

> 버전 확인

> 셀러리 4.0은 Python2.7/3.4/3.5 PyPy5.4/5.5에서 정상적으로 동작합니다.

## 셀러리는..

  - 단순해요!

    셀러리는 사용하기도 쉽고 관리하기도 쉽습니다. 설정 파일도 필요하지 않아요!

    가장 단순한 셀러리 앱은 아래와 같이 만들 수 있어요.

    ```py
    from celery import Celery

    app = Celery('hello', broker='amqp://guest@localhost//')

    @app.task
    def hello():
        return 'hello world'
    ```

  - 높은 가용성

    워커와 클라이언트는 연결이 끊어지거나 실패하면 자동으로 다시 연결을 시도합니다. 그리고 몇몇 브로커들은 Primary/Primary나 Primary/Replica 의 복제방식을 통해 고가용성을 제공합니다.

  - 빨라요!

    하나의 셀러리 프로세스는 1분에 수십만개의 태스크를 처리할 수 있고, ms초 이하의 RTT(왕복지연시간)로 태스크를 처리 가능하답니다. (RabbitMQ, librabbitmq와 최적화된 설정을 할 경우)

  - 유연해요!

    셀러리의 대부분 파트는 그 자체로 이용할 수도 있고 원하는 만큼 확장도 가능합니다. Custom pool implementations, serializers, compression schemes, logging, schedulers, consumers, producers, broker transports을 포함해 더 많이요.

## 셀러리의 기능들

  - 모니터링

    모니터링 이벤트 스트림은 각 워커에서 나오고, 클러스터에서 수행하는 작업을 실시간으로 알려줍니다.

    [더 알아보기..](http://docs.celeryproject.org/en/latest/userguide/monitoring.html#guide-monitoring)

  - 워크 플로우

    간단하거나 복잡한 워크플로우를 "캔버스"라는 도구를 통해 그룹핑, 체이닝, 청킹등을 할 수 있습니다.

    [더 알아보기..](http://docs.celeryproject.org/en/latest/userguide/canvas.html#guide-canvas)

  - 시간 / 비율 제한

    태스크가 시간당 얼마나 실행 될지 제어할 수 있고, 한 태스크가 얼마나 오랫동안 실행될지 허용할 수 있습니다. 각각의 워커마다 다르게 설정하거나 각각의 태스크마다도 다르게 설정할 수 있답니다.

    [더 알아보기..](http://docs.celeryproject.org/en/latest/userguide/workers.html#worker-time-limits)

  - 스케쥴링

    어떤 태스크를 정해진 시간에 실행할 수 있습니다. 또, 정해진 주기로 태스크를 실행 할 수도 있습니다. Crontab에서 사용하는 방식(분/시간/요일등등)을 이용할 수도 있습니다.

    [더 알아보기..](http://docs.celeryproject.org/en/latest/userguide/periodic-tasks.html#guide-beat)

  - 사용자 컴포넌트

    각각의 워커 컴포넌트들을 커스터마이징해 사용할 수 있습니다. 그리고 추가적인 컴포넌트도 커스터마이징해 사용할 수 있습니다. 워커는 내부 구조를 세밀하게 제어할수있는 종속성 그래프인 "bootsteps"를 사용하여 빌드됩니다.

## 프레임워크와 함께 이용하기

셀러리는 웹 프레임 워크와 쉽게 함께 사용할 수 있고, 일부는 합쳐진 패키지도 있습니다.

  - Pyramid: [pyramid_celery](https://pypi.python.org/pypi/pyramid_celery/)
  - Pylons: [celery-pylons](https://pypi.python.org/pypi/celery-pylons/)
  - Flask: 필요없음
  - Web2Py: [web2py-celery](https://pypi.python.org/pypi/web2py-celery/)
  - Tornado: [tornado-celery](https://pypi.python.org/pypi/tornado-celery/)

Django의 경우에는 [장고와 함께하는 셀러리 첫걸음](http://docs.celeryproject.org/en/latest/django/first-steps-with-django.html#django-first-steps)을 참고하세요.

통합 패키지가 굳이 필요하지는 않지만 개발을 더 쉽게 해주고 DB 커넥션 등에서 중요한 hook를 추가하기도 하기때문에 이용하는 편이 낫습니다.

## 설치하기

셀러리는 PyPI를 통해 쉽게 설치할 수 있습니다.

```bash
pip install -U pip
```
