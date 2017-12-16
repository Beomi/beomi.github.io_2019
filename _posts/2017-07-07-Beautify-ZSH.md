---
title: "멋진 Terminal 만들기"
date: 2017-07-07
layout: post
categories:
- macOS
published: true
image: /img/Beautify-ZSH.png
---

> 이번 가이드는 macOS를 위한 가이드입니다.

맥을 개발용으로 사용하는 경우 터미널을 좀 더 편리하고 다양하게 사용하는 방법 중 기본 Shell인 `bash`대신 `zsh`을 사용하는 경우가 많습니다. 그리고 `oh-my-zsh`을 함께 사용해 더 많은 기능을 편리하게 깔수 있기도 합니다. 물론 `oh-my-zsh`의 기본 테마인 `robbyrussell`도 예쁘지만, 약간 아쉬운 점이 남기도 하죠. 좀 더 예쁘고 사용하고싶어지는 기분이 들도록 `agnoster`테마를 깔고 `Oceanic Next`색 테마를 입힌 후 터미널에서 사용하는 명령어가 제대로 쳤는지 확인해주는 `zsh-syntax-highlighting`를 깔아봅시다. 참, 터미널은 `iTerm2`라는 멋진 맥용 터미널을 먼저 깔아야 해요.

> 앞으로 나오는 가이드는 이미 깐 경우 Pass해주시면 됩니다.

## [iTerm2](https://www.iterm2.com/downloads.html) 설치하기

<div style="text-align: center;">
<img src="/img/iTerm2_logo.jpg" style="display:inline-block;max-height: 250px">
</div>

