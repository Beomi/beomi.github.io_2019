---
title: "Selenium Implicitly wait vs Explicitly wait"
date: 2017-10-29
layout: post
categories:
- HowToMakeWebCrawler
published: true
image: /img/Selenium_Implicitly_wait_vs_Explicitly_wait.png
---

> 좀 더 보기 편한 [깃북 버전의 나만의 웹 크롤러 만들기](https://beomi.github.io/gb-crawling/)가 나왔습니다!

## 들어가며

Selenium WebDriver를 이용해 실제 브라우저를 동작시켜 크롤링을 진행할 때 가끔가다보면 `NoSuchElementException`라는 에러가 나는 경우를 볼 수 있습니다.

가장 대표적인 사례가 바로 JS를 통해 동적으로 HTML 구조가 변하는 경우인데요, 만약 사이트를 로딩한 직후에(JS처리가 끝나지 않은 상태에서) JS로 그려지는 HTML 엘리먼트를 가져오려고 하는 경우가 대표적인 사례입니다. (즉, 아직 그리지도 않은 요소를 가져오려고 했기 때문에 생기는 문제인 것이죠.)

![]({{site.static_url}}/img/dropbox/2017-10-22%2023.39.57.png)

그래서 크롤링 코드를 작성할 때 크게 두가지 방법으로 브라우저가 HTML Element를 기다리도록 만들어 줄 수 있습니다.

## Implicitly wait

Selenium에서 브라우저 자체가 웹 요소들을 기다리도록 만들어주는 옵션이 `Implicitly Wait`입니다.

아래와 같은 형태로 카카오뱅크 타이틀을 한번 가져와 봅시다.

```python
from selenium import webdriver

driver = webdriver.Chrome('chromedriver')

# driver를 만든 후 implicitly_wait 값(초단위)을 넣어주세요.
driver.implicitly_wait(3)

driver.get('https://www.kakaobank.com/')

# 하나만 찾기
title = driver.find_element_by_css_selector('div.intro_main > h3')
# 여러개 찾기
small_titles = driver.find_elements_by_css_selector('div.cont_txt > h3')

print(title.text)

for t in small_titles:
    print(t.text)

driver.quit()
```

위 코드를 실행하면 여러분이 `.get()`으로 지정해준 URL을 가져올 때 각 HTML요소(Element)가 나타날 때 까지 최대 3초까지 '관용있게' 기다려 줍니다.

즉, 여러분이 `find_element_by_css_selector`와 같은 방식으로 HTML엘리먼트를 찾을 때 만약 요소가 없다면 요소가 없다는 `No Such Element`와 같은 Exception을 발생시키기 전 모든 시도에서 3초를 기다려 주는 것이죠.

하지만 이런 방식은 만약 여러분이 크롤링하려는 웹이 ajax를 통해 HTML 구조를 동적으로 바꾸고 있다면 과연 '3초'가 적절한 값일지에 대해 고민을 하게 만듭니다.(모든 ajax가 진짜로 3초 안에 이루어질까요?)

그래서 우리는 조금 더 발전된 기다리는 방식인 Explicitly wait을 사용하게 됩니다.

> NOTE: 기본적으로 Implicitly wait의 값은 0초입니다. 즉, 요소를 찾는 코드를 실행시킨 때 요소가 없다면 전혀 기다리지 않고 Exception을 raise하는 것이죠.

## Explicitly wait

자, 여러분이 인터넷 웹 사이트를 크롤링하는데 ajax를 통해 HTML 구조가 변하는 상황이고, 각 요소가 들어오는 시간은 몇 초가 될지는 예상할 수 없다고 가정해 봅시다.

위에서 설정해 준 대로 implicitly_wait을 이용했다면 어떤 특정한 상황(인터넷이 유독 느렸음)으로 인해 느려진 경우 우리가 평소에 기대했던 3초(n초)를 넘어간 경우 Exception이 발생할 것이고 이로 인해 반복적인 크롤링 작업을 진행할 때 문제가 생길 수 있습니다.

따라서 우리는 명확하게 특정 Element가 나타날 때 까지 기다려주는 방식인 Explicitly Wait을 사용할 수 있습니다.

아래 코드는 위에서 Implicitly wait을 통해 사용했던 암묵적 대기(`get_element_by_id` 등)을 사용한 대신 명시적으로 `div.intro_main > h3`라는 CSS Selector로 가져오는 부분입니다.

```python
from selenium import webdriver
# 아래 코드들을 import 해 줍시다.
from selenium.webdriver.common.by import By
# WebDriverWait는 Selenium 2.4.0 이후 부터 사용 가능합니다.
from selenium.webdriver.support.ui import WebDriverWait
# expected_conditions는 Selenium 2.26.0 이후 부터 사용 가능합니다.
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Chrome('chromedriver')

driver.get('https://www.kakaobank.com/')

try:
    # WebDriverWait와 .until 옵션을 통해 우리가 찾고자 하는 HTML 요소를
    # 기다려 줄 수 있습니다.
    title = WebDriverWait(driver, 10) \
        .until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.intro_main > h3")))
    print(title.text)
finally:
    driver.quit()
```

위 코드를 사용하면 우리가 찾으려는 대상을 driver가 명시적으로 '10초'를 기다리도록 만들어 줄 수 있습니다.

## 마치며

만약 여러분이 ajax를 사용하지 않는 웹 사이트에서 단순하게 DOM구조만 변경되는 상황이라면 사실 Explicitly wait을 사용하지 않아도 괜찮을 가능성이 높습니다. (DOM API처리속도는 굉장히 빠릅니다.)

하지만 최신 웹 사이트들은 대부분 ajax요청을 통해 웹 구조를 바꾸는 SPA(Single Page App)이 많기 때문에 크롤링을 진행할 때 Explicitly wait을 이용하는 것이 좋습니다.

