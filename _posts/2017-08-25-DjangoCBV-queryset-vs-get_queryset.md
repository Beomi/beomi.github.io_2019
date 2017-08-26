---
title: "Django CBV: queryset vs get_queryset() 삽질기"
date: 2017-08-25
layout: post
categories:
- django
published: true
image: /img/queryset_vs_get_queryset_on_django_cbv.jpg
---

> 요약: `queryset`은 request 발생시 한번만 쿼리셋이 동작하고, `get_queryset()`은 매 request마다 쿼리를 발생시킨다. 조건이 걸린 쿼리셋을 쓸때는 `get_queryset()`을 오버라이딩하자.

## 사건의 발단

ListView안에서 체크박스로 ForeignKey로 연결된 장고 모델 인스턴스를 저장(`.save()`를 호출)하는데 저장 후 모델 인스턴스의 값을 확인하는 뷰에서는 결과값이 저장 전의 데이터로 나타났었다.

```python
# 문제의 코드..
class OrderMatchingList(ListView):
    class Meta:
        model = Order

    queryset_list = Order.objects.filter(status__gte=5) \
        .select_related('education', 'region') \
        .prefetch_related('orderdetail_set')
    queryset = sorted(queryset_list, key=lambda x: x.start_date())
```

사실 지금은 코드를 보면 `queryset`에서 `sorted`된 값을 반환하고, 이경우에는 쿼리셋 자체가 저 변수로 할당되어버려 다음 request에서 쿼리가 돌지 않는다는 것을 쉽게 찾을 수 있다. 하지만 원래 한번 안보이면 잘 안보이는 법.. 심지어 이 경우에는 Exception이 나는 것도 아니기 때문에 더 찾기 어려웠다.. (ㅠㅠ)

## 삽질의 시작

여러가지 가정을 할 수 있는 상황이었다.

- 혹시 브라우저가 리스트를 캐싱하고 있던건 아닐까? (브라우저 캐시)
- 장고가 View의 Response를 캐싱하고 있는걸까? (장고 캐시)
- 혹시 DB에 `save()`가 안된(아예 DB가 업데이트가 되지 않은) 것은 아닐까?
- 장고 `queryset`에 캐싱이 되어있었을까?
- AJAX call이 비정상적으로 이루어진 것은 아닐까?
- 아니면, 아예 내 View 로직이 잘못된 것은 아닐까? (CBV인데?)
- `select_related`나 `prefetch_related`에서 캐싱이 발생하는걸까?
- ...

이런저런 가정을 하고 하나씩 체크를 해보기로 했다.

> 아래부분에서는 django 로직과 관련된 삽질만 다뤘습니다. JS쪽은 문제가 없었거든요.

---

### 첫번째 삽질: "브라우저가 캐싱을 하고 있는건 아닐까?"

만약 브라우저가 HTML파일을 캐싱하고 있다면

- 캐시 삭제후 강력 새로고침을 하거나,
- 다른 브라우저로 접근하면

정상적인 화면이 나와야 했다.

> 그러나... "#망했어요"

브라우저가 캐싱하고 있는게 아니었고, 다른 브라우저에서도 기존(업데이트 전)값을 가져왔다.

---

### 두번째 삽질: "장고가 template 렌더링 된것을 캐싱하는게 아닐까?"

사실 장고에서 response는 따로 캐싱을 명시적으로 하지 않으면 쿼리가 새로 발생해야 하는 경우에는 캐싱을 하지 않는다. 

하지만 일단 template을 재 렌더링 하지 않는게 아닐까... 하는 생각에 아래와 같은 부분을 추가해 보았다.

```
{% for object in object_list %}
{{ object }} 이건 object다 
{% endfor %}
```

> 역시 .. "응 아니야~ 장고 일 잘하고 있음"

템플릿은 렌더링이 충분히 잘 되고 있었다.

뭐가 문제일까?

---

### 세번째 삽질: "`.save()` 메소드의 사용을 잘못한게 아닐까?"

아예 다음번에는 DB에 저장이 되지 않고 있는게 아닌가.. 하는 생각에 `save()`와 `update()`의 사용법을 찾고, `force_insert=True`와 같은 옵션을 넣어보기도 했다.

```python
# view.py 파일에서...
    # ...
    for m_pay in mentor_payment_list:
        if str(m_pay.pk) in cleaned_keys:
            m_pay.status = 1
        else:
            m_pay.status = 0
        m_pay.save(update_fields=['status'])
    # ...
```

