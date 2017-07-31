---
title: "Class Based View로 빠른 장고 개발하기(1): CBV의 종류"
date: 2017-07-29
layout: post
categories:
- Django
published: false
image: /img/cbv_in_django.jpeg
---

> 이 가이드는 `django 1.11.x`버전과 `python 3.6.x`버전을 대상으로 합니다.

## Django에서의 `View`

장고에서 view는 MVC모델에서의 Controller에 해당합니다. 즉 HTTP request에 따라 어떤 데이터를 response로 해줄지 결정을 해주는 부분입니다.

장고가 파이썬 기반인 만큼 장고의 뷰를 Function(함수) 기반으로 작성할 수도 있고 Class(클래스) 기반으로 작성할 수도 있습니다. View가 '요청을 받는다 -> 처리한다 -> 요청의 답을 보내준다'라는 과정을 바탕으로 하는 것을 생각해보면 사실 함수의 입력값(요청 받기)을 함수의 결과(요청의 답)로 보내주는 과정과 거의 흡사하다고 볼 수 있습니다.

장고에서 `CBV`라고 불리는 뷰도 이와 동일한 과정을 거칩니다. 하지만 클래스라는 틀 안에서 `get`, `post`등의 내부 함수가 구현되어있고 기본적인 `View`를 비롯해 일반적인(Generic한) 뷰들(ex: `ListView`, `DetailView`등등)을 제공해주기 때문에 웹 서비스에서 기본적으로 생각하는 CRUD(Create, Read, Update and Delete)를 굉장히 빠르고 쉽게 구현할 수 있습니다.

## Django CBV의 종류

### View: 가장 기본적인 뷰

장고에서 제공해주는 CBV는 여러가지 종류가 있습니다.

그 중 가장 대표적인 것이 `View`입니다. Function Based View(이하 FBV)에서 CBV로 넘어오는 경우 `View`를 이용하면 쉽게 전환이 가능합니다.

만약 아래와 같은 FBV가 있다고 가정해 봅시다. (Post모델이 있다고 가정해봅시다.)

```python
# views.py
from .models import Post

def post_list(request):
    posts = Post.objects.all()
    return render(request, 'post_list.html', {'posts':posts})
```

이 함수는 `urls.py`파일을 통해 불러질거에요.

```python
# urls.py
from django.conf.urls import url
from .views import post_list # 위에서 만들어준 post_list를 불러옵시다.

urlpatterns = [
    url(r'^posts/$', post_list, name='post_list'),
]
```

`post_list`라는 이름의 FBV는 `/posts/`라는 경로로 HTTP 요청이 들어올 때 `Post`라는 모델의 모든 객체를 담은 쿼리셋을 담아 `post_list.html`이라는 템플릿에 렌더링해 보냅니다. 만약 이 뷰를 CBV로 바꾼다면 아래와 유사하게 됩니다.

```python
# views.py
from .models import Post
from django.views import View # 가장 기본인 View를 import해줍시다.

class PostList(View):
    def get(self, request, *args, **kwargs):
        posts = Post.objects.all()
        return render(request, 'post_list.html', {'posts':posts})
```

그리고 이렇게 만들어준 `PostList` 클래스는 `urls.py`안에서 `.as_view()`메소드를 통해 실제로 동작하게 됩니다.

```python
# urls.py
from django.conf.urls import url
from .views import PostList # 위에서 만들어준 PostList CBV를 불러옵시다.

urlpatterns = [
    url(r'^posts/$', PostList.as_view(), name='post_list'),
]
```

위 코드를 보면 FBV와 CBV가 큰 차이가 없다고 느낄 수 있습니다.

하지만 `PostList`와 같이 자주 사용하는 뷰들은 장고 내에 이미 사용하기 쉽게 구현되어있습니다.

### ListView: 특정 모델을 목록으로 만들어주는 뷰 

앞서 만든 `PostList`라는 CBV는 `Post`라는 모델 전부를 보여주는 뷰입니다.
