---
title: "user mode로 설치한 pip 패키지 PATH에 등록하기"
date: 2018-02-12
layout: post
categories:
- Python
published: true
image: https://d1sr4ybm5bj1wl.cloudfront.net/img/2018-02-12-Add-packages-installed-with-pip-usermode.png
---

> 이번 글은 macOS 기준입니다.

## pip 유저모드?

파이썬 패키지 매니저인 `pip`를 사용할 때 종종 이용하는 옵션이 `--user`, 즉 사용자 디렉토리에 패키지 패키지를 설치하는 방법을 통해 `sudo`처럼 권한 상승 없이 패키지들을 설치해 사용할 수 있습니다.

이때 차이가 나는 부분은 저 패키지들이 어떤 디렉토리(폴더)에 설치되는지입니다. 

여러분이 `brew`를 통해 python3을 설치했다면 아래와 같이 파이썬이 `/usr/local/bin`에 설치되어있는 것을 볼 수 있습니다.

![]({{site.static_url}}/img/dropbox/2018-02-12PM1.09.36.png)

일반적으로 `pip3 install ...`와 같은 방식을 통해 패키지를 설치한다면 패키지들의 바로가기들이 저 폴더에 자리잡게 됩니다.

그리고 `/usr/local/bin`은 시스템 환경변수 `PATH`에 기본적으로 등록되어있기 때문에 추가적인 설정 없이도 명령어들, 예를들어 `fabric3`을 설치했다면 `fab`와 같은 명령어들을 사용할 수 있습니다.

## 뭐가 문제인가요?

하지만 `--user` 옵션을 통해 설치할 경우 패키지가 설치되는 경로는 위 경로 대신 `~/Library/Python/3.6/bin`에 설치됩니다. (python3.6기준)

하지만 해당 경로는 시스템 환경변수 `PATH`에 등록되어있지 않아 아래와 같이 `fabric3`을 설치했지만 `fab`명령어를 사용할 수 없습니다.

![]({{site.static_url}}/img/gif_2018-02-12-Add-packages-installed-with-pip-usermode-1.gif)

## 어떻게 해결하나요?

해결 방법은 간단합니다. `~/Library/Python/3.6/bin`를 시스템 `PATH` 환경 변수에 추가해주면 됩니다.

### zsh를 사용하신다면

zsh를 사용한다면 `.zshrc`파일에서 아래와 같이 입력해주면 됩니다.

> Python3.5나 3.4를 사용한다면 숫자 `3.6`을 `3.5`,`3.4`로 버전에 맞게 바꿔 사용하세요.

```sh
echo 'export PATH="/Users/$(whoami)/Library/Python/3.6/bin":$PATH"' >> .zshrc
```

### bash를 사용하신다면

zsh를 사용한다면 `.bashrc`파일에서 아래와 같이 입력해주면 됩니다.

```sh
echo 'export PATH="/Users/$(whoami)/Library/Python/3.6/bin":$PATH"' >> .bashrc
```

이제 터미널을 종료한 뒤 다시 켜면 `fab`등 명령어가 잘 실행되는 것을 볼 수 있습니다.
