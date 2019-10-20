---
title: "V Lang 톺아보기[1]: 첫 만남"
date: 2019-10-20
layout: post
categories:
- vlang
published: true
image: https://beomi-tech-blog.s3.amazonaws.com/img/2019-10-20-162858.png
---

## V lang? V 언어?

> V lang의 Hello World 예제 모습

![image-20191021012923246](https://beomi-tech-blog.s3.amazonaws.com/img/2019-10-20-162923.png)

오늘 페이스북 진중님의 [타임라인 게시글에](https://www.facebook.com/hacker.golbin/posts/10157577567570040) 아래와 같이 V 언어에 대한 홍보(?)가 올라왔다.

![image-20191021012957993](https://beomi-tech-blog.s3.amazonaws.com/img/2019-10-20-162958.png)

컴파일도 엄청 빠르고, V 언어로 V 언어를 컴파일하는 (마치 pypy같은..!?), 게다가 Go보다 간단하고, 웹 프레임웍/ORM 내장에 동시성 처리와 패키지도 있다!

-라는 말에 낚에서 우와 신기하다! 하고나서 대체 어떤 언어인지 살펴보러 가보았다.

와, 스타가 벌써 12.5k+ (1만2천5백개+)라고?

> 참고: Python의 (사실상)표준 구현체인 CPython의 스타가 27.2k+, React가 138k+, Vue가 151k+(언제 이렇게..), Django가 44.7k+ 등으로 12.5k면 무척무척(!!) 많은 숫자다.

이정도면 스타트업으로 따지면 유니콘급 아닐까?

기왕 본 김에 Hello World 부터 한번 시작해 봐야겠다. - 라고 생각해서 기본 문법부터 간단 웹서버까지 한번 띄워보기로 생각했다.

> 이것이 바로 HDD, Hype Driven Dev....

- 공식 페이지: [https://vlang.io](https://vlang.io)

- Docs: [https://vlang.io/docs](https://vlang.io/docs)

당연히 시작은 공식 문서를 봐야지.

## 모든 시작은 설치부터

사실 Golang 관련해서 처음에 어려움을 겪은 적이 있었다. `GO_PATH` 관련이나 혹은 설치 패키지 등 드물게(거의 없지만) 발생하는 케이스에서 접근성이 약간 낮나? 하는 생각을 하기도 했다. (사실, 파이썬도 어떤어떤 경우(윈도우 계정명이 한글이라거나..)에는 설치가 꼬이기도 한다. 아주 가끔.)

그래서 '과연 설치가 잘 되기는 할까...?'하는 의문을 품었다. 게다가 아래 사진처럼 Linux는 바이너리 파일을 지원하지만, macOS와 Windows는 지원하지 않는 것을 보았다. 즉, 직접 빌드를 해야한다는 것!

![](https://beomi-tech-blog.s3.amazonaws.com/img/2019-10-20-162858.png)

직접 뭔가 빌드를 해보신 분들은 아시겠지만 빌드라는건 빌드 시간이 정말 빠를까? 하는 막연한 두려움이 생긴다.

그래도 어쩔수 없으니, 해보기로 한걸 해보기로 했다.

### 반전: 설치는 Git clone이 제일 오래 걸리더라

>  공식 설치방법: [Installing V from source](https://github.com/vlang/v#installing-v-from-source)

설치는 아주 단순하게 Git clone 이후 make 명령어만 치면 끝난다. 아래 세줄로 끝!

```shell
git clone https://github.com/vlang/v
cd v
make
```

실제로 걸리는 시간은 1분도 걸리지 않더라(!!)

실행되는 코드는 [vc](https://github.com/vlang/vc), V 컴파일러를 C로 변환한 레포를 받은 뒤 V를 빌드(!)해 바이너리 파일을 만든다.

> 성공한 빌드 환경:
>
> - macOS 10.14.6(18G87)
> - Apple clang version 11.0.0 (clang-1100.0.33.8) 
> - XCode 11.1

아무 폴더에서나 진행한 뒤 해당 폴더로 접근 가능하도록 시스템의 `PATH` 에 등록해주면 완료.

> 저는 Home폴더 내 `.v` 폴더를 만들고 그 안에 설치를 진행했습니다. 
>
> 사실 어디에 두던 상관없고, `sudo ./v symlink` 명령어를 통해 `/usr/local/bin` 에 심볼릭 링크를 걸어줄수도 있습니다.
>
> (이 설명을 뒤늦게 읽었어요....)

![image-20191021020214470](https://beomi-tech-blog.s3.amazonaws.com/img/2019-10-20-170215.png)

그리고 가장 먼저하는 Hello world!

v는 그냥 실행하면 마치 파이썬처럼 REPL 환경을 제공한다. (`>>>` 표시 보고 순간 파이썬인줄 알았다!)

![image-20191021020433704](https://beomi-tech-blog.s3.amazonaws.com/img/2019-10-20-170434.png)

분명히 컴파일 하는 언어인데 이렇게 잘 지원을 해준다.

그래도 기본적인 사용법은 파일을 만들고 👉 컴파일/빌드 해주고 👉 실행! 이니까, 그렇게 해보기로 했다.

## 파일로 시작하는 V lang

### Code Editor?

막상 파일로 시작하려니 엇, 이건 지원하는 코드 에디터나 IDE가 있나? 하는 의문이 들었다.

코드 에디터나 IDE의 지원에 따라 생산성이 달라지는건 확실하기 때문에, 없다면 상당히 회의적이게 될 것 같다는 생각을 했지만..

그런데 짜잔! VS Code에 `V` 라는 이름의 패키지로 V lang을 위한 하이라이팅, 테마, 코드 스니펫 등을 지원하고 있었다.

> 글 쓰는 중 0.0.7 👉 0.0.8로 버전업이 있었다. 빠른 버전업 와우!
>
> 설치는 VS Code 내 Extensions 마켓 플레이스에 'v' 라고만 검색하면 최상위에 뜬다.
>
> 검색이 어려우면 👉 [V for VSCode(설치링크)](https://marketplace.visualstudio.com/items?itemName=0x9ef.vscode-vlang) 에서 Install 클릭!

![image-20191021021735468](https://beomi-tech-blog.s3.amazonaws.com/img/2019-10-20-171735.png)

그러면 잘 될까? 가장 제일 먼저 나오는 Hello World를 만들어보았다.

![image-20191021022244624](https://beomi-tech-blog.s3.amazonaws.com/img/2019-10-20-172245.png)

여타 다른 언어와 동일한 수준으로 하이라이팅이 잘 된다!

> 괄호 레벨에 따라 컬러링 붙는건 다른 익스텐션으로, [Bracket Pair Colorizer 2(설치링크)](https://marketplace.visualstudio.com/items?itemName=CoenraadS.bracket-pair-colorizer-2) 를 설치하시면 됩니다. 꽤 좋아요. 추천!

### 첫 파일, 첫 빌드 

`01_hello.v` 라는, `.v` 확장자를 가진 첫 파일을 만들었다. (바로 위 파일이다!)

V를 통해 위 코드를 실행하는 것에는 두가지 방식이 있다.

1. V로 빌드 & Binary 실행
2. `v run` 명령어로 1번 통합실행

간단하게 v run으로 테스트를 해봤다. 실제로 기존 같은 이름의 바이너리 파일이 있으면 덮어쓰기를 하고 실행하는 것을 볼 수 있다. 만들어진 바이너리 파일은 실행 권한도 있어서 곧바로 실행할 수도 있다.

![image-20191021023627752](https://beomi-tech-blog.s3.amazonaws.com/img/2019-10-20-173628.png)

여타 다른 C언어나 Go처럼, 파일 내부의 `main()` 함수를 찾아서 실행하는 것은 동일하다.

하지만 `main` 함수가 없더라도 해당 파일 내부는 모두 실행이 된다.

아래 파일은 `main` 없이 만든 v 파일이다.

![image-20191021023817682](https://beomi-tech-blog.s3.amazonaws.com/img/2019-10-20-173818.png)

실제 실행을 해보면 아래와 같이 파일 내부에 있는 것을 잘 실행한다.

![image-20191021023847851](https://beomi-tech-blog.s3.amazonaws.com/img/2019-10-20-173848.png)

## 정리

크게 다른 부분은 없다. 하지만 몇가지 부분에서 놀랐다.

1. 설치에서 에러가 나지 않았다! 

   사실 이거 굉장히 중요한 부분이다. 사용자들의 접근성에 있어서 **매우** 중요함.

2. Code Editor가 지원된다

   이것 역시 처음 접할때 & 이후 개발시에도 편리함을 얼마나 지원하느냐의 이슈라 **매우** 중요함!

3. 불편하지 않고 '깔끔한데?' 라는 생각이 드는 문법

   분명히 빌드/컴파일을 해야하는 언어지만 마치 "타입 힌팅해서 쓰는 파이썬 + JS 조금.." 같다는 느낌적 느낌을 받았다. 좀 더 알아보고 느낌이 달라질수도 있겠지만, 현재 느낌은 마치 노션을 접했을때 느낀 산뜻한 느낌과 비슷한 기분. (물론 이걸 어디다 써먹을 수 있냐는 질문은 별도의 문제라는 것...)

간단하게 배우고 - 실제로 공식 문서에서 1시간이면 다 배운다고 한다는 말이 Fact - 빠르게 쓰는 것, 부담이 없게 느껴지는게 신기했다. 조금 더 알아봐야지.

