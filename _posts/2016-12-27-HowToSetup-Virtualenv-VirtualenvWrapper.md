---
title: "Virtualenv/VirtualenvWrapper OS별 설치&이용법"
date: 2016-12-27 17:00:00+09:00
layout: post
categories:
- Python
- MacOS
- Ubuntu
- Windows
- DevEnv
image: /img/old_post/python-virtualenv.jpg
---

# Virtualenv란?

Virtualenv란 시스템 OS에 설치된 주 python뿐만 아니라 여러 버전의 Python과 프로젝트별로 다른 종류의 라이브러리를 사용하는 것에 있어 가장 핵심된 기능을 제공합니다.

예를들어, 어떤 옛날 프로젝트에서는 Python2.7버전에 pip로 Django1.6을 사용했다고 가정해봅시다. 하지만 이번에 새로 시작하는 프로젝트는 Python3.6에 pip로 Django1.10을 사용하려고 합니다. 물론 가장 쉬운 방법은 개발 환경별로 다른 컴퓨터를 사용하는 것이지만, 공간적/금전적/편의적으로 어렵습니다.

따라서 우리는 Python실행파일과 pip로 설치된 라이브러리들을 독립된 폴더에 넣어버리는 방법을 선택할 수 있는데, 이것이 Virtualenv의 핵심입니다.

