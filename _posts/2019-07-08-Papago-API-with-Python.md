---
title: "pypapago 개발기"
date: 2019-07-08
layout: post
categories:
  - python
  - howtomakewebcrawler
published: true
image: https://beomi-tech-blog.s3.amazonaws.com/img/2019-07-08-064243.png
---

## TL;DR

아래 내용을 통해 개발한 `pypapago` 는 현재 pypi에 올라가 있어 아래 명령어로 설치해 바로 사용할 수 있습니다.

```bash
pip install -U pypapago
```

> 2019.07.09일자 기준 최신버전은 `0.1.1.1` 입니다.

Github Repo: [https://github.com/Beomi/pypapago](https://github.com/Beomi/pypapago)

## 파파고 번역?

![image-20190708154324468](https://beomi-tech-blog.s3.amazonaws.com/img/2019-07-08-064325.png)

네이버에서는 [Papago](https://papago.naver.com/) 라는 이름으로 ML 기반과 사전 기반 두가지 방식의 번역과 언어 감지 등 여러가지 서비스를 제공한다. 한편 해당 서비스는 [파파고 공식 사이트](https://papago.naver.com/)에서 실제로 사용할 수 있지만 API를 이용해서 사용할 수도 있기 때문에, 개발자들이 API Key만 신청하면 한 번에 5천자, 그리고 하루에 1만자 이내로만 요청할 수 있다는 제한이 있다. (무료로 사용하는 경우)

![image-20190709233846881](https://beomi-tech-blog.s3.amazonaws.com/img/2019-07-09-143847.png)

한편 [papago.naver.com](https://papago.naver.com)에서 제공하는 웹 페이지 상에서의 번역은 추가적인 제한이 없기 때문에, 해당 웹 페이지를 파싱해서 어떤 API Call을 하고 있는지 뜯어보면 보다 많은 요청을 자유롭게 할 수 있지 않을까 싶었다.

## AJAX(XHR) Request 뜯어보기

파파고에 번역할 문장을 집어넣고 '번역' 버튼을 누를 때 이뤄지는 HTTP 요청을 크롬 개발자 도구로 살펴보면 다음과 같다.

![image-20190709234152264](https://beomi-tech-blog.s3.amazonaws.com/img/2019-07-09-144153.png)

실제로 `translatedText` 라는 키에 결과값이 잘 들어오는 것을 볼 수 있다.

한편 그렇다면 HTTP 요청을 보내는 방식이 어떻게 이뤄지는지 확인이 필요하다.

가장 먼저 살펴보는 것은 API Call이 어떤 URL(HOST)와 어떤 Method로 요청이 이뤄지는지 보는 것.

![image-20190709234351546](https://beomi-tech-blog.s3.amazonaws.com/img/2019-07-09-144352.png)

위 스샷을 살펴보면 `https://papago.naver.com/apis/n2mt/translate` 주소에 `POST` 방식으로 HTTP 요청을 보내고 있다는 것을 볼 수 있다.

`POST` 방식으로 보내는 HTTP 요청은 주로 `<form>` 내부의 FormData와 함께 보내는 경우가 많다. 따라서 아래쪽의 Form Data 항목을 살펴보면 다음과 같다.

![image-20190709234311481](https://beomi-tech-blog.s3.amazonaws.com/img/2019-07-09-144311.png)

하지만 우리가 입력한 "I am GROOT"라는 문장은 위 FormData 어디에서도 살펴볼 수가 없다. 어떻게 된 것일까?

## Base64 Encode & Decode

위와 같이 암호화된 것 처럼 보이는 데이터를 `base64` 로 디코딩을 해 보았다.

![image-20190709234642650](https://beomi-tech-blog.s3.amazonaws.com/img/2019-07-09-144643.png)

결과는 위와 같이 "I am GROOT"라는 부분이 잘 나오는 것을 볼 수 있다. 한편 앞쪽에 나와있는 이상한 문자열은 정체를 알 수 없었다.

따라서 우리가 실제로 조정하는 것이 필요한 `source`, `target`, `text`를 남기고 앞쪽은 base64로 인코딩 된 값을 그대로 가져왔다. (패키지 소스코드의 `SECRET_KEY` 부분.  사실은 secret이 아니다.)

## 코드로 만들어보자

### Basic setup

가장 기초적인 방법은 크롬에서 실제로 요청하는 HTTP를 그대로 따라하는 방법이다.

`Translator` Class를 생성할 때 기초적인 헤더들을 설정해 주고, 앞서 살펴보았던 요청에 필요한 base64로 인코딩 된 값들을 넣어준다. 

Github: [https://github.com/Beomi/pypapago/blob/0.1.1.1/pypapago/translator.py#L14-L33](https://github.com/Beomi/pypapago/blob/0.1.1.1/pypapago/translator.py#L14-L33)

```python
class Translator:
    """
    Main Translator Class
    """

    def __init__(self, regex_pattern=None, headers=None):
        self.regex_pattern = re.compile(regex_pattern or '[가-힣]+')
        self.headers = headers or {
            'device-type': 'pc',
            'origin': 'https://papago.naver.com',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'ko',
            'authority': 'papago.naver.com',
            'pragma': 'no-cache',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko)\
                           Chrome/75.0.3770.100 Safari/537.36',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'accept': 'application/json',
            'cache-control': 'no-cache',
            'x-apigw-partnerid': 'papago',
            'referer': 'https://papago.naver.com/',
            'dnt': '1',
        }
        self.SECRET_KEY = 'rlWxMKMcL2IWMPV6ImUwMWMwZWFkLWMyNDUtNDg2YS05ZTdiLWExZTZmNzc2OTc0MyIsImRpY3QiOnRydWUsImRpY3REaXNwbGF5Ijoz'
        self.QUERY_KEY = '0,"honorific":false,"instant":false,"source":"{source}","target":"{target}","text":"{query}"}}'
```

### String Type의 base64 값 만들기

앞서 사용한 `self.QUERY_KEY` 의 경우는 아직 UTF-8이기 때문에 base64로 인코딩 된 `str` 결과물이 필요하다.

이때 단순히 encode를 하면 type이 `str`이 아니라 `byte`타입이기 때문에 문제가 생긴다. (String와 Byte를 합칠 수 없다고 TypeError가 발생한다.)

Github: [https://github.com/Beomi/pypapago/blob/0.1.1.1/pypapago/translator.py#L35-L42](https://github.com/Beomi/pypapago/blob/0.1.1.1/pypapago/translator.py#L35-L42)

```python
    @staticmethod
    def string_to_base64(s):
        """
        Generate Base64 Encoded string
        :param s: Origin Text (UTF-8)
        :return: B64 encoded text (B64, still UTF-8 string)
        """
        return base64.b64encode(s.encode('utf-8')).decode('utf-8')
```

따라서 위와 같이 `.decode('utf-8')` 으로 다시한번 바꾸어주는 과정이 필요하다.

### HTTP 요청 보내기

위와 같이 준비가 끝나면 실제 HTTP 요청으로 보내는 것이 필요하다.

API Host도 알고, Method와 내용물도 알고 있으니 간단하게 보내기만 하면 된다.

Github: [https://github.com/Beomi/pypapago/blob/0.1.1.1/pypapago/translator.py#L44-L61](https://github.com/Beomi/pypapago/blob/0.1.1.1/pypapago/translator.py#L44-L61)

```python
    def translate(self, query, source='en', target='ko', verbose=False):
        """
        Main Translate function
        :param query: Original Text to translate
        :param source: Source(Original) text language [en, ko]
        :param target: Target text language [en, ko]
        :param verbose: Return verbose json data. Default: False
        :return: Translated text
        """
        data = {
            'data': self.SECRET_KEY + self.string_to_base64(
                self.QUERY_KEY.format(source=source, target=target, query=query)
            )
        }
        response = requests.post('https://papago.naver.com/apis/n2mt/translate', headers=self.headers, data=data)
        if not verbose:
            return response.json()['translatedText']
        return response.json()
```

실제로 `query`, `source`, `target` 을 우리가 바꾸어 사용하기 때문에 해당하는 값들을 넣어주고,  API 요청이 이뤄질때 실제로 넘어오는 결과값은 굉장히 길고 디테일한 정보를 담고있다. 이런 정보도 사용할 수 있도록 `verbose` 옵션을 통해 Raw json을 받을 수 있는 옵션도 넣어준다.

### Bulk/Parallel로 실행하기

한편 번역기를 사용할 때 한번에 하나가 아니라 여러개를 실행해야 하는 경우도 있다.

이런 경우를 위해 `multiprocessing` 을 사용해 기본적으로는 cpu코어 수(하이퍼스레딩은 2배)만큼 Worker를 띄워 사용하도록 설정해두고, 커스텀으로 worker 수를 지정할 수 있도록 옵션을 넣어준다.

> 실제로 worker를 30개를 넣으면 25배+로 빨라진다. WOW.

Github: [https://github.com/Beomi/pypapago/blob/0.1.1.1/pypapago/translator.py#L63-L80](https://github.com/Beomi/pypapago/blob/0.1.1.1/pypapago/translator.py#L63-L80)

```python
    def bulk_translate(self, queries, source='en', target='ko', workers=None, verbose=False):
        """
        Call Translate function in parallel
        :param queries: List of query texts
        :param source: Source(Original) text language [en, ko]
        :param target: Target text language [en, ko]
        :param workers: Python multiprocessing workers. Default: vCPU cores
        :param verbose: Return verbose json data. Default: False
        :return: List of translated texts
        """
        with Pool(workers or cpu_count()) as pool:
            result = list(tqdm(pool.imap(
                func=partial(self.translate, source=source, target=target, verbose=verbose),
                iterable=queries
            ), total=len(queries)))
            pool.close()
            pool.join()
            return result
```

그리고 Bulk로 작업을 하는 경우에는 보통의 경우 얼마나 진행되었는지 알고싶은 것이 당연하기 때문에 `imap` 와 `tqdm` 을 사용해 Progress bar를 화면(Jupyter Notebook도 지원함!)에 나타나도록 만들어주었다.

(아래는 Google colab에서 pypapago를 이용해 몇천개 번역을 worker 30개로 돌릴때 화면에 나타나는 모습)

![image-20190710000439238](https://beomi-tech-blog.s3.amazonaws.com/img/2019-07-09-150439.png)

## 맺으며

간단하게 써보려고 하다가 파파고 API의 요청건수가 가볍게 넘어버려서 (ㅠㅠ) + Google번역기 패키지가 자꾸 에러를 뿜어서 라는 두가지 이유로 인해 만들어보았다.

오랫만에 작업한 pypi 패키징이라 살짝 헷갈리기도 해서 `0.1.0` 배포 후 `0.1.1` 로 긴급 패치(의존성을 `setup.py` 에 넣는 것 잊음)를 했지만 정작 오타가 있어서 `0.1.1.1`이라는 이상한 버전으로 올리게 되었다는 이야기.

pypi 패키징 하는 부분도 간단하게 정리가 필요할 것 같다.



