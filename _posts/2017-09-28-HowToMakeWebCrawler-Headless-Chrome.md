---
title: "나만의 웹 크롤러 만들기(7): 창없는 크롬으로 크롤링하기"
date: 2017-09-28
layout: post
categories:
- Python
- HowToMakeWebCrawler
published: true
image: /img/Crawling-with-HeadlessChrome.png
---

> 이번 가이드는 가이드 3편([Selenium으로 무적 크롤러 만들기](/2017/02/27/HowToMakeWebCrawler-With-Selenium/))의 확장편입니다. 아직 `selenium`을 이용해보지 않은 분이라면 먼저 저 가이드를 보고 오시는걸 추천합니다.

## HeadLess Chrome? 머리없는 크롬?

### HeadLess란?

Headless라는 용어는 '창이 없는'과 같다고 이해하시면 됩니다. 여러분이 브라우저(크롬 등)을 이용해 인터넷을 브라우징 할 때 기본적으로 창이 뜨고 HTML파일을 불러오고, CSS파일을 불러와 어떤 내용을 화면에 그러야 할지 계산을 하는 작업을 브라우저가 자동으로 진행해줍니다. 

하지만 이와같은 방식을 사용할 경우 사용하는 운영체제에 따라 크롬이 실행이 될 수도, 실행이 되지 않을 수도 있습니다. 예를들어 우분투 서버와 같은 OS에서는 '화면' 자체가 존재하지 않기 때문에 일반적인 방식으로는 크롬을 사용할 수 없습니다. 이를 해결해 주는 방식이 바로 Headless 모드입니다. 브라우저 창을 실제로 운영체제의 '창'으로 띄우지 않고 대신 화면을 그려주는 작업(렌더링)을 가상으로 진행해주는 방법으로 실제 브라우저와 동일하게 동작하지만 창은 뜨지 않는 방식으로 동작할 수 있습니다.

### 그러면 왜 크롬?

일전 가이드에서 `PhantomJS`(팬텀)라는 브라우저를 이용하는 방법에 대해 다룬적이 있습니다. 팬텀은 브라우저와 유사하게 동작하고 Javascript를 동작시켜주지만 성능상의 문제점과 크롬과 완전히 동일하게 동작하지는 않는다는 문제점이 있습니다. 우리가 크롤러를 만드는 상황이 대부분 크롬에서 진행하고, 크롬의 결과물 그대로 가져오기 위해서는 브라우저도 크롬을 사용하는 것이 좋습니다.

> 하지만 여전히 팬텀이 가지는 장점이 있습니다. WebDriver Binary만으로 추가적인 설치 없이 환경을 만들 수 있다는 장점이 있습니다.

윈도우 기준 크롬 59, 맥/리눅스 기준 크롬 60버전부터 크롬에 `Headless Mode`가 정식으로 추가되어서 만약 여러분의 브라우저가 최신이라면 크롬의 Headless모드를 쉽게 이용할 수 있습니다.

## 크롬 버전 확인하기

