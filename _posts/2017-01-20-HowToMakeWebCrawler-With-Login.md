---
title: "나만의 웹 크롤러 만들기(2): Login with Session"
date: 2017-01-20
layout: post
categories:
- Python
- HowToMakeWebCrawler
published: true
image: /img/2017-01-20-HowToMakeWebCrawler-With-Login/httpcookie.jpg
---

이전게시글: [나만의 웹 크롤러 만들기 with Requests/BeautifulSoup](/2017/01/20/HowToMakeWebCrawler/)

웹 사이트를 로그인 하는데 있어 쿠키와 세션을 빼놓고 이야기하는 것은 불가능하다.

이번 포스팅에서는 requests모듈을 이용해 로그인이 필요한 웹 사이트를 크롤링 하는 예제를 다룬다.

## 쿠키(Cookie)? 세션(Session)?

웹은 대다수가 HTTP기반으로 동작한다. 하지만 HTTP가 구현된 방식에서 웹 서버와 클라이언트는 지속적으로 연결을 유지한 상태가 아니라 요청(request)-응답(response)의 반복일 뿐이기 때문에, 이전 요청과 새로운 요청이 같은 사용자(같은 브라우저)에서 이루어졌는지를 확인하는 방법이 필요하다. 이 때 등장하는 것이 '쿠키'와 '세션'이다.

쿠키는 유저가 웹 사이트를 방문할 때 사용자의 브라우저에 심겨지는 작은 파일인데, Key - Value 형식으로 로컬 브라우저에 저장된다. 서버는 이 쿠키의 정보를 읽어 HTTP 요청에 대해 브라우저를 식별하게 된다.

그러나, 쿠키는 로컬에 저장된다는 근원적인 문제로 인해 악의적 사용자가 쿠키를 변조하거나 탈취해 정상적이지 않은 쿠키로 서버에 요청을 보낼 수 있다. 만약 '로그인 하였음'이라는 식별을, 로컬 쿠키만을 신뢰해 로그인을 한 상태로 서버가 인식한다면 쿠키 변조를 통해 관리자나 다른 유저처럼 행동할 수도 있는 것이다.

이로 인해 서버측에서 클라이언트를 식별하는 '세션'을 주로 이용하게 된다.

세션은 브라우저가 웹 서버에 요청을 한 경우 서버 내에 해당 세션 정보를 파일이나 DB에 저장하고 클라이언트의 브라우저에 session-id라는 임의의 긴 문자열을 할당하게 된다. 이때 사용되는 쿠키는 클라이언트와 서버간 연결이 끊어진 경우 삭제되는 메모리 쿠키를 이용한다.

## Requests의 Session

이전 게시글에서 다룬 requests모듈에는 Session이라는 도구가 있다.

```py
import requests

# Session 생성
s = requests.Session()
```

Session은 위와 같은 방식으로 만들 수 있다.

이렇게 만들어진 세션은 이전 게시글에서의 `requests`위치를 대신하는데, 이전 게시글의 코드를 바꿔본다면 아래와 같다.

```py
# parser.py
import requests

# Session 생성
s = requests.Session()

# HTTP GET Request: requests대신 s 객체를 사용한다.
req = s.get('http://clien.net/')

# HTML 소스 가져오기
html = req.text
# HTTP Header 가져오기
header = req.headers
# HTTP Status 가져오기 (200: 정상)
status = req.status_code
# HTTP가 정상적으로 되었는지 (True/False)
is_ok = req.ok
```

코드를 with구문을 사용해 좀 더 정리하면 아래와 같다. 위 코드와 아래코드는 정확히 동일하게 동작하지만, 위쪽 코드의 경우 Session이 가끔 풀리는 경우가 있어 (5번중 한번 꼴) 아래 코드로 진행하는 것을 추천한다.

```py
# parser.py
import requests

# Session 생성, with 구문 안에서 유지
with requests.Session() as s:
    # HTTP GET Request: requests대신 s 객체를 사용한다.
    req = s.get('http://clien.net/')
    # HTML 소스 가져오기
    html = req.text
    # HTTP Header 가져오기
    header = req.headers
    # HTTP Status 가져오기 (200: 정상)
    status = req.status_code
    # HTTP가 정상적으로 되었는지 (True/False)
    is_ok = req.ok
```

## 로그인하기

간단하게 로그인을 구현하기 위한 예시로 클리앙을 로그인 해 클리앙 장터(회원만 열람가능)를 Parsing해 보자.

<p align="center">
<img src="/img/2017-01-20-HowToMakeWebCrawler-With-Login/clien_web.png" />
</p>

크롬 개발자 도구를 통해 확인해보면 로그인 form Field에 id 입력 input태그의 name이 `mb_id`이고 pw 입력 input태그의 name이 `mb_password`인 것을 볼 수 있다.

<p align="center">
<img src="/img/2017-01-20-HowToMakeWebCrawler-With-Login/clien_login2.png" />
</p>

HTML form Field에서는 `name:입력값`이라는 Key:Value식으로 데이터를 전달한다.(주로 POST방식)

클리앙의 경우 `mb_id:사용자id`, `mb_password:사용자pw`라는 Key:Value로 입력을 받는다.

하지만 코드를 보면 onsubmit event에 `fhead_submit(this);`의 js코드가 걸려있는 것을 볼 수 있다.

fhead_submit 함수를 살펴보면 그냥 입력 유무만 확인하는 심플한 함수이다. 그리고 `f.action`으로 `cs2/bbs/login_check.php`로 POST 요청을 보낸다는 것을 확인할 수 있다. 우리에게 필요한 것은 POST요청이 가는 URL이기 때문에, `f.action`에 배정된 URL로 POST요청을 바로 보낼 것이다.