우선 [iTerm2 다운로드 페이지](https://www.iterm2.com/downloads.html)에 들어가서 iTerm2를 받아주세요.

![iTerm2 Download Page]({{site.static_url}}/img/iTerm2_download.png)

Stable Releases중 최신 버전을 받아주세요. 다운 받은 후 압축을 풀면 iTerm2라는 맥 앱이 생길거에요. 맥 파인더에서 '응용 프로그램'으로 iTerm2를 옮겨주세요.

## [HomeBrew](https://brew.sh/) 설치하기

<div style="text-align: center;">
<img src="/img/homebrew_logo.png" style="display:inline-block;max-height: 250px">
</div>

우분투의 APT와 비슷하게 프로그램 패키지를 관리해 주는 프로그램이 있습니다. 바로 `HomeBrew`라는 프로그램인데요, `brew`라는 명령어로 패키지를 관리할 수 있습니다.

> HomeBrew 공식 홈페이지는 [https://brew.sh/](https://brew.sh/)입니다.

아래 명령어를 터미널에 입력해주세요.

```bash
/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
```

## Zsh 설치하기

<div style="text-align: center;">
<img src="/img/zsh.jpg" style="display:inline-block;max-height: 250px">
</div>

`zsh`은 `bash`에 추가적인 명령어를 추가하고 편의성을 개선한 새로운 쉘입니다. 한가지 예로 `git` 폴더 상태를 관리해주고 터미널에 상태를 나타내주는 점 등이 있습니다.

zsh은 위에서 설치한 `brew`를 통해 설치할 수 있습니다. 아래 명령어를 터미널에 입력해 주세요.

```bash
brew install zsh
```

## OhMyZsh 설치하기

<div style="text-align: center;">
<img src="/img/ohmyzsh_logo.png" style="display:inline-block;max-height: 250px">
</div>

`oh-my-zsh`은 `zsh`을 좀 더 편리하게 이용하게 이용해주는 일종의 `zsh` 플러그인입니다. `oh-my-zsh`은 아래 명령어를 통해 설치할 수 있습니다. 터미널에 아래 명령어를 입력해주세요.

> OhMyZsh을 설치하면 기본 쉘을 `zsh`로 바꾸기 위해 맥 잠금해제 암호를 물어봅니다. 암호 입력시에는 입력해도 `*`같은 표시는 뜨지 않으니 그냥 입력하고 엔터를 눌러주세요!

```bash
sh -c "$(curl -fsSL https://raw.github.com/robbyrussell/oh-my-zsh/master/tools/install.sh)"
```

## [Oceanic Next iTerm](https://github.com/mhartington/oceanic-next-iterm) 색 테마 입히기

<div style="text-align: center;">
<img src="/img/oceanic_next_color_scheme.png" style="display:inline-block;max-height: 250px">
</div>

`oceanic-next-iterm`을 이용해 터미널의 색 테마를 바꿔봅시다. 우선 [master.zip](https://github.com/mhartington/oceanic-next-iterm/archive/master.zip) 파일을 받아줍시다.

`master.zip`파일의 압축을 풀어주면 `Oceanic-Next.itermcolors`파일을 보실 수 있으실텐데요, 이 파일을 더블클릭으로 실행하면 iTerm2의 색 테마에 추가가 됩니다.

<div style="text-align: center;">
<img src="/img/Oceanic-Next.itermcolors.png" style="display:inline-block;max-height: 250px">
</div>

iTerm2를 실행하고 맥 화면 상단 좌측의 사과 아이콘 옆 iTerm2를 누르고 나오는 메뉴 중 'Preferences...'를 눌러주세요.

![]({{site.static_url}}/img/Oceanic-Next.itermcolors2.png)

이제 위 스크린샷처럼 Profiles > Default > Colors > Color Presets... > Oceanic-Next 로 차례대로 눌러주신 후 iTerm2를 껐다가 켜면 적용이 완료되어있을 거랍니다.

## Agnoster 테마 설치하기

<div style="text-align: center;">
<img src="/img/agnoster.png" style="display:inline-block;max-height: 250px">
</div>

이제 우리 zsh의 테마를 위 스크린샷처럼 `Agnoster`테마로 바꿔줍시다!

텍스트 편집기(vi, sublimetext3, atom등)로 `~/.zshrc`파일을 열어주세요.

만약 `.zshrc`파일에 특별한 수정을 하지 않았다면 10번째줄 처럼 `ZSH_THEME`를 설정하는 코드가 보일거에요. 이 줄을 아래 스크린 샷처럼 바꿔주세요.

```bash
ZSH_THEME="agnoster"
```

<div style="text-align: center;">
<img src="/img/agnoster.zshrc.png" style="display:inline-block;max-height: 250px">
</div>

이제 새 탭을 열면 Agnoster테마로 바뀐 쉘이 보일거에요! 하지만 이렇게 하면 폰트가 일부 깨진답니다. 아래 Ubuntu Mono Powerline폰트를 받아 설정을 진행해주세요.

## Ubuntu Mono derivative Powerline 폰트 설치 & 설정하기

<div style="text-align: center;">
<img src="/img/Ubuntu_Mono_derivative_Powerline.png" style="display:inline-block;max-height: 250px">
</div>


우선 [Ubuntu_Mono_derivative_Powerline.ttf](/others/Ubuntu_Mono_derivative_Powerline.ttf)를 다운받아 서체 설치를 진행해 주세요.

서체 설치가 완료되면 iTerm2를 다시 실행해 주세요.

> 주의: 서체 설치 전 iTerm2이 켜져있었다면 완전히 종료 후 다시 켜 주세요. 켜져있는 상태에서 설정에 들어간다면 설치한 폰트가 뜨지 않을 수 있습니다!

<div style="text-align: center;">
<img src="/img/Oceanic-Next.itermcolors.png" style="display:inline-block;max-height: 250px">
</div>

위에서 Oceanic Next 테마를 설치한 것과 같이 위 스크린샷처럼 Preferences..에 들어가 주세요.

![]({{site.static_url}}/img/iTerm2_Ubuntu_Mono1.png)

그리고 위 사진처럼 Profiles > Default > Text > ChangeFont를 눌러주세요. 그러면 아래와 같은 창이 뜹니다. 시스템에 깔린 모든 폰트가 나오기 때문에 '고정폭'을 먼저 선택하고 폰트를 선택해 주세요.

<div style="text-align: center;">
<img src="/img/iTerm2_Ubuntu_Mono2.png" style="display:inline-block;max-height: 250px">
</div>

## zsh-syntax-highlighting 설치하기

<div style="text-align: center;">
<img src="/img/zsh-syntax-highlighting.png" style="display:inline-block;max-height: 250px">
</div>

이제 시스템의 `PATH`에 등록된 명령어들을 자동으로 Syntax HighLighting을 해주는 `zsh-syntax-highlighting`를 설치해 봅시다.

아래 명령어 두줄을 터미널에 입력해 주세요.

```bash
git clone https://github.com/zsh-users/zsh-syntax-highlighting.git
echo "source ${(q-)PWD}/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh" >> ${ZDOTDIR:-$HOME}/.zshrc
```

## 수고하셨습니다 :D

이제 모두 끝났습니다!! iTerm2를 완전히 종료한 후 다시 실행해 보면 잘 작동되는 것을 보실 수 있으실거에요!
