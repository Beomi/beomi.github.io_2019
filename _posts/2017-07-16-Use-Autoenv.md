---
title: "Autoenv로 편리한 개발하기"
date: 2017-07-16
layout: post
categories:
- macOS
published: true
image: https://beomi-tech-blog.s3.ap-northeast-2.amazonaws.com/img/use-autoenv.jpg
---

> 이번 가이드는 macOS를 대상으로 합니다.

프로젝트를 여러가지를 동시에 진행하고 프로젝트에서 사용하는 개발환경이 다양해지다 보니 사용하게 되는 도구들이 많습니다.

Python에서는 `virtualenv`, `pyenv`등이 대표적이고 Node.js에서는 `nvm`이나 `n`등이 대표적인 사례입니다.

즉 시스템에 전역으로 설치되어있는 것과 다른 버전 혹은 다른 패키지들이 설치된 가상환경에서 개발을 진행해 각 프로젝트별로 다른 환경에서 개발을 진행합니다.

하지만 이러한 도구들을 사용하기 위해서는 프로젝트를 실행하기 전 특별한 명령어들(ex: `workon venv_name`등)을 사용해야 합니다.

Autoenv는 이러한 명령어들을 각 프로젝트 폴더 진입시 자동으로 실행할 수 있도록 도와줍니다.

## Autoenv가 작동하는 방법

Autoenv는 시스템의 `cd`명령어를 바꿔, 폴더 안에 진입한 후 폴더 안에 `.env`파일이 있는지를 탐색하고 만약 `.env`파일이 있으면 그 파일을 한줄한줄 사람이 터미널에 치듯 실행새줍니다.

예를 들어, `hello`라는 폴더 안의 `.env`에 아래와 같이 되어있다고 가정해 봅시다.

```bash
# .env파일
echo "Hello World!"
```

이후 이 `hello`폴더에 진입할 때마다 `Hello World!`가 출력됩니다.

```bash
~ $ cd hello
Hello World!
~/hello $
```

이처럼 여러가지 방법으로 이용할 수 있습니다. 

## Autoenv 설치하기

Autoenv는 다음 두 절차를 통해 쉽게 설치할 수 있습니다.

우선 `brew`로 설치해 줍시다. (HomeBrew는 [brew.sh](http://brew.sh)에서 설치할 수 있습니다.)

```bash
brew install autoenv  
```

다음으로는 autoenv 실행 스크립트를 `.zshrc`나 `.bash_profile` 파일의 끝부분에 적어줍시다.

```bash
# .zshrc 나 .bash_profile 의 파일 가장 끝
source /usr/local/opt/autoenv/activate.sh
```

> 만약 아직 ZSH을 설치하지 않았다면 [멋진 Terminal 만들기](/2017/07/07/Beautify-ZSH/)을 읽어보세요!

## 유의사항

![]({{site.static_url}}/img/dropbox/Screenshot%202017-07-16%2017.44.52.png)

`.env`파일 설정 후 첫 폴더 진입시 `.env`파일을 신뢰하고 실행할지 않을 지에 대한 동의가 나타납니다. 이 부분은 `.env`파일이 악의적으로 변경되었을때 사용자에게 알리기 위해서 있기 때문에 즐거운 마음으로 Y를 눌러줍시다.

## SSH키파일 등록하기

SSH키파일을 `.bash_profile`등에 등록해 터미널이 켜질때마다 불러오는 방법도 있지만, 그 대신 `ssh-add`명령어를 통해 직접 현재 터미널에만 제한적으로 불러오는 방법이 있습니다. 

만약 `~/.ssh`폴더 안에 `my_key_file.pem`이라는 키 파일들이 있다면 아래와 같이 `.env`를 구성할 수 있습니다.

```bash
# .env파일
ssh-add ~/.ssh/my_key_file.pem
```

이와 같이 구성하면 폴더에 진입시마다 아래와 같이 키 파일이 등록된다는 것을 확인할 수 있습니다.

```bash
~ $ cd project
Identity added: /Users/beomi/.ssh/my_key_file.pem (/Users/beomi/.ssh/my_key_file.pem)
~/project $
```

## Python 가상환경 관리하기

### venv를 사용할 경우

파이썬 3.4이후부터 내장된 venv를 이용한 경우 다음과 같이 `.env`를 구성할 수 있습니다.

```bash
# .env파일
source ./가상환경폴더이름/bin/activate
```

### virtualenv를 이용할 경우

venv와 동일합니다. 아래와 같이 `.env`를 구성해 주세요.

```bash
# .env파일
source ./가상환경폴더이름/bin/activate
```

### virtualenv-wrapper를 이용중인 경우

`workon`명령어를 그대로 사용할 수 있습니다. 아래와 같이 `.env`를 설정해 주세요. (저는 이 방법을 사용하고 있습니다.)

```bash
# .env파일
workon 가상환경이름
```

### Pyenv를 이용중인 경우 

pyenv에서는 `local`이라는 명령어를 통해 기본적으로 폴더별 Python 버전을 관리해 줍니다. 따라서 `.env`를 통해 Global설정을 하는 경우를 제외하면 사용하지 않는 것을 추천합니다.

## Node.js 개발환경 관리하기

### n을 사용할 경우

node버전을 관리해 주는 `n`은 `sudo`권한을 필요로 합니다. 시스템 전역에서 사용하는 node의 버전을 변경하기 때문입니다. 그래서 패스워드를 입력해 주는 과정이 필요할 수 있습니다. `.env`파일을 아래와 같이 만들어 주세요.

```bash
sudo n latest # 버전은 사용 환경에 맞게 입력해 주세요.
```

## 마무리

사실 Python을 주력 언어로 사용하다 보니 다른 언어들에 대해 언급은 적은 측면이 있습니다. 하지만 Autoenv 자체가 굉장히 심플한 스크립트로 이루어져 있기 때문에 필요에 맞춰 바꾸어 사용하는 것도 방법중 하나라고 생각합니다.