크롬 버전 확인은 크롬 브라우저에서 [chrome://version/](chrome://version/)로 들어가 확인할 수 있습니다.

![](/img/dropbox/ScreenShot2017-08-0112.47.57.png)

이와 같이 크롬 버전이 60버전 이상인 크롬에서는 'Headless'모드를 사용할 수 있습니다.

## 크롬드라이버(chromedriver) 업데이트

크롬 버전이 올라감에 따라 크롬을 조작하도록 도와주는 `chromedriver` 역시 함께 업데이트를 진행해야 합니다.

[https://sites.google.com/a/chromium.org/chromedriver/downloads](https://sites.google.com/a/chromium.org/chromedriver/downloads)

위 링크에서 Latest Release 옆 크롬드라이버를 선택해 OS별로 알맞은 zip파일을 받아 압축을 풀어줍시다.

## 기존 코드 수정하기

크롬의 헤드리스 모드를 사용하는 방식은 기존 selenium을 이용한 코드와 거의 동일합니다만, 몇가지 옵션을 추가해줘야합니다.

기존에 webdriver를 사용해 크롬을 동작한 경우 아래와 같은 코드를 사용할 수 있었습니다.

```python
from selenium import webdriver

# 유의: chromedriver를 위에서 받아준 
# chromdriver(windows는 chromedriver.exe)의 절대경로로 바꿔주세요!
driver = webdriver.Chrome('chromedriver')

driver.get('http://naver.com')
driver.implicitly_wait(3)
driver.get_screenshot_as_file('naver_main.png')

driver.quit()
```

위 코드를 동작시키면 크롬이 켜지고 파이썬 파일 옆에 `naver_main.png`라는 스크린샷 하나가 생기게 됩니다. 
이 코드는 지금까지 우리가 만들었던 코드와 큰 차이가 없는걸 확인해 보세요.

하지만 이 코드를 몇가지 옵션만 추가해주면 바로 Headless모드로 동작하게 만들어줄 수 있습니다.

```python
from selenium import webdriver

options = webdriver.ChromeOptions()
options.add_argument('headless')
options.add_argument('window-size=1920x1080')
options.add_argument("disable-gpu")
# 혹은 options.add_argument("--disable-gpu")

driver = webdriver.Chrome('chromedriver', chrome_options=options)

driver.get('http://naver.com')
driver.implicitly_wait(3)
driver.get_screenshot_as_file('naver_main_headless.png')

driver.quit()
```

위 코드를 보시면 `ChromeOptions()`를 만들어 `add_argument`를 통해 Headless모드인 것과, 크롬 창의 크기, 그리고 gpu(그래픽카드 가속)를 사용하지 않는 옵션을 넣어준 것을 볼 수 있습니다.

제일 중요한 부분은 바로 `options.add_argument('headless')`라는 부분입니다. 크롬이 Headless모드로 동작하도록 만들어주는 키워드에요. 그리고 크롬 창의 크기를 직접 지정해 준 이유는, 여러분이 일반적으로 노트북이나 데스크탑에서 사용하는 모니터의 해상도가 1920x1080이기 때문입니다. 즉, 여러분이 일상적으로 보는 것 그대로 크롬이 동작할거라는 기대를 해볼수 있습니다!

마지막으로는 `disable-gpu`인데요, 만약 위 코드를 실행했을때 GPU에러~가 난다면 `--disable-gpu`로 앞에 dash(-)를 두개 더 붙여보세요. 이 버그는 크롬 자체에 있는 문제점입니다. 브라우저들은 CPU의 부담을 줄이고 좀더 빠른 화면 렌더링을 위해 GPU를 통해 그래픽 가속을 사용하는데, 이 부분이 크롬에서 버그를 일으키는 현상을 보이고 있습니다. (윈도우 크롬 61버전까지는 아직 업데이트 되지 않았습니다. 맥 61버전에는 해결된 이슈입니다.)

그리고 `driver` 변수를 만들 때 단순하게 chromedriver의 위치만 적어주는 것이 아니라 `chrome_options`라는 이름의 인자를 함께 넘겨줘야 합니다.

이 `chrome_options`는 Chrome을 이용할때만 사용하는 인자인데요, 이 인자값을 통해 headless등의 추가적인 인자를 넘겨준답니다.

자, 이제 그러면 한번 실행해 보세요. 크롬 창이 뜨지 않았는데도 `naver_main_headless.png`파일이 생겼다면 여러분 컴퓨터에서 크롬이 Headless모드로 성공적으로 실행된 것이랍니다!

## Headless브라우저임을 숨기기

Headless모드는 CLI기반의 서버 OS에서도 Selenium을 통한 크롤링/테스트를 가능하게 만드는 멋진 모드지만, 어떤 서버들에서는 이런 Headless모드를 감지하는 여러가지 방법을 쓸 수 있습니다.

아래 글에서는 Headless모드를 탐지하는 방법과 탐지를 '막는'방법을 다룹니다.(창과 방패, 또 새로운 창!)

아래 코드의 TEST_URL은 [https://intoli.com/blog/making-chrome-headless-undetectable/chrome-headless-test.html](https://intoli.com/blog/making-chrome-headless-undetectable/chrome-headless-test.html) 인데요, 이곳에서 Headless모드가 감춰졌는지 아닌지 확인해 볼 수 있습니다.

### User Agent 확인하기

#### Headless 탐지하기

가장 쉬운 방법은 `User-Agent`값을 확인하는 방법입니다.

일반적인 크롬 브라우저는 아래와 같은 `User-Agent`값을 가지고 있습니다.

```
Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36
```

하지만 Headless브라우저는 아래와 같은 `User-Agent`값을 가지고 있습니다.

잘 보시면 'HeadlessChrome/~~'와 같이 'Headless'라는 단어가 들어가있는걸 확인할 수 있습니다!

```
Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/60.0.3112.50 Safari/537.36
```

#### Headless 탐지 막기

따라서 기본적으로 갖고있는 `User-Agent`값을 변경해줘야합니다.

이것도 위에서 사용한 `chrome_options`에 추가적으로 인자를 전달해주면 됩니다. 위코드를 약간 바꿔 아래와 같이 만들어보세요.

```python
from selenium import webdriver

TEST_URL = 'https://intoli.com/blog/making-chrome-headless-undetectable/chrome-headless-test.html'

options = webdriver.ChromeOptions()
options.add_argument('headless')
options.add_argument('window-size=1920x1080')
options.add_argument("disable-gpu")

# UserAgent값을 바꿔줍시다!
options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36")

driver = webdriver.Chrome('chromedriver', chrome_options=options)

driver.get(TEST_URL)

user_agent = driver.find_element_by_css_selector('#user-agent').text

print('User-Agent: ', user_agent)

driver.quit()
```

이제 여러분의 Headless크롬은 일반적인 크롬으로 보일거랍니다.

### 플러그인 개수 확인하기

#### Headless 탐지하기

크롬에는 여러분이 따로 설치하지 않아도 추가적으로 플러그인 몇개가 설치되어있답니다. PDF 내장 리더기같은 것들이죠.

하지만 Headless모드에서는 플러그인이 하나도 로딩되지 않아 개수가 0개가 됩니다. 이를 통해 Headless모드라고 추측할 수 있답니다.

아래 자바스크립트 코드를 통해 플러그인의 개수를 알아낼 수 있습니다.

```javascript
if(navigator.plugins.length === 0) {
    console.log("Headless 크롬이 아닐까??");
}
```

#### Headless 탐지 막기

물론 이 탐지를 막는 방법도 있습니다. 바로 브라우저에 '가짜 플러그인' 리스트를 넣어주는 것이죠!

아래 코드와 같이 JavaScript를 실행해 플러그인 리스트를 가짜로 만들어 넣어줍시다.

```python
from selenium import webdriver

TEST_URL = 'https://intoli.com/blog/making-chrome-headless-undetectable/chrome-headless-test.html'

options = webdriver.ChromeOptions()
options.add_argument('headless')
options.add_argument('window-size=1920x1080')
options.add_argument("disable-gpu")
options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36")
options.add_argument("lang=ko_KR") # 한국어!
driver = webdriver.Chrome('chromedriver', chrome_options=options)

driver.get('about:blank')
driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: function() {return[1, 2, 3, 4, 5];},});")
driver.get(TEST_URL)

user_agent = driver.find_element_by_css_selector('#user-agent').text
plugins_length = driver.find_element_by_css_selector('#plugins-length').text

print('User-Agent: ', user_agent)
print('Plugin length: ', plugins_length)

driver.quit()
```

위와 같이 JS로 navigator 객체의 `plugins`속성 자체를 오버라이딩 해 임의의 배열을 반환하도록 만들어주면 개수를 속일 수 있습니다.

> 단, 출력물에서는 Plugin length가 여전히 0으로 나올거에요. 왜냐하면 사이트가 로딩 될때 이미 저 속성이 들어가있기 때문이죠 :'( 그래서 우리는 좀 더 다른방법을 뒤에서 써볼거에요.

### 언어 설정

#### Headless 탐지하기

여러분이 인터넷을 사용할때 어떤 사이트를 들어가면 다국어 사이트인데도 여러분의 언어에 맞게 화면에 나오는 경우를 종종 보고, 구글 크롬을 써서 외국 사이트를 돌아다니면 '번역해줄까?' 하는 친절한 질문을 종종 봅니다.

이 설정이 바로 브라우저의 언어 설정이랍니다. 즉, 여러분이 선호하는 언어가 이미 등록되어있는 것이죠.

Headless모드에는 이런 언어 설정이 되어있지 않아서 이를 통해 Headless모드가 아닐까 '추측'할 수 있습니다.

#### Headless 탐지 막기

Headless모드인 것을 감추기 위해 언어 설정을 넣어줍시다. 바로 `add_argument`를 통해 크롬에 전달해 줄 수 있답니다.

```python
from selenium import webdriver

TEST_URL = 'https://intoli.com/blog/making-chrome-headless-undetectable/chrome-headless-test.html'

options = webdriver.ChromeOptions()
options.add_argument('headless')
options.add_argument('window-size=1920x1080')
options.add_argument("disable-gpu")
options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36")
options.add_argument("lang=ko_KR") # 한국어!
driver = webdriver.Chrome('chromedriver', chrome_options=options)

driver.get(TEST_URL)
driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: function() {return[1, 2, 3, 4, 5]}})")
# lanuages 속성을 업데이트해주기
driver.execute_script("Object.defineProperty(navigator, 'languages', {get: function() {return ['ko-KR', 'ko']}})")

user_agent = driver.find_element_by_css_selector('#user-agent').text
plugins_length = driver.find_element_by_css_selector('#plugins-length').text
languages = driver.find_element_by_css_selector('#languages').text

print('User-Agent: ', user_agent)
print('Plugin length: ', plugins_length)
print('languages: ', languages)

driver.quit()
```

> 단, 출력물에서는 language가 빈칸으로 나올거에요. 왜냐하면 사이트가 로딩 될때 이미 저 속성이 들어가있기 때문이죠 :'( 그래서 우리는 좀 더 다른방법을 뒤에서 써볼거에요.

### WebGL 벤더와 렌더러

#### Headless 탐지하기

여러분이 브라우저를 사용할때 WebGL이라는 방법으로 그래픽카드를 통해 그려지는 방법을 가속을 한답니다. 즉, 실제로 디바이스에서 돌아간다면 대부분은 그래픽 가속을 사용한다는 가정이 기반인 셈이죠.

> 사실 이 방법으로 차단하는 웹사이트는 거의 없을거에요. 혹여나 GPU가속을 꺼둔 브라우저라면 구별할 수 없기 때문이죠.

위 코드에서 사용해준 `disable-gpu`옵션은 사실 이 그래픽 가속을 꺼주는 것이에요. 따라서 이부분을 보완해 줄 필요가 있습니다.

#### Headless 탐지 막기

가장 쉬운 방법은 크롬이 업데이트되길 기대하고 `disable-gpu`옵션을 꺼버리는 것이지만, 우선은 이 옵션을 함께 사용하는 방법을 알려드릴게요.

위에서 사용한 script실행방법을 또 써 볼 것이랍니다.

```python
from selenium import webdriver

TEST_URL = 'https://intoli.com/blog/making-chrome-headless-undetectable/chrome-headless-test.html'

options = webdriver.ChromeOptions()
options.add_argument('headless')
options.add_argument('window-size=1920x1080')
options.add_argument("disable-gpu")
options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36")
options.add_argument("lang=ko_KR") # 한국어!
driver = webdriver.Chrome('chromedriver', chrome_options=options)

driver.get(TEST_URL)
driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: function() {return[1, 2, 3, 4, 5]}})")
driver.execute_script("Object.defineProperty(navigator, 'languages', {get: function() {return ['ko-KR', 'ko']}})")
driver.execute_script("const getParameter = WebGLRenderingContext.getParameter;WebGLRenderingContext.prototype.getParameter = function(parameter) {if (parameter === 37445) {return 'NVIDIA Corporation'} if (parameter === 37446) {return 'NVIDIA GeForce GTX 980 Ti OpenGL Engine';}return getParameter(parameter);};")

user_agent = driver.find_element_by_css_selector('#user-agent').text
plugins_length = driver.find_element_by_css_selector('#plugins-length').text
languages = driver.find_element_by_css_selector('#languages').text
webgl_vendor = driver.find_element_by_css_selector('#webgl-vendor').text
webgl_renderer = driver.find_element_by_css_selector('#webgl-renderer').text

print('User-Agent: ', user_agent)
print('Plugin length: ', plugins_length)
print('languages: ', languages)
print('WebGL Vendor: ', webgl_vendor)
print('WebGL Renderer: ', webgl_renderer)

driver.quit()
```

위 코드에서는 WebGL렌더러를 Nvidia회사와 GTX980Ti엔진인 '척' 하고 있는 방법입니다.

> 하지만 WebGL print 구문에서는 여전히 빈칸일거에요. 이 역시 이미 사이트 로딩시 속성이 들어가있기 때문이에요.

## Headless 브라우저 숨기는 방법 다함께 쓰기

위에서 사용한 방법 중 `User-Agent`를 바꾸는 방법 외에는 사실 모두 Javascript를 이용해 값을 추출하고 오버라이딩 하는 방식으로 바꿔보았습니다.

하지만 번번히 결과물이 빈칸으로 나오는 이유는 `driver.execute_script`라는 함수 자체가 사이트가 로딩이 끝난 후 (`onload()`이후) 실행되기 때문입니다.

즉, 우리는 우리가 써준 저 JS코드가 사이트가 로딩 되기 전 실행되어야 한다는 것이죠!

사실 기본 크롬이라면 사이트가 로딩 되기전 JS를 실행하는 Extension들을 사용할 수 있어요. 하지만 Headless크롬에서는 아직 Extension을 지원하지 않습니다 :'(

그래서 차선책으로 [mitmproxy](http://docs.mitmproxy.org/en/latest/mitmproxy.html)라는 Proxy 프로그램을 사용해볼거에요.

### mitmproxy 사용하기

우선 Mitmproxy를 pip로 설치해주세요.

```bash
pip install mitmproxy
```

그리고 proxy 처리를 해 줄 파일인 `inject.py`파일을 만들어주세요.

```python
# inject.py
from bs4 import BeautifulSoup
from mitmproxy import ctx

# load in the javascript to inject
with open('content.js', 'r') as f:
    content_js = f.read()

def response(flow):
    # only process 200 responses of html content
    if flow.response.headers['Content-Type'] != 'text/html':
        return
    if not flow.response.status_code == 200:
        return

    # inject the script tag
    html = BeautifulSoup(flow.response.text, 'lxml')
    container = html.head or html.body
    if container:
        script = html.new_tag('script', type='text/javascript')
        script.string = content_js
        container.insert(0, script)
        flow.response.text = str(html)

        ctx.log.info('Successfully injected the content.js script.')
```

이제 터미널에서 아래 명령어로 mitmproxy 서버를 띄워주세요.

```
mitmdump -p 8080 -s "inject.py"
```

> 이 서버는 크롤링 코드를 실행 할 때 항상 켜져있어야 해요!

이제 우리 크롤링 코드에 `add_argument`로 Proxy옵션을 추가해 주세요.

```python
from selenium import webdriver

TEST_URL = 'https://intoli.com/blog/making-chrome-headless-undetectable/chrome-headless-test.html'

options = webdriver.ChromeOptions()
options.add_argument('headless')
options.add_argument('window-size=1920x1080')
options.add_argument("disable-gpu")
options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36")
options.add_argument("proxy-server=localhost:8080")
driver = webdriver.Chrome('chromedriver', chrome_options=options)

driver.get(TEST_URL)
print(driver.page_source)

user_agent = driver.find_element_by_css_selector('#user-agent').text
plugins_length = driver.find_element_by_css_selector('#plugins-length').text
languages = driver.find_element_by_css_selector('#languages').text
webgl_vendor = driver.find_element_by_css_selector('#webgl-vendor').text
webgl_renderer = driver.find_element_by_css_selector('#webgl-renderer').text

print('User-Agent: ', user_agent)
print('Plugin length: ', plugins_length)
print('languages: ', languages)
print('WebGL Vendor: ', webgl_vendor)
print('WebGL Renderer: ', webgl_renderer)
driver.quit()
```

하지만 사실 이 코드는 정상적으로 동작하지 않을거에요. 헤드리스모드를 끄면 잘 돌아가지만 헤드리스모드를 켜면 정상적으로 동작하지 않아요. 바로 SSL오류 때문입니다.

크롬에서 SSL을 무시하도록 만들수 있고, 로컬의 HTTP를 신뢰 가능하도록 만들 수도 있지만 아직 크롬 Headless모드에서는 지원하지 않습니다.

정확히는 아직 webdriver에서 지원하지 않습니다. 

## 결론

아직까지는 크롬 Headless모드에서 HTTPS 사이트를 '완전히 사람처럼'보이게 한뒤 크롤링 하는 것은 어렵습니다. 하지만 곧 업데이트 될 크롬에서는 익스텐션 사용 기능이 추가될 예정이기 때문에 이 기능이 추가되면 복잡한 과정 없이 JS를 바로 추가해 진짜 일반적인 크롬처럼 동작하도록 만들 수 있으리라 생각합니다.

사실 서버 입장에서 위와 같은 요청을 보내는 경우 처리를 할 수 있는 방법은 JS로 헤드리스 유무를 확인하는 방법이 전부입니다. 즉, 서버 입장에서도 '식별'은 가능하지만 이로 인해 유의미한 차단은 하기 어렵습니다. 현재로서는 UserAgent 값만 변경해주어도 대부분의 사이트에서는 자연스럽게 크롤링을 진행할 수 있으리라 생각합니다.

## Reference

- [Detecting Chrome Headless](http://antoinevastel.github.io/bot%20detection/2017/08/05/detect-chrome-headless.html)
- [MAKING CHROME HEADLESS UNDETECTABLE](https://intoli.com/blog/making-chrome-headless-undetectable/)



