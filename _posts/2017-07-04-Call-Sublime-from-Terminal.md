---
title: "서브라임텍스트 터미널에서 실행하기(macOS)"
date: 2017-07-04
layout: post
categories:
- macOS
published: true
image: /img/sublimetext.jpg
---

> 이번 가이드는 macOS 용입니다.

## 들어가기 전

### 프로그램의 설치 경로

macOS에 프로그램을 설치하면 기본적으로 `/Users/유저이름/Library`(`~/Library`와 같음)에 위치합니다. 사용자의 Library에 저장되는 이 경로는 root 권한 없이도 응용프로그램을 추가하거나 제거하는 것이 가능합니다.

### 터미널에서 실행되는 경로, `PATH`

대부분의 운영체제에서는 `PATH`가 있습니다. 그리고 이 `PATH`에 등록된 경로는 시스템 전역에서 호출 가능한 위치가 됩니다. 예를들어 `PATH`에 등록된 경로 중 `/usr/local/bin`폴더가 있었다면 아래와 같이 `python`명령어를 실행할 경우 `/usr/local/bin/python`에 있는 파이썬이 실행됩니다.

```sh
➜ ~ which python
/usr/local/bin/python
```

그리고 기본적으로 `/usr/local/bin`폴더는 사용자 터미널의 PATH에 등록되어있습니다. 따라서 SublimeText3(혹은 2) 실행 프로그램을 `ln -s`명령어를 통해 `/usr/local/bin`폴더에 심볼릭 링크를 걸어줘야 합니다.

> 심볼릭 링크란? 파일을 이동하지 않고 어떤 위치에 바로가기를 하나 더 만드는 것입니다. 윈도우의 바로가기 아이콘과 비슷하다고 생각하시면 됩니다.

## SublimeText가 깔렸는지 확인하기

최신 버전의 sublimetext는 3버전입니다. 하지만 2버전도 유사한 방식으로 사용할 수 있습니다.

우선 아래 명령어를 터미널에 입력할 경우 실행이 되는지 확인해보세요.

> 코드를 그대로 복사해서 사용하세요!

```sh
# SublimeText3 의 경우
open /Applications/Sublime\ Text.app/Contents/SharedSupport/bin/subl
# SublimeText2 의 경우
open /Applications/Sublime\ Text\ 2.app/Contents/SharedSupport/bin/subl
```

위 명령어를 쳐서 서브라임 텍스트 창이 뜬 경우 아래 가이드를 따라가 주시면 됩니다.

## 심볼릭 링크 등록하기

우리는 `subl`이라는 명령어로 서브라임 텍스트 프로그램을 실행할 계획입니다.

터미널에 아래와 같은 명령어를 입력해 주세요.

SublimeText3인 경우:

```sh
ln -s "/Applications/Sublime\ Text.app/Contents/SharedSupport/bin/subl" /usr/local/bin/subl
```

SublimeText2인 경우:

```sh
ln -s "/Applications/Sublime\ Text\ 2.app/Contents/SharedSupport/bin/subl" /usr/local/bin/subl
```

## 모두 끝났습니다!

이제 터미널에서 `subl`이라는 명령어를 통해 서브라임 텍스트를 실행할 수 있습니다 :)

그냥 서브라임텍스트를 실행하려면

```sh
subl
```

현 폴더를 열려면

```sh
subl .
```

이와 같이 `subl`뒤에 파일/폴더등을 인자로 전달해 줄 수 있습니다.

> 만약 위 방식으로 되지 않으신다면 `.zshrc`이나 `.bashrc`등의 파일에 아래와 같이 입력해 주세요.

```bash
alias subl="/Applications/Sublime\ Text.app/Contents/SharedSupport/bin/subl"
```