```js
// fhead_submit Function
function fhead_submit(f)
{

	if (f.mb_id.value =='아이디'){
		  alert("회원아이디를 입력하십시오.");
        f.mb_id.focus();
        return false;
	}
    if (!f.mb_id.value) {
        alert("회원아이디를 입력하십시오.");
        f.mb_id.focus();
        return false;
    }
	if (!f.mb_password.value) {
        alert("패스워드를 입력하십시오.");
      //  f.mb_password.focus();
        return false;
    }

    f.action = 'https://www.clien.net/cs2/bbs/login_check.php';
    return true;
}
```

우선 저 URL에 로그인 요청을 날리면 어떤 결과가 나오는지 살펴보자.

```py
# parser.py
import requests

# 로그인할 유저정보를 넣어주자 (모두 문자열)
LOGIN_INFO = {
    'mb_id': '사용자이름',
    'mb_password': '사용자패스워드'
}

# Session 생성, with 구문 안에서 유지
with requests.Session() as s:
    # HTTP POST request: 로그인을 위해 POST url와 함께 전송될 data를 넣어주자.
    login_req = s.post('https://www.clien.net/cs2/bbs/login_check.php', data=LOGIN_INFO)
    print(login_req.text)
```

위 코드를 정상적인 id와 pw를 넣어 실행해본 결과 아래와 같은 결과가 나온다. JavaScript코드인데, nowlogin이 추가된 클리앙의 홈페이지로 이동하는 듯 하다.

```js
<script language='JavaScript'> location.replace('http://www.clien.net..?nowlogin=1'); </script>
```

그렇다면 비정상적인 id와 pw를 넣으면 어떻게 나올까?

실행해보니 정상적인때와 다른 무척 긴 시간이 걸리며 (정상적일때는 0.1초, 지금은 약 5초) 아래와 같이 긴 HTML 문서가 나왔다.

```html
<meta http-equiv="content-type" content="text/html; charset=utf-8">
<script type="text/javascript">
[...(이하생략)...]
</script>
```

즉, 정상적으로 로그인이 된 경우 `.text`에는 `http://www.clien.net..?nowlogin=1`이라는 텍스트(js)가 들어있다는 것을 알 수 있다.

## 진짜 데이터를 가져와보자

이제 우리 코드를 좀 더 강화시켜보자. 로그인이 실패한 경우 Exception을 Raise하고, 성공일 경우에는 로그인이 필요한 회원 장터의 게시글을 가져와보자.

```py
# parser.py
import requests
from bs4 import BeautifulSoup as bs

# 로그인할 유저정보를 넣어주자 (모두 문자열)
LOGIN_INFO = {
    'mb_id': '사용자이름',
    'mb_password': '사용자패스워드'
}

# Session 생성, with 구문 안에서 유지
with requests.Session() as s:
    # HTTP POST request: 로그인을 위해 POST url와 함께 전송될 data를 넣어주자.
    login_req = s.post('https://www.clien.net/cs2/bbs/login_check.php', data=LOGIN_INFO)
    # 로그인에 성공한 경우 nowlogin=1이 포함된 스크립트가 response로 온다.
    if not 'http://www.clien.net..?nowlogin=1' in login_req.text:
        raise Exception('로그인에 실패했습니다.')
    # -- 여기서부터는 로그인이 된 세션이 유지됩니다 --
    # 이제 장터의 게시글 하나를 가져와 봅시다. 아래 예제 링크는 중고장터 공지글입니다.
    resp = s.get('http://www.clien.net/cs2/bbs/board.php?bo_table=sold&wr_id=796574')
    # BeautifulSoup으로 parsing을 해줍니다.
    # 이전 게시글과는 다르게 .content를 이용했는데,
    # 한국 웹 사이트의 경우 UTF-8에서도 일부 UnicodeError가 발생할 수 있어
    # 아래와 같은 resp.content 를 이용해 에러를 피했습니다.
    soup = bs(resp.content, 'html.parser')
    title = soup.select('div.view_title > div > h4 > span')
    contents = soup.select('#writeContents > p')
    # HTML을 제대로 파싱한 뒤에는 .text속성을 이용합니다.
    print(title[0].text) # 글제목
    for c in contents: # 글내용
        print(c.text)
```

위 예제를 실행해보면 아래와 같은 결과가 나올 것이다.

```
WARNING:root:Some characters could not be decoded, and were replaced with REPLACEMENT CHARACTER.
회원중고장터 이용규칙
이 게시판은 회원간 중고 제품의 거래를 위한 게시판입니다.
[...이하생략...]
```

Clien 페이지의 일부 문자가 UTF-8로 decode되지 못해 대체 문자로 표현되었다는 경고가 뜨지만, 대부분의 글자가 정상적으로 decode되어 글의 제목인 '회원중고장터 이용규칙'이 나오는 것을 확인할 수 있다.

## 그러나, 위 코드가 안먹힌다면?

일부 사이트의 경우 프론트 브라우저 단에서 ID와 PW를 이용해 암호화된 전송값을 보내는 경우가 있다. 또한, SPA등으로 인해 PageSource을 가져오는 것이 불충분한 경우가 자주 있다.

물론, JS파일을 분석해 수동으로 data에 넣어주는 방법도 있지만, 다음 포스팅에서 좀 더 간편히 실제 브라우저(혹은 Headless브라우저)를 이용해 로그인과 크롤링을 해보자.

다음 가이드: [나만의 웹 크롤러 만들기(3): Selenium으로 무적 크롤러 만들기](/2017/02/27/HowToMakeWebCrawler-With-Selenium/)