`.save()`는 모델 인스턴스에 적용하는 케이스이고, `.update()`는 쿼리셋에 적용하는 방법이다. `save()`의 경우 모델 인스턴스를 가져오기 위해 SELECT 쿼리를 한번 날리고 값을 변경 후 UPDATE를 해주는 방법이라면, `update()`는 쿼리 자체를 SELECT쿼리로 날리는 방식이다. 따라서 만약의 경우 `.update()`를 실행 중 다른 요청에서 값이 변경되었다면 그 Transaction이 손실될 수 있고, 모델 인스턴스의 값 자체를 이용해 업데이트하는 방법은 사용하기 어렵다. (물론 사용은 가능하지만 SELECT쿼리같이 `.get()`으로 한번 가져와야 하기때문에 큰 의미는 없습니다. 여전히 중간에 값이 변경되었을 경우에 기존 값(get)에 대한 불가능하고요.)

`m_pay.save(update_fields=['status'])`에서는 `save()`에 `update_fields` 리스트를 넣어주었다. 일반적인 `save()`함수가 인스턴스 전체를 변경하는 `UPDATE`문을 사용하지만 `update_fields`가 있는 경우에는 `force_insert`가 자동으로 `True`가 되며 동시에 해당되는 Column만 update가 일어난다.

게다가 `update_fields`를 넣기 전에도 이미 잘 작동하던 코드.

> 무엇이 문제일까? 문제는 미궁속으로..

---

### 네번째 삽질: "`select_related`나 `prefetch_related`에서 캐싱이 발생하는건 아닐까?"

장고에서 `select_related`나 `prefetch_related`는 기본적으로 한번에 데이터를 가져와 queryset 자체에 캐싱을 하는 전략인데.. 혹시 여기에서 '과도한 캐싱'이 발생하고 있는건 아닐까?

그렇다면 장고의 캐싱을 강제로 없애는 `never_cache` 데코레이터를 사용하면 어떨까? 하지만 지금 뷰는 CBV니까.. `@method_decorator`로 `never_cache`를 전달해 주면 되겠다!

```python
from django.views.decorators.cache import never_cache

@method_decorator(never_cache, name='dispatch')
class OrderMatchingList(SuperuserRequiredMixin, LoginRequiredMixin, ListView):
    # ...
```

물론, 당연히, 캐시 문제가 아니었기 때문에 **안되는 것**은 당연했다.

---

### 다섯번째 삽질, 여섯번째, 일곱 ... 그리고 더 많은 삽질 끝에서의 허무

도대체 뭐가 문제인거지? `ListView`가 아예 문제인가? 이런 고민을 하다가 결국 django의 `ListView`자체를 뜯어보는데 눈에 들어오는 `MultipleObjectMixin`.

```python
class MultipleObjectMixin(ContextMixin):
    # ...
    queryset = None
    # ...

    def get_queryset(self):
        # ...
```

헐. `queryset`와 `get_queryset`은 다른데.

---

## 해결 & 평화

사실 이 문제가 생긴건 DB에서 정렬하는 대신 파이썬 View에서 쿼리셋을 정렬하는 방식으로 사용하려다보니 생긴 문제였다.

모델 내부의 `start_date()`에 따라 정렬하는 방식을 쿼리셋 내부에서 구현이 어려워 파이썬의 `sorted`를 이용했는데, 이 sorted된 결과물이 `queryset` 변수에 담겨 새 request에도 같은 결과를 반환하게 된 것.

따라서 다음과 같이 `get_queryset`으로 변환해주어서 깔끔하게 해결되었다. 

```python
class OrderMatchingList(ListView):
    class Meta:
        model = Order

    def get_queryset(self):
        queryset_list = Order.objects.filter(status__gte=5) \
            .select_related('education', 'region') \
            .prefetch_related('orderdetail_set')
        return sorted(queryset_list, key=lambda x: x.start_date())
```

사실 DJDT(Django Debug Toolbar)를 사용하며 쿼리의 개수를 확인해보는데 첫 요청시에는 6개의 쿼리가 가는데 비해 두번째 요청부터는 3개의 쿼리만이 실행되고, 그마저도 데이터를 가져오는 쿼리는 없고 세션/로그인등의 비교만 쿼리를 실행하고 있다는 것을 발견해 쿼리셋쪽의 문제라는 것을 알 수 있었다.

### 여담

문제의 코드 부분(아래)에서 `select_related`와 `prefetch_related`를 제거하면 쿼리수는 몇십개로 증가하지만 데이터 자체는 정상적으로 가져왔다. 이건 또 왜그랬을까?

```python
# 문제의 코드..
class OrderMatchingList(ListView):
    class Meta:
        model = Order

    queryset_list = Order.objects.filter(status__gte=5) \
        .select_related('education', 'region') \
        .prefetch_related('orderdetail_set')
    queryset = sorted(queryset_list, key=lambda x: x.start_date())
```