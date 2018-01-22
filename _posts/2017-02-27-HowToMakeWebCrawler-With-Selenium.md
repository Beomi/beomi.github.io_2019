---
title: "나만의 웹 크롤러 만들기(3): Selenium으로 무적 크롤러 만들기"
date: 2017-02-27
layout: post
categories:
- Python
- HowToMakeWebCrawler
published: true
image: https://d1sr4ybm5bj1wl.cloudfront.net/img/2017-01-25-HowToMakeWebCrawler-With-Selenium/selenium1.jpg
---

> 좀 더 보기 편한 [깃북 버전의 나만의 웹 크롤러 만들기](https://beomi.github.io/gb-crawling/)가 나왔습니다!

이전게시글: [나만의 웹 크롤러 만들기(2): Login with Session](/2017/01/20/HowToMakeWebCrawler-With-Login/)

# Selenium이란?
---

Selenium은 주로 웹앱을 테스트하는데 이용하는 프레임워크다. `webdriver`라는 API를 통해 운영체제에 설치된 Chrome등의 브라우저를 제어하게 된다.

브라우저를 직접 동작시킨다는 것은 JavaScript를 이용해 비동기적으로 혹은 뒤늦게 불러와지는 컨텐츠들을 가져올 수 있다는 것이다. 즉, '눈에 보이는' 컨텐츠라면 모두 가져올 수 있다는 뜻이다. 우리가 requests에서 사용했던 `.text`의 경우 브라우저에서 '소스보기'를 한 것과 같이 동작하여, JS등을 통해 동적으로 DOM이 변화한 이후의 HTML을 보여주지 않는다. 반면 Selenium은 실제 웹 브라우저가 동작하기 때문에 JS로 렌더링이 완료된 후의 DOM결과물에 접근이 가능하다.

# 어떻게 설치하나?
---

## pip selenium package

Selenium을 설치하는 것은 기본적으로 `pip`를 이용한다.

```bash
pip install selenium
```

> 참고: Selenium의 버전은 자주 업데이트 되고, 브라우저의 업데이트 마다 새로운 Driver를 잡아주기 때문에 항상 최신버전을 깔아 주는 것이 좋다.

이번 튜토리얼에서는 `BeautifulSoup`이 설치되어있다고 가정합니다.

> BeautifulSoup은 `pip install bs4`로 설치 가능합니다.

## webdriver

Selenium은 `webdriver`라는 것을 통해 디바이스에 설치된 브라우저들을 제어할 수 있다. 이번 가이드에서는 Chrome을 사용해 볼 예정이다.

### Chrome WebDriver

크롬을 사용하려면 로컬에 크롬이 설치되어있어야 한다.

그리고 크롬 드라이버를 다운로드 받아주자.

[https://sites.google.com/a/chromium.org/chromedriver/downloads](https://sites.google.com/a/chromium.org/chromedriver/downloads)

글 작성일자인 2월 27일에는 ChromeDrive 2.27버전이 최신이며, 크롬 v54~56을 지원한다.

![ChromeDriver Download Page]({{site.static_url}}/img/dropbox/2017-02-27%2021.36.55.png)

버전을 클릭하면 아래와 같은 OS별 Driver파일이 나열되어있다. 사용하는 OS에 따른 driver를 받아주자.

![ChromeDriver Lists]({{site.static_url}}/img/dropbox/2017-02-27%2021.39.34.png)

zip파일을 받고 풀어주면 `chromedriver`라는 파일이 저장된다.

![]({{site.static_url}}/img/dropbox/2017-02-27%2021.41.17.png)

위 폴더를 기준으로 할 경우 `/Users/beomi/Downloads/chromedriver`가 크롬드라이버의 위치다.

이 경로를 나중에 Selenium 객체를 생성할 때 지정해 주어야 한다.

### PhantomJS webdriver

PhantomJS는 기본적으로 WebTesting을 위해 나온 Headless Browser다.(즉, 화면이 존재하지 않는다)

하지만 JS등의 처리를 온전하게 해주며 CLI환경에서도 사용이 가능하기 때문에, 만약 CLI서버 환경에서 돌아가는 크롤러라면 PhantomJS를 사용하는 것도 방법이다.

PhantomJS는 [PhantomJS Download Page](http://phantomjs.org/download.html)에서 받을 수 있다.

Binary 자체로 제공되기 때문에, Linux를 제외한 OS에서는 외부 dependency없이 바로 실행할 수 있다.

![Extracted PhantomJS Zip file]({{site.static_url}}/img/dropbox/2017-02-27%2021.47.01.png)

압축을 풀어주면 아래와 같은 많은 파일들이 있지만, 우리가 사용하는 것은 `bin`폴더 안의 `phantomjs`파일이다.

위 폴더 기준으로 할 경우 `/Users/beomi/Downloads/phantomjs-2.1.1-macosx/bin/phantomjs`가 PhantomJS드라이버의 위치다.

# Selenium으로 사이트 브라우징
---

Selenium은 `webdriver api`를 통해 브라우저를 제어한다.

우선 `webdriver`를 import해주자.

```py
from selenium import webdrver
```

이제 `driver`라는 이름의 webdriver 객체를 만들어 주자.

> 이름이 꼭 driver일 필요는 없으며, 이번 가이드에서는 크롬을 기본적으로 이용할 예정이다.

```py
from selenium import webdriver

# Chrome의 경우 | 아까 받은 chromedriver의 위치를 지정해준다.
driver = webdriver.Chrome('/Users/beomi/Downloads/chromedriver')
# PhantomJS의 경우 | 아까 받은 PhantomJS의 위치를 지정해준다.
driver = webdriver.PhantomJS('/Users/beomi/Downloads/phantomjs-2.1.1-macosx/bin/phantomjs')
```

Selenium은 기본적으로 웹 자원들이 모두 로드될때까지 기다려주지만, 암묵적으로 모든 자원이 로드될때 까지 기다리게 하는 시간을 직접 `implicitly_wait`을 통해 지정할 수 있다.

```py
from selenium import webdriver

driver = webdriver.Chrome('/Users/beomi/Downloads/chromedriver')
# 암묵적으로 웹 자원 로드를 위해 3초까지 기다려 준다.
driver.implicitly_wait(3)
```

이제 특정 url로 브라우저를 켜 보자.

```py
from selenium import webdriver

driver = webdriver.Chrome('/Users/beomi/Downloads/chromedriver')
driver.implicitly_wait(3)
# url에 접근한다.
driver.get('https://google.com')
```

만약 chromedriver의 위치가 정확하다면 새 크롬 화면이 뜨고 구글 첫 화면으로 들어가질 것이다.

Selenium은 driver객체를 통해 여러가지 메소드를 제공한다.

URL에 접근하는 api,
- get('http://url.com')

페이지의 단일 element에 접근하는 api,

- find_element_by_name('HTML_name')
- find_element_by_id('HTML_id')
- find_element_by_xpath('/html/body/some/xpath')

페이지의 여러 elements에 접근하는 api 등이 있다.

- find_element_by_css_selector('#css > div.selector')
- find_element_by_class_name('some_class_name')
- find_element_by_tag_name('h1')

위 메소드들을 활용시 HTML을 브라우저에서 파싱해주기 때문에 굳이 Python와 BeautifulSoup을 사용하지 않아도 된다.

하지만 Selenium에 내장된 함수만 사용가능하기 때문에 좀더 사용이 편리한 soup객체를 이용하려면 `driver.page_source` API를 이용해 현재 렌더링 된 페이지의 Elements를 모두 가져올 수 있다.

# 네이버 로그인 하기
---

네이버는 requests를 이용해 로그인하는 것이 어렵다. 프론트 단에서 JS처리를 통해 로그인 처리를 하기 때문인데, Selenium을 이용하면 아주 쉽게 로그인을 할 수 있다.

```py
from selenium import webdriver

driver = webdriver.Chrome('/Users/beomi/Downloads/chromedriver')
driver.implicitly_wait(3)
# url에 접근한다.
driver.get('https://nid.naver.com/nidlogin.login')
```

네이버 로그인 화면을 확인 해 보면 아이디를 입력받는 부분의 name이 `id`, ​비밀번호를 입력받는 부분의 name이 `pw`인 것을 알 수 있다.

![Naver Login Page]({{site.static_url}}/img/dropbox/2017-02-27%2022.19.18.png)

`find_element_by_name`을 통해 아이디/비밀번호 input 태그를 잡아주고, 값을 입력해 보자.

```py
from selenium import webdriver

driver = webdriver.Chrome('/Users/beomi/Downloads/chromedriver')
driver.implicitly_wait(3)
driver.get('https://nid.naver.com/nidlogin.login')
# 아이디/비밀번호를 입력해준다.
driver.find_element_by_name('id').send_keys('naver_id')
driver.find_element_by_name('pw').send_keys('mypassword1234')
```

![Naver Login Input]({{site.static_url}}/img/dropbox/2017-02-27%2022.23.11.png)

성공적으로 값이 입력된 것을 확인할 수 있다.

이제 Login버튼을 눌러 실제로 로그인이 되는지 확인해 보자.

```py
from selenium import webdriver

driver = webdriver.Chrome('/Users/beomi/Downloads/chromedriver')
driver.implicitly_wait(3)
driver.get('https://nid.naver.com/nidlogin.login')
driver.find_element_by_name('id').send_keys('naver_id')
driver.find_element_by_name('pw').send_keys('mypassword1234')
# 로그인 버튼을 눌러주자.
driver.find_element_by_xpath('//*[@id="frmNIDLogin"]/fieldset/input').click()
```

성공적으로 로그인이 되는 것을 확인할 수 있다.

![Naver Login Success]({{site.static_url}}/img/dropbox/2017-02-27%2022.28.00.png)

로그인이 필요한 페이지인 네이버 페이의 주문내역 페이지를 가져와보자.

![Naver Pay Order]({{site.static_url}}/img/dropbox/2017-02-27%2022.38.43.png)

네이버 페이의 Url은 `https://order.pay.naver.com/home` 이다. 위 페이지의 알림 텍스트를 가져와 보자.

```py
from selenium import webdriver
from bs4 import BeautifulSoup

driver = webdriver.Chrome('/Users/beomi/Downloads/chromedriver')
driver.implicitly_wait(3)
driver.get('https://nid.naver.com/nidlogin.login')
driver.find_element_by_name('id').send_keys('naver_id')
driver.find_element_by_name('pw').send_keys('mypassword1234')
driver.find_element_by_xpath('//*[@id="frmNIDLogin"]/fieldset/input').click()

# Naver 페이 들어가기
driver.get('https://order.pay.naver.com/home')
html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')
notices = soup.select('div.p_inr > div.p_info > a > span')

for n in notices:
    print(n.text.strip())
```

로그인이 잘 되고, 성공적으로 리스트를 받아오는 것을 확인해 볼 수 있다.

![Result]({{site.static_url}}/img/dropbox/2017-02-27%2022.41.46.png)

# 정리하기
---

Selenium은 웹 테스트 자동화 도구이지만, 멋진 크롤링 도구로 사용할 수 있다.

또한, BeautifulSoup와 함께 사용도 가능하기 때문에 크롤링을 하는데 제약도 줄어 훨씬 쉽게 크롤링을 할 수 있다.

```py
from selenium import webdriver
from bs4 import BeautifulSoup

# setup Driver|Chrome : 크롬드라이버를 사용하는 driver 생성
driver = webdriver.Chrome('/Users/beomi/Downloads/chromedriver')
driver.implicitly_wait(3) # 암묵적으로 웹 자원을 (최대) 3초 기다리기
# Login
driver.get('https://nid.naver.com/nidlogin.login') # 네이버 로그인 URL로 이동하기
driver.find_element_by_name('id').send_keys('naver_id') # 값 입력
driver.find_element_by_name('pw').send_keys('mypassword1234')
driver.find_element_by_xpath(
    '//*[@id="frmNIDLogin"]/fieldset/input'
    ).click() # 버튼클릭하기
driver.get('https://order.pay.naver.com/home') # Naver 페이 들어가기
html = driver.page_source # 페이지의 elements모두 가져오기
soup = BeautifulSoup(html, 'html.parser') # BeautifulSoup사용하기
notices = soup.select('div.p_inr > div.p_info > a > span')

for n in notices:
    print(n.text.strip())
```

# 다음 가이드
---

Selenium으로 많은 사이트에서 여러 정보를 가져와 볼 수 있게 되었습니다. 

하지만 가져온 데이터를 DB에 저장하려면 약간의 어려움이 따르게 됩니다.

다음 시간에는 Django의 ORM을 이용해 sqlite3 DB에 데이터를 저장해보는 방법에 대해 알아보겠습니다.

다음 가이드: [나만의 웹 크롤러 만들기(4): Django로 크롤링한 데이터 저장하기](/2017/03/01/HowToMakeWebCrawler-Save-with-Django/)