---
title: "[DjangoTDDStudy] #02: UnitTest 이용해 기능 테스트 하기"
date: 2016-12-27
layout: post
categories:
- DjangoTDDStudy
- Python
image: https://d1sr4ybm5bj1wl.cloudfront.net/img/old_post/unit-test.jpg
---


# 최소기능 앱

TDD를 하는데 있어 가장 기본은 당연히 테스트코드를 짜는 것이다. 하지만 그 전에 먼저, 테스트 시나리오를 작성해야 한다. 예를들어, "인터넷 쇼핑몰에 들어간 후, 상품을 검색하고, 상품을 선택하고, 장바구니에 담고, 카트에 간 후, 결제를 한다."라는 시나리오도 가능하다.

그리고, 이 시나리오를 충족하면서 가장 간단한 기능으로만 구성되지만 실제로 '동작'하는 앱을 만드는 것이다.

일단 이 최소기능 앱을 만들기 전에 우리 코드를 약간 바꿔보자.

# Python 기본 라이브러리: unittest

지금까지는 selenium의 webdriver만을 직접 이용해왔지만, 만약 테스트 할 내용이 단순히 인터넷 창 하나를 띄우는것이 아니라 여러가지로 테스트를 늘려야 한다면 이전시간에 짠 코드는 딱히 도움이 되지는 않을 듯 하다.

그리고, 열려진 브라우저를 일일히 닫아주는 것도 상당히 귀찮다. 그러니까 unittest를 이용해 보자.

방금까지 사용한 `functional_tests.py`파일을 아래와 같이 바꿔보자.

```python
# functional_tests.py

from selenium import webdriver
import unittest

class NewVisitorTest(unittest.TestCase):
    def setUp(self):
        self.browser = webdriver.Chrome('chromedriver')

    def tearDown(self):
        self.browser.quit()

    def test_can_start_a_list_and_retrieve_it_later(self):
        self.browser.get('http://localhost:8000')

        self.assertIn('To-Do', self.browser.title)
        self.fail('Finished the Test')

if __name__=='__main__':
    unittest.main(warning='ignore')
```

위 코드중 마지막의 `if __name__=='__main__'`은, 이 파이썬 코드가 다른 파이썬 파일에서 import 되어 사용되지 않고 `python functional_tests.py`라고 직접 실행한 경우에만 아래 코드를 실행한다.

만약 위 파일이 `import functional_tests`의 방식으로 import되었다면 위 코드의 `__name__`은 functional_tests가 된다.

```py
from abc import some_thing
# __name__ 은 some_thing

import abc
# __name__ 은 abc

from abc import some_thing as st
# __name__ 은 st
```

이와 같은 `__name__`을 가진다.

다시한번 위 코드를 살펴보면, NewVisitorTest 클래스는 unittest라이브러리의 TestCase클래스를 상속받고 내장함수는 setUp, teatDown, test_can_start_a_list_and_retrieve_it_later가 있다.

unittest.main()을 통해 실행되면 ~~Test라는 class들이 모두 테스트 클래스로 지정되고 실행되는데, 이 클래스 안에 있는 `test_`로 시작하는 함수 하나하나가 테스트 함수로 인식된다. (만약 `test_`로 시작하지 않으면 테스트 코드라고 인식하지 않는다.)

또한, 테스트 함수 하나하나가 실행되기 전에 setUp이 실행되고 테스트 함수가 끝날때 마다 tearDown이 실행된다.


# 암묵적 대기 / 명시적 대기

셀레늄이 URL에 들어가 페이지 로딩이 끝날때까지 기다렸다가 동작하기는 하지만, 완벽하지는 않기때문에 (ajax call로 DOM을 재구성하는 경우 등) 얼마정도 우리가 지정한 element가 나올때까지 기다리게 할 수 있다.

바로 implicit_wait()이라는 암시적 대기를 주는 것이다.

```python
# functional_tests.py

from selenium import webdriver
import unittest

class NewVisitorTest(unittest.TestCase):
    def setUp(self):
        self.browser = webdriver.Chrome('chromedriver')
        self.browser.implicit_wait(3)

    def tearDown(self):
        self.browser.quit()

    def test_can_start_a_list_and_retrieve_it_later(self):
        self.browser.get('http://localhost:8000')

        self.assertIn('To-Do', self.browser.title)
        self.fail('Finished the Test')

if __name__=='__main__':
    unittest.main(warning='ignore')
```

browser에 implicit_wait을 3초로 두었다.
그런데, 이 implicit_wait은 이 테스트 코드 전체 행동에 영향을 준다. 즉, 어떤 동작을 하기 전에 일단 3초는 허용하고 본다는 것이다.

그래서 좀 더 복잡한 코드의 경우에는 명시적 대기를 줘야만 한다.

아래는 selenium의 공식 문서 [webdriver_advanced](http://www.seleniumhq.org/docs/04_webdriver_advanced.jsp)의 코드를 일부 변형한 것이다.(Driver/URL)

```py
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait # v2.4.0 이상
from selenium.webdriver.support import expected_conditions as EC # v2.26.0 이상

browser = webdriver.Chrome('chromedriver')
browser.get("http://localhost:8000")
try:
    element = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.ID, "myDynamicElement")))
finally:
    browser.quit()
```

위 코드에서 브라우저는 0.5초마다 'myDynamicElement'라는 ID를 가진 요소가 존재하는지를 체크한다. 만약 10초 내로 나타난다면 정상적으로 진행되고, 나타나지 않으면 TimeoutException을 내뱉는다.

### 여담
하지만 selenium문서에서는 이 코드는 implicit_wait와 크게 다르지 않다고 한다. 좀더 공부가 필요할 듯 하다.


