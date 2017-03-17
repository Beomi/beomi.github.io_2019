---
author: livingmethod
comments: true
date: 2016-11-04 13:46:54+00:00
layout: post
link: http://blog.jblee.kr/2016/11/04/%eb%b2%88%ec%97%ad-%ec%9e%a5%ea%b3%a0django%ec%99%80-%ed%95%a8%ea%bb%98%ed%95%98%eb%8a%94-celery-%ec%b2%ab%ea%b1%b8%ec%9d%8c/
slug: '%eb%b2%88%ec%97%ad-%ec%9e%a5%ea%b3%a0django%ec%99%80-%ed%95%a8%ea%bb%98%ed%95%98%eb%8a%94-celery-%ec%b2%ab%ea%b1%b8%ec%9d%8c'
title: '[번역] 장고(Django)와 함께하는 Celery 첫걸음'
wordpress_id: 424
categories:
- Django
- Python
- Translation
image: https://livingmethod.files.wordpress.com/2016/11/celery_128.png
---

원문: [http://docs.celeryproject.org/en/latest/django/first-steps-with-django.html](http://docs.celeryproject.org/en/latest/django/first-steps-with-django.html)

```
유의사항: 현재(11.14) celery가 4.0버전으로 stable 릴리즈가 되었습니다.
아래 문서는 3.1의 마지막 버전의 문서를 번역한 것입니다. 최신 문서는 곧 업데이트 될 예정입니다.
```


Celery는 공식적인 패키지로 django-celery를 제공합니다. 이 문서는 celery의 현재(2016.11)의 최신 버전인 3.1버전을 기준으로 하고 있습니다.


# 장고(Django)와 함께하는 Celery 첫걸음


원제: First steps with Django


## 장고와 함께 Celery사용하기





* * *




_**유의점:**_
_이전 버전의 celery는 장고와 독립적인 패키지를 필요로 했지만, 3.1버전부터는 더이상 그렇지 않습니다. 이제 장고에서 공식적으로 celery를 바로 사용할 수 있도록 지원하며, 따라서 이 문서는 celery와 장고를 간단하게 연결하는 부분만을 다루고 있습니다. 즉, 장고와 함께 사용하지 않고 독립적으로 사용하는 celery와 완전히 같은 API를 사용하고 있기 때문에, 현재는 [First Steps with Celery](http://docs.celeryproject.org/en/latest/getting-started/first-steps-with-celery.html#first-steps)를 읽고나서 다시 이 문서로 오시는 것을 추천합니다. 이미 작동하고 있는 celery 앱을 갖고 계시다면, [Next Steps](http://docs.celeryproject.org/en/latest/getting-started/next-steps.html#next-steps) 가이드를 참고하시기 바랍니다._






* * *



Celery를 장고 프로젝트에서 사용하시려면, 우선 Celery 라이브러리의 인스턴스를 정의해야 합니다. (이 인스턴스는 아래에서 'app'이라고 불립니다.)

만약 최신 장고프로젝트(django 1.10)의 형식을 따라 사용하고 계시다면,  장고 프로젝트는 아래와 같은 형태일 것입니다. (프로젝트 이름: 'proj')

```
- proj/
  - proj/__init__.py
  - proj/settings.py
  - proj/urls.py
- manage.py
```


만약 이런 구조로 되어있다면, 추천하는 방법은 장고 프로젝트 폴더(proj/proj/)안에 celery.py파일을 생성하는 것입니다. 아래와 같이요.

```
- proj/
  - proj/__init__.py
  - proj/settings.py
  - proj/urls.py
  - proj/celery.py
- manage.py
```

파일: proj/proj/celery.py

```python
from __future__ import absolute_import

import os

from celery import Celery

# Django의 세팅 모듈을 Celery의 기본으로 사용하도록 등록합니다.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proj.settings')

from django.conf import settings  # noqa

app = Celery('proj')

# 문자열로 등록한 이유는 Celery Worker가 Windows를 사용할 경우
# 객체를 pickle로 묶을 필요가 없다는 것을 알려주기 위함입니다.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
```


위와같이 celery.py파일을 만드신 후에, 장고 프로젝트 폴더의 __init__.py 모듈에서 이 celery 앱을 import해와야 합니다. 이 과정은 장고가 시작될 때 @shared_task 데코레이터의 사용을 가능하게 합니다.

파일: proj/proj/__init__.py

```py
from __future__ import absolute_import

# 아래 import는 장고가 시작될 때 항상 import되기 때문에
# shared_task가 장고에서 작동하는 것을 가능하게 해 줍니다.
from .celery import app as celery_app # Celery를 import합니다.
```

참고로, 위에서 제시한 장고 프로젝트의 구조는 거대한 프로젝트에 적합합니다. 만약 [First Steps with Celery](http://docs.celeryproject.org/en/latest/getting-started/first-steps-with-celery.html#tut-celery) 튜토리얼처럼 작고 간단한 프로젝트라면, 한 모듈(한 파이썬 파일)에서 App과 Task를 모두 다루는 것도 괜찮습니다.

자, 이제 우리가 여기서 처음으로 만든 모듈(celery.py)를 뜯어 보도록 합시다. 우선, 우리는 absolute import를 future에서 import 할 것입니다. 다른 library와 꼬이지 않게 위해서요.


```py
from __future__ import absolute_import
```


그 다음에, 우리는 Celery의 커맨드라인 프로그램을 위해 기본 DJANGO_SETTINGS_MODULE을 가져와서 설정해줍니다.


```py
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proj.settings')
```




이렇게 장고의 세팅파일을 명시해 주는 것은 터미널에서 사용하는 celery커맨드가 장고 프로젝트가 도대체 어디에 있는 장고 프로젝트를 말하는 건지를 알 수 있게 도와줍니다. 이 코드는 항상! App Instance가 생성되지 전에 적어줘야 합니다.

이 다음에 우리가 해야하는 것은 App Instance 객체를 생성하는 겁니다.


```py
app = Celery('proj')
```

위 코드는 celery 라이브러리의 인스턴스가 됩니다. 물론, 여러 다른이름으로 여러개의 인스턴스를 만들 수도 있습니다. 그런데, Django와 Celery를 사용할 때에는 하나만 만들어도 충분합니다.

우리는 장고 세팅 모듈을 Celery의 설정 소스로 삼아줄 것인데요, 바로 이게 여러개의 인스턴스를 만들 필요가 없는 이유랍니다. Celery를 장고 세팅에서 바로 설정할 수 있게 해주기 때문이죠!

이곳에 Object를 바로 넣어줄 수도 있지만, 문자열(Str)로 넘겨주는 것이 더 나은데요, 이렇게 해주면 worker가 Windows나 execv를 사용할 때 Object를 serialize할 필요가 없기 때문입니다.







```py
app.config_from_object('django.conf:settings')
```





이렇게 문자열로 넣어줍시다.

일반적으로, 재사용 가능한 앱을 만드는 것은 모든 작업 코드들을 다른 파일인, 예를들어 tasks.py와 같은 파일에 몰아두는 것입니다. 그리고 celery는 이 모듈들을 자동으로 찾을 수 있답니다.


```py
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
```




위 코드로 celery는 자동적으로 장고 세팅에 재사용 가능한 앱에서 tasks.py를 찾을 겁니다.(단, task들이 있는 파일 이름이 tasks.py여야 자동으로 찾을 수 있습니다.)

```
- app1/
    - app1/tasks.py
    - app1/models.py
- app2/
    - app2/tasks.py
    - app2/models.py
```

이와 같은 모양으로, 각 앱 아래에 tasks.py를 두는 것입니다.

이 방법을 통해 개별적 모듈들을 CELERY_IMPORTS 세팅값에 등록해주지 않아도 됩니다. lambda를 통해 필요한 경우에만(재사용 가능한 앱이 있는 경우에만) 자동탐색이 동작하게 되기 때문에, Celery App을 import한다고 해서 장고 세팅 객체를 검사(evaluate)하지는 않습니다.

마지막으로, debug_task라는 예제는 request받은 정보를 단순하게 dump하는 작업만 합니다. 그리고, bind=True라는 Task옵션은 Celery 3.1에서 도입된 기능으로, 현재 작업 인스턴스를 좀 더 쉽게 refer하도록 도와줍니다.



* * *





## @shared_task 데코레이터 이용하기


우리가 작성한(혹은 지금 보고있는 분이 작성한) task들은 재사용 가능한 앱들에 있을텐데, 이러한 재사용가능한 앱들은 Project자체에 의존하기는 어렵습니다. 그리고 app을 단독으로 직접적으로 import할 수도 없죠.

@shared_task 데코레이이터는 딱딱한(concrete) 앱 없이도 task를 만들 수 있도록 해 줍니다.

demoapp/tasks.py

```py
from __future__ import absolute_import

from celery import shared_task

@shared_task
def add(x, y):
    return x + y

@shared_task
def mul(x, y):
    return x * y

@shared_task
def xsum(numbers):
    return sum(numbers)
```



* * *




_**참고:**_
_장고-셀러리 예제 프로젝트의 전체 코드는 아래에서 보실 수 있습니다._
_[https://github.com/celery/celery/tree/3.1/examples/django/](https://github.com/celery/celery/tree/3.1/examples/django/)_






* * *





## 장고 ORM와 Cache를 Celery결과 백엔드로 이용해 봅시다


만약 task의 결과를 장고 database에 저장하고 싶다면 우선 django-celery 라이브러리를 먼저 설치해야 합니다.(위에서 이미 설치했겠지만요!)(혹은 SQLAlchemy Result Backend를 이용해도 됩니다.)

django-celery라이브러리는 Django ORM와 Django Cache Framework를 Result Backend로 사용하게 해 줍니다. 이걸 사용하려면,

1. django-celery 라이브러리를 설치해 줍니다.


```
$ pip install django-celery
```

2. djcelery를 INSTALLED_APPS(장고 프로젝트 settings.py)에 추가해 줍시다.

3. 데이터베이스 테이블을 만들어 줍시다


```    
$ python manage.py migrate djcelery
```

4. Celery가 django-celery backend를 사용하도록 설정해줍시다.
4-1. 만약 Database Backend를 이용하고 싶다면..

```py
app.conf.update(
    CELERY_RESULT_BACKEND='djcelery.backends.database:DatabaseBackend',
)
```


4-2. 만약 Cache Backend를 이용하고 싶다면..

```py
app.conf.update(
    CELERY_RESULT_BACKEND='djcelery.backends.cache:CacheBackend',
)
```


4-3. 만약 Celery를 Django settings에 직접 연결해 두었다면 app.conf.update부분 없이 바로 괄호 안의 문구를 settings.py안에 넣어두기만 하면 됩니다.



* * *



_**(유의점)상대적 import:**__
__import를 하는 방법은 항상 일치해야 합니다. 만약,  `project.app` 을  `INSTALLED_APPS` 에 import 해 주었다면 `from project.app` 와 같은 형식으로 import해주어야 합니다. 혹은 각각의 task들이 이름이 모두 다르게 하는 방법도 있습니다.
__추가정보: [Automatic naming and relative imports](http://docs.celeryproject.org/en/latest/userguide/tasks.html#task-naming-relative-imports)_



* * *





## 워커 프로세스 실행해보기


실 배포 환경에서는 worker를 시스템 daemon으로 사용해야합니다. ([Running the worker as a daemon](http://docs.celeryproject.org/en/latest/tutorials/daemonizing.html#daemonizing) 을 참고하세요.) 하지만, 테스트할 때에는 worker instance를 celery worker manage 커맨드를 통해 시작하는 것이 더 편리합니다. 장고의 runserver를 이용하는 것 처럼요 :)







```sh
$ celery -A proj worker -l info
```




위 코드로 간단하게 실행이 가능하고, command-line 옵션을 모두 보려면





```sh
$ celery help
```

라고 쳐 봅시다.



* * *





## 이제 어디로 가야할까요?


만약 좀 더 배우고 싶다면, [Next Steps](http://docs.celeryproject.org/en/latest/getting-started/next-steps.html#next-steps) 튜토리얼을 보세요. 그 튜토리얼을 마친 이후에는 [User Guide](http://docs.celeryproject.org/en/latest/userguide/index.html#guide)를 보고 공부할 수 있을거에요.