아래 가이드는 OS별로 나누어져있습니다. [\[MAC OS가이드\]](#macos) [\[LINUX 가이드(UBUNTU)\]](#linux) [\[WINDOWS 가이드\]](#windows)

2016.12.30 기준 MAC OS가 완성되어있습니다.

<span id="macos"></span>

# MAC OS(OS X)의 경우

## Virtualenv를 설치해보자 [MAC OS]

MAC OS에는 시스템 전역에 기본적으로 Python2가 설치되어있기 때문에 아래 명령어로 쉽게 pip를 설치할 수 있습니다.

```sh
$ sudo easy_install pip
```

만약 sudo로 시스템 전역에 설치하기가 싫다면 [HomeBrew](http://brew.sh/)를 이용해 Python을 유저영역에 설치할 수도 있습니다.

```sh
$ brew install python
#Python3의 경우는 brew install python3)
```

pip가 성공적으로 설치되었는지 확인하려면 다음 명령어로 pip의 버전을 확인해 보면 됩니다.

```sh
$ pip -V
#Python3 pip의 경우에는 pip3 -V
```

![](https://www.dropbox.com/s/ouazxdbx2ql7cxa/%EC%8A%A4%ED%81%AC%EB%A6%B0%EC%83%B7%202016-12-27%2017.56.54.png?dl=1)

만약 pip나 pip3이라는 명령어가 먹히지 않는다면 아래의 명령어로 Python의 모듈로서 pip를 호출할 수 있습니다.

```sh
# Python2의 경우
$ python -m pip -V

# Python3의 경우
$ python3 -m pip -V
```

![](https://www.dropbox.com/s/1iq7nss1tgenriu/%EC%8A%A4%ED%81%AC%EB%A6%B0%EC%83%B7%202016-12-27%2017.57.57.png?dl=1)

Virtualenv와 VirtualenvWrapper는 pip를 통해 설치가 가능합니다.

```sh
# Python2의 경우
$ pip install virtualenv virtualenvwrapper

# Python3의 경우
$ pip3 install virtualenv virtualenvwrapper
```

만약 `pip`/`pip3` 명령이 먹지 않는다면 아래 명령어로 대체할 수 있습니다.
(시스템에 easy_install로 pip를 설치한 경우 sudo권한이 필요할 수 있는데, 이때는 `sudo pip install`으로 명령어 앞에 sudo를 붙여줍시다.)

```sh
# Python2 pip의 경우
$ python -m pip install virtualenv virtualenvwrapper

# Python3 pip의 경우
$ python3 -m pip install virtualenv virtualenvwrapper
```

지금까지 사용한 `pip`와 `pip3`은 virtualenv를 어느 pip에 설치할까에 대한 내용일 뿐, 파이썬 가상환경에 어떤 Python이 설치될지와는 무관합니다.

## Virtualenv의 기본적 명령어 [MAC OS]

Virtualenv는 기본적으로 아래의 명령어로 동작합니다.

```sh
$ virtualenv --python=파이썬버전 가상환경이름
# ex)
# $ virtualenv --python=python3.5 test_env
# $ virtualenv --python=python2.7 test_env2
```

![](https://www.dropbox.com/s/hehcdglqiu14mik/%EC%8A%A4%ED%81%AC%EB%A6%B0%EC%83%B7%202016-12-27%2018.13.11.png?dl=1)

이와 같이 Python버전을 명시해주고 가상환경을 만들 수 있습니다. (단, 선택할 Python은 시스템에 깔려있는 버전이어야 합니다.)

> 만약

> ![](https://www.dropbox.com/s/l0wwqtuoch9tw8r/%EC%8A%A4%ED%81%AC%EB%A6%B0%EC%83%B7%202016-12-30%2019.18.33.png?dl=1)

> 와 같이 The path x.x does not exist라는 에러가 난다면 PYTHON의 PATH을 절대경로로 맞춰줘야 합니다. `which python3`을 했을 때 `/usr/bin/python3`이 나왔다면, `virtualenv --python=/usr/bin/python3`와 같이 절대경로로 입력해주시면 됩니다.

> ![](https://www.dropbox.com/s/bnb3r5fephimoig/%EC%8A%A4%ED%81%AC%EB%A6%B0%EC%83%B7%202016-12-30%2019.23.40.png?dl=1)

만든 가상환경에 진입(가상환경을 활성화)하려면 아래 명령어를 이용하면 됩니다.

```sh
$ source 가상환경이름/bin/activate
```

Python3이 설치된 test_env로 진입한 경우

![](https://www.dropbox.com/s/xiymbhfyezjj6wa/%EC%8A%A4%ED%81%AC%EB%A6%B0%EC%83%B7%202016-12-27%2018.14.28.png?dl=1)

Python2가 설치된 test_env2로 진입한 경우

![](https://www.dropbox.com/s/ovxyqj9ig38433h/%EC%8A%A4%ED%81%AC%EB%A6%B0%EC%83%B7%202016-12-27%2018.15.53.png?dl=1)

각각 다른 python버전이 실행되고 있다는 것을 알 수 있습니다.

이후 pip를 통해 외부 모듈과 라이브러리들을 설치하는 경우, source 명령어로 가상환경에 진입하지 않으면 라이브러리들을 불러쓸 수 없게됩니다. 즉, 프로젝트 별로 다른 라이브러리만이 설치된 환경을 구성한 것이죠.

## VirtualenvWrapper 설정하기

VirtualEnv를 사용하기 위해서는 `source`를 이용해 가상환경에 진입합니다. 그러나, 이 진입 방법은 가상환경이 설치된 위치로 이동해야되는 것 뿐 아니라 가상환경이 어느 폴더에 있는지 일일이 사용자가 기억해야 하는 단점이 있습니다. 이를 보완하기 위해 `VirtualenvWrapper`를 사용합니다.

또한, VirtualenvWrapper를 사용할 경우 터미널이 현재 위치한 경로와 관계없이 가상환경을 활성화할 수 있다는 장점이 있습니다.

VirtualenvWrapper는 `.bashrc`나 `.zshrc`에 약간의 설정과정을 거쳐야 합니다.

우선 홈 디렉토리로 이동해보세요.

```sh
$ cd ~
```

가상환경이 들어갈 폴더 `.virtualenvs`를 만들어주세요.

```sh
$ mkdir ~/.virtualenvs
```

그리고 홈 디렉토리의 `.bashrc`나 `.zshrc`의 파일 제일 마지막에 아래 코드를 복사해 붙여넣어줍시다.
(파일이 없다면 만들어 사용하시면 됩니다.)

```sh
# python virtualenv settings
export WORKON_HOME=~/.virtualenvs
export VIRTUALENVWRAPPER_PYTHON='$(command \which python3)'  # Usage of python3
source /usr/local/bin/virtualenvwrapper.sh
```

저장하고 나온 후 터미널을 종료후 새로 켜주면, VirtualenvWrapper의 명령어들을 사용할 수 있습니다.

만약 `/usr/local/bin/virtualenvwrapper.sh`파일이 존재하지 않는다면 다음 명령어로 `virtualenvwrapper.sh`파일을 찾아서 위 코드를 바꿔 사용하세요.

```sh
find /usr -name virtualenvwrapper.sh
```

## VirtualenvWrapper 명령어들

VirtualenvWrapper의 명령어는 여러가지가 존재하지만, 이 포스팅에서는 기본적인 것만 다루고 넘어갑니다.

- 가상환경 만들기

```sh
$ mkvirtualenv 가상환경이름
# 예시
# $ mkvirtualenv test_env3
```

`mkvirtualenv` 명령어를 사용할 경우 홈 디렉토리의 `.virtualenvs`폴더 안에 `가상환경이름`을 가진 폴더(`test_env3`)가 생깁니다.

- 가상환경 지우기

```sh
$ rmvirtualenv 가상환경이름
# 예시
# $ rmvirtualenv test_env3
```

`rmvirtualenv` 명령어를 사용할 경우 `mkvirtualenv`로 만든 가상환경을 지워줍니다.

만든 가상환경을 지우는 방법은 이방법 뿐 아니라 홈 디렉토리의 `.virtualenvs`폴더 안의 가상환경이름을 가진 폴더를 지우는 방법도 있습니다.

- 가상환경 진입하기 + 가상환경 목록 보기

```sh
$ workon 가상환경이름
# 가상환경으로 진입시 앞에 (가상환경이름)이 붙습니다.
(가상환경이름) $
# 예시
# $ workon test_env3
# (test_env3) $
```

`workon`명령어를 통해 `mkvirtualenv`로 만든 가상환경으로 진입할 수 있습니다.

`workon`명령어를 가상환경이름 없이 단순하게 칠 경우, 현재 만들어져있는 가상환경의 전체 목록을 불러옵니다.

```sh
$ workon
test_env3
```

- 가상환경 빠져나오기

```sh
(가상환경이름) $ deactivate
$
# 예시
# (test_env3) $ deactivate
# $
```

가상환경에서 빠져나오는 것은 다른것들과 동일하게 `deactivate`명령어로 빠져나올 수 있습니다.


<span id="linux"></span>

# LINUX(UBUNTU)의 경우

## Virtualenv를 설치해 보자 [LINUX(UBUNTU)]

Ubuntu의 경우에는 14버전 기준으로 Python2와 Python3이 기본적으로 설치되어있습니다.

> Ubuntu16에서는 Python3이 기본입니다.

하지만 `pip`/`pip3`이 설치되어있지 않을 수 있기 때문에 `python-pip`나 `python3-pip`를 설치해야 합니다.

```sh
# APT를 업데이트
$ sudo apt-get update && apt-get upgrade -y
# Python2를 이용할 경우
$ sudo apt-get install python-pip python-dev
# Python3을 이용할 경우
$ sudo apt-get install python3-pip python3-dev
```

![](https://www.dropbox.com/s/62h1l9cfjvy3kxx/%EC%8A%A4%ED%81%AC%EB%A6%B0%EC%83%B7%202016-12-30%2018.56.35.png?dl=1)

> 꼭 `python-dev`와 `python3-dev`를 설치하지 않아도 됩니다. 하지만 이후 정상적 동작을 보장할 수 없습니다.

pip 설치가 완료되었는지 확인하려면 아래 명령어를 입력해보면 됩니다.
(이번 게시글에서는 python3-pip로 진행합니다. Python2의 pip를 이용하시려면 `python3-pip`대신 `python-pip`를 설치하셔서 `pip`명령어를 사용하세요.)

```sh
# Python2 pip의 경우
$ pip -V
# Python3 pip의 경우
$ pip3 -V
```

![](https://www.dropbox.com/s/gce8siz6uo6nres/%EC%8A%A4%ED%81%AC%EB%A6%B0%EC%83%B7%202016-12-30%2018.57.52.png?dl=1)

이제 pip설치가 완료되었으므로 Virtualenv와 VirtualenvWrapper를 설치해보겠습니다.

```sh
# Python2의 경우
$ pip install virtualenv virtualenvwrapper

# Python3의 경우
$ pip3 install virtualenv virtualenvwrapper
```

만약 `pip`/`pip3` 명령이 먹지 않는다면 아래 명령어로 대체할 수 있습니다.
(시스템에 root권한으로 pip를 설치한 경우 sudo권한이 필요할 수 있는데, 이때는 `sudo pip install`으로 명령어 앞에 sudo를 붙여줍시다.)

```sh
# Python2 pip의 경우
$ python -m pip install virtualenv virtualenvwrapper

# Python3 pip의 경우
$ python3 -m pip install virtualenv virtualenvwrapper
```

지금까지 사용한 `pip`와 `pip3`은 virtualenv를 어느 pip에 설치할까에 대한 내용일 뿐, 파이썬 가상환경에 어떤 Python이 설치될지와는 무관합니다.

## Virtualenv의 기본적 명령어 [LINUX(UBUNTU)]

Virtualenv는 기본적으로 아래의 명령어로 동작합니다.

![](https://www.dropbox.com/s/9oewqawn9mrvek8/%EC%8A%A4%ED%81%AC%EB%A6%B0%EC%83%B7%202016-12-30%2019.29.18.png?dl=1)

```sh
$ virtualenv --python=파이썬버전 가상환경이름
# ex)
# $ virtualenv --python=python3.5 py3_env
# $ virtualenv --python=python2.7 test_env2
```

> 만약 virtualenv 라는 명령이 먹히지 않는다면 `python3 -m virtualenv`(python2는 `python -m virtualenv`)명령어를 이용하거나, 쉘을 껐다가 다시 켜주세요.

> 만약

> ![](https://www.dropbox.com/s/l0wwqtuoch9tw8r/%EC%8A%A4%ED%81%AC%EB%A6%B0%EC%83%B7%202016-12-30%2019.18.33.png?dl=1)

> 와 같이 The path x.x does not exist라는 에러가 난다면 PYTHON의 PATH을 절대경로로 맞춰줘야 합니다. `which python3`을 했을 때 `/usr/bin/python3`이 나왔다면, `virtualenv --python=/usr/bin/python3`와 같이 절대경로로 입력해주시면 됩니다.

> ![](https://www.dropbox.com/s/bnb3r5fephimoig/%EC%8A%A4%ED%81%AC%EB%A6%B0%EC%83%B7%202016-12-30%2019.23.40.png?dl=1)

이와 같이 Python버전을 명시해주고 가상환경을 만들 수 있습니다. (단, 선택할 Python은 시스템에 깔려있는 버전이어야 합니다. Ubuntu16의 경우 python2이 깔려있지 않을 수 있습니다.)

만든 가상환경에 진입(가상환경을 활성화)하려면 아래 명령어를 이용하면 됩니다.

```sh
$ source 가상환경이름/bin/activate
```

Python3이 설치된 py3_env로 진입한 경우

![](https://www.dropbox.com/s/tlrjm1ikl4kkj0q/%EC%8A%A4%ED%81%AC%EB%A6%B0%EC%83%B7%202016-12-30%2019.32.26.png?dl=1)

이후 pip를 통해 외부 모듈과 라이브러리들을 설치하는 경우, source 명령어로 가상환경에 진입하지 않으면 라이브러리들을 불러쓸 수 없게됩니다. 즉, 프로젝트 별로 다른 라이브러리만이 설치된 환경을 구성한 것이죠.

## VirtualenvWrapper 설정하기 [LINUX(UBUNTU)]

VirtualEnv를 사용하기 위해서는 `source`를 이용해 가상환경에 진입합니다. 그러나, 이 진입 방법은 가상환경이 설치된 위치로 이동해야되는 것 뿐 아니라 가상환경이 어느 폴더에 있는지 일일이 사용자가 기억해야 하는 단점이 있습니다. 이를 보완하기 위해 `VirtualenvWrapper`를 사용합니다.

또한, VirtualenvWrapper를 사용할 경우 터미널이 현재 위치한 경로와 관계없이 가상환경을 활성화할 수 있다는 장점이 있습니다.

VirtualenvWrapper는 `.bashrc`나 `.zshrc`에 약간의 설정과정을 거쳐야 합니다.

우선 홈 디렉토리로 이동해보세요.

```sh
$ cd ~
```

가상환경이 들어갈 폴더 `.virtualenvs`를 만들어주세요.

```sh
$ mkdir ~/.virtualenvs
```

그리고 홈 디렉토리의 `.bashrc`나 `.zshrc`의 파일 제일 마지막에 아래 코드를 복사해 붙여넣어줍시다.
(파일이 없다면 만들어 사용하시면 됩니다.)

```sh
# python virtualenv settings
export WORKON_HOME=~/.virtualenvs
export VIRTUALENVWRAPPER_PYTHON='$(command \which python3)'  # Usage of python3
source /usr/local/bin/virtualenvwrapper.sh
```

저장하고 나온 후 터미널을 종료후 새로 켜주면, VirtualenvWrapper의 명령어들을 사용할 수 있습니다.

만약 `/usr/local/bin/virtualenvwrapper.sh`파일이 존재하지 않는다면 다음 명령어로 `virtualenvwrapper.sh`파일을 찾아서 위 코드를 바꿔 사용하세요.

```sh
find /usr -name virtualenvwrapper.sh
```

## VirtualenvWrapper 명령어들 [LINUX(UBUNTU)]

VirtualenvWrapper의 명령어는 여러가지가 존재하지만, 이 포스팅에서는 기본적인 것만 다루고 넘어갑니다.

- 가상환경 만들기

```sh
$ mkvirtualenv 가상환경이름
# 예시
# $ mkvirtualenv test_env3
```

`mkvirtualenv` 명령어를 사용할 경우 홈 디렉토리의 `.virtualenvs`폴더 안에 `가상환경이름`을 가진 폴더(`test_env3`)가 생깁니다.

- 가상환경 지우기

```sh
$ rmvirtualenv 가상환경이름
# 예시
# $ rmvirtualenv test_env3
```

`rmvirtualenv` 명령어를 사용할 경우 `mkvirtualenv`로 만든 가상환경을 지워줍니다.

만든 가상환경을 지우는 방법은 이방법 뿐 아니라 홈 디렉토리의 `.virtualenvs`폴더 안의 가상환경이름을 가진 폴더를 지우는 방법도 있습니다.

- 가상환경 진입하기 + 가상환경 목록 보기

```sh
$ workon 가상환경이름
# 가상환경으로 진입시 앞에 (가상환경이름)이 붙습니다.
(가상환경이름) $
# 예시
# $ workon test_env3
# (test_env3) $
```

`workon`명령어를 통해 `mkvirtualenv`로 만든 가상환경으로 진입할 수 있습니다.

`workon`명령어를 가상환경이름 없이 단순하게 칠 경우, 현재 만들어져있는 가상환경의 전체 목록을 불러옵니다.

```sh
$ workon
test_env3
```

- 가상환경 빠져나오기

```sh
(가상환경이름) $ deactivate
$
# 예시
# (test_env3) $ deactivate
# $
```

가상환경에서 빠져나오는 것은 다른것들과 동일하게 `deactivate`명령어로 빠져나올 수 있습니다.

<span id="windows"></span>

# Windows의 경우
