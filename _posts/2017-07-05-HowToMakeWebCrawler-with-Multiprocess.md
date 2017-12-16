---
title: "나만의 웹 크롤러 만들기(6): N배빠른 크롤링, multiprocessing!"
date: 2017-07-05
layout: post
categories:
- Python
- HowToMakeWebCrawler
published: true
image: https://beomi-tech-blog.s3.ap-northeast-2.amazonaws.com/img/crawling_with_multiprocessing.png
---

> 좀 더 보기 편한 [깃북 버전의 나만의 웹 크롤러 만들기](https://beomi.github.io/gb-crawling/)가 나왔습니다!

> 이전 가이드: [나만의 웹 크롤러 만들기(5): 웹페이지 업데이트를 알려주는 Telegram 봇](/2017/04/20/HowToMakeWebCrawler-Notice-with-Telegram/)

## 들어가기전..

나만의 웹 크롤러 만들기 6번째 가이드는 크롤링을 병렬화를 통해 빠르게 진행하는 방법을 안내합니다.

지금까지 만들어온 크롤러들은 모두 한번에 하나의 요청만을 처리하고 있습니다. 물론 지금까지 따라오셨다면 충분히 크롤러들을 여러분의 의도에 맞게 잘 수정해서 사용해보셨을거라 생각합니다.

하지만 한 페이지만을 여유로운 시간을 갖고 크롤링하는 것이 아니라 여러 사이트 혹은 여러 페이지를 좀더 빠르게 긁어오는 방법에는 역시 N개를 띄우는 방법이 제일 낫다고 볼 수 있습니다.

만약 100만개의 페이지가 있다면 1~25만/25만1~50만/50만1~75만/75만1~100만와 같이 4개로 쪼개서 돌린다면 더 빠르게 도는 것은 당연합니다.

하지만 전달해주는 페이지의 목록이나 페이지 숫자에 직접 저 수들을 입력하는 것은 상당히 귀찮은 일이기도 하고, 크롤링이 '자동화'를 위한 것이라는 면에 반하는 측면도 있습니다. 따라서 우리는 Python 자체에 내장된 병렬화 모듈을 사용할 예정입니다.

Python을 이용할 때 프로그램을 병렬적으로 처리하는 방법은 여러가지가 있습니다. 하지만 우리가 하는 일은 연산이 아니고 IO와 네트워크가 가장 큰 문제이기 때문에 `multiprocessing`을 사용합니다.

> `threading` 모듈도 사용 가능합니다. 하지만 `multiprocessing`모듈을 추천합니다. `threading`모듈은 싱글 프로세스 안의 스레드에서 동작하지만 이로인해 GIL의 제약에 걸리는 경우가 생기기 때문에 성능 향상에 제약이 있습니다. (물론 우리는 CPU 연산보다 IO/네트워크로 인한 지연이 훨씬 크기 때문에 큰 차이는 없습니다.)

## 멀티프로세스란?

프로세스란 '실행 중인 프로그램'을 의미합니다. 간단하게 말해 멀티프로세스는 프로세스를 여러개 띄우는 것, 즉 프로그램을 여러개 실행시키는 것이라고 볼 수 있습니다.

Python에는 멀티프로세싱 프로그램을 위한 모듈이 `multiprocessing`이라는 이름으로 내장되어 있습니다. 

가장 단순한 예시로, 임의의 숫자 리스트 (ex: `[20, 25, 30, 35]`)를 받고 그 자리의 피보나치 수를 구해주는 프로그램이 있다고 가정해 봅시다.

만약 for문을 통해 리스트를 순회하며 계산한다면 아래와 같이 코드를 짤 수 있습니다.

> 주의: 명백한 코드 실행 시간 차이를 보여주기 위한 느린 코드입니다.

```python
import time

start_time = time.time()

def fibo(n): # 회귀적 피보나치 함수
    if n == 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fibo(n-1) + fibo(n-2)

num_list = [31, 32, 33, 34]
result_list = []
for num in num_list:
    result_list.append(fibo(num))

print(result_list)
print("--- %s seconds ---" % (time.time() - start_time))
```

실행을 해보면 다음과 같이 약 7s가 걸리는 것을 볼 수 있습니다. 너무 오래걸리네요.

<script type="text/javascript" src="https://asciinema.org/a/c6iRt6q82WDuFruFfcFlmmrjn.js" id="asciicast-c6iRt6q82WDuFruFfcFlmmrjn" async></script>

그렇다면 `multiprocessing`을 이용하면 어떨까요?

```python
from multiprocessing import Pool
import time

start_time = time.time()

def fibo(n):
    if n == 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fibo(n-1) + fibo(n-2)

def print_fibo(n): # 피보나치 결과를 확인합니다.
    print(fibo(n))

num_list = [31, 32, 33, 34]
    
pool = Pool(processes=4) # 4개의 프로세스를 사용합니다.
pool.map(print_fibo, num_list) # pool에 일을 던져줍니다.

print("--- %s seconds ---" % (time.time() - start_time))
```

실행을 해 봅시다!

<script type="text/javascript" src="https://asciinema.org/a/gwOTuBQgs11J6ckOlgIERAdF5.js" id="asciicast-gwOTuBQgs11J6ckOlgIERAdF5" async></script>

확실히 빨라진 모습을 볼 수 있습니다. 3s, 즉 절반정도로 줄어든 것을 확인 할 수 있습니다.

## 크롤링 병렬화 하기

이번 가이드에서는 위에서 사용한 모듈인 `multiprocessing`을 이용해 진행합니다. 크롤링은 위에서 사용한 것처럼 연산집중적이지 않습니다. 그래서 크롤링하는 함수를 만들어두었다면 그 함수를 그대로 사용하시면 됩니다.

이번 가이드에서는 첫번째 가이드에서 사용했던 함수를 약간 변형해 사용해 봅니다.

### 하나씩 크롤링 하기

```python
# parser.py
import requests
from bs4 import BeautifulSoup as bs
import time


def get_links(): # 블로그의 게시글 링크들을 가져옵니다.
    req = requests.get('https://beomi.github.io/beomi.github.io_old/')
    html = req.text
    soup = bs(html, 'html.parser')
    my_titles = soup.select(
        'h3 > a'
        )
    data = []

    for title in my_titles:
        data.append(title.get('href'))
    return data

def get_content(link):
    abs_link = 'https://beomi.github.io'+link
    req = requests.get(abs_link)
    html = req.text
    soup = bs(html, 'html.parser')
    # 가져온 데이터로 뭔가 할 수 있겠죠?
    # 하지만 일단 여기서는 시간만 확인해봅시다.
    print(soup.select('h1')[0].text) # 첫 h1 태그를 봅시다.

if __name__=='__main__':
    start_time = time.time()
    for link in get_links():
        get_content(link)
    print("--- %s seconds ---" % (time.time() - start_time))
```

약 7.3s가 걸리는 것을 아래에서 확인해 볼 수 있습니다.

<script type="text/javascript" src="https://asciinema.org/a/WgPLMFdo60dedeMD7PO53uyNZ.js" id="asciicast-WgPLMFdo60dedeMD7PO53uyNZ" async></script>

### Multiprocessing으로 병렬 크롤링하기

이제 좀더 빠른 크롤링을 위해 병렬화를 도입해 봅시다.

`multiprocessing`에서 `Pool`을 import 해 줍시다.

그리고 pool에 `get_content`함수를 넣어 줍시다.

```python
# parser.py
import requests
from bs4 import BeautifulSoup as bs
import time

from multiprocessing import Pool # Pool import하기


def get_links(): # 블로그의 게시글 링크들을 가져옵니다.
    req = requests.get('https://beomi.github.io/beomi.github.io_old/')
    html = req.text
    soup = bs(html, 'html.parser')
    my_titles = soup.select(
        'h3 > a'
        )
    data = []

    for title in my_titles:
        data.append(title.get('href'))
    return data

def get_content(link):
    abs_link = 'https://beomi.github.io'+link
    req = requests.get(abs_link)
    html = req.text
    soup = bs(html, 'html.parser')
    # 가져온 데이터로 뭔가 할 수 있겠죠?
    # 하지만 일단 여기서는 시간만 확인해봅시다.
    print(soup.select('h1')[0].text) # 첫 h1 태그를 봅시다.

if __name__=='__main__':
    start_time = time.time()
    pool = Pool(processes=4) # 4개의 프로세스를 사용합니다.
    pool.map(get_content, get_links()) # get_contetn 함수를 넣어줍시다.
    print("--- %s seconds ---" % (time.time() - start_time))
```

<script type="text/javascript" src="https://asciinema.org/a/yITked7NP4bM7nPaAZM4CcIYF.js" id="asciicast-yITked7NP4bM7nPaAZM4CcIYF" async></script>

약 2.8초로 약 3~4배의 속도 향상이 있었습니다.

## 마무리 및 팁

멀티프로세싱으로 크롤링을 할 때 유의할 점은 Pool을 생성시 `processes`의 개수가 많다고 빠르지는 않다는 점을 유의하셔야 합니다.

두번째 parser.py파일을 실행 시 process를 4개인 경우 2.8s, 8개로 할 때 1.85s, 16개로 할 때 0.96s, 32개로 할 때 0.63s로 속도 향상이 두드러집니다. 하지만 64개로 할 때는 오히려 1.30s로 속도 지연이 발생합니다. 프로세스는 CPU코어(Hyper-Thread인 경우 2배) 개수의 2배(ex: 4코어 i5는 8개, 4코어8스레드인 i7은 16개)로 하면 가장 빠르지는 않지만 적당히 빠른 속도를 가져다줍니다.

다음으로는 웹 사이트에서 이러한 공격적 크롤링을 차단할 수 있다는 문제입니다. 잘 관리되는 사이트의 경우 이와 같은 공격적 크롤링은 사실 시스템 관리자에게 있어서는 공격 시도와 같이 보일 수 있기 때문에 적당한 속도를 유지하며 `robots.txt`를 존중해주는 것이 중요합니다.

무작정 빠르게 긁는다고 빠르지 않은 점에는 이 코드를 실행하는 컴퓨터의 네트워크 환경 자체가 제약이 되기도 합니다. 만약 핫스팟이나 테더링을 이용하거나 인터넷 속도에 제약을 받는 환경에서 이러한 작업을 돌린다면 오히려 네트워크쪽 문제로 인해 에러나 지연이 발생할 가능성이 높습니다. 이런 경우에는 `processes`개수를 2~4개로 맞춰서 크롤링을 진행하는 것이 최적의 속도를 이끌어낼 수도 있습니다.

다음 가이드에서는 실제 명령어를 받아 사용자들의 정보를 저장하고 사용자들에게 실제로 유용한 정보(예: 글 제목과 링크)를 보내주는 내용으로 진행할 예정입니다.

