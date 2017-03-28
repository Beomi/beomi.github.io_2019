---
title: "편리한 깃헙페이지 블로깅을 위한 이미지서버, 구글드라이브: 업로드 ShellScript편"
date: 2017-03-27 15:45:00 +0900
layout: post
categories:
- Tips
- GithubPages
published: true
image: /img/Tips/google-drive-logo.jpg
---

> 본 가이드는 MacOS에서 이용가능합니다.

## 들어가며

깃헙 페이지를 Jekyll등을 이용해 Markdown파일을 이용하다보면 스크린샷을 저장하고 깃헙 레포 폴더에 옮긴 후 수동으로 url을 추가해 주는 작업이 상당히 귀찮고, 심지어 깃헙 레포당 저장공간은 1G로 제한됩니다. 

Dropbox의 경우에는 MacOS 내장 스크린샷(CMD+Shift+4)를 이용할 경우 파일을 자동으로 dropbox에 올린 후 공유 url이 나옵니다. 하지만 일반 유저는 용량 제한도 있고, 트래픽 제한도 있습니다.

따라서 무료로 15G의 용량과 명시적 트래픽 제한이 없는 구글드라이브를 이용하는 방안을 고려해보았습니다.

> 정확히는 Github은 레포당 용량을 명시적으로 제한하지는 않지만 1G가 넘어가는 경우 스토리지를 이용하도록 가이드합니다. Dropbox링크를 통한 트래픽은 무료 유저의 경우 일 20G, 유료플랜 유저의 경우 일 200G를 줍니다. GoogleDrive의 경우 무료 계정도 일 100G(추정치)의 트래픽을 제공하기 때문에 큰 무리는 따르지 않는다 생각합니다.

## Gdrive 설치하기

이번 가이드에서는 [Gdrive](https://github.com/prasmussen/gdrive)를 이용합니다.

[Homebrew](https://brew.sh/)를 통해 간단히 설치할 수 있습니다. 터미널에서 아래와 같이 입력해 주세요.

```sh
brew install gdrive
```

## Gdrive AUTH

gdrive를 설치하고 나서, gdrive가 구글드라이브에 액세스 할 수 있도록 권한을 부여해야 합니다. 

아래 명령어는 구글드라이브의 최상위 디렉토리를 리스팅 하는 명령어인데, 이 과정에서 드라이브 액세스 권한을 요구하기 때문에 자연스럽게 권한 등록이 가능합니다.

```sh
gdrive list
```

명령어를 입력시 아래와 같은 창이 뜹니다. 절대 창을 끄지 마시고 아래 안내되는 구글 링크로 들어가세요.

> 보안을 위해 키 일부를 지웠습니다. 원래는 회색 빈칸이 없습니다 :)

![Console: GoogleDrive auth link](https://www.dropbox.com/s/60qcsi8agd3zqjl/%EC%8A%A4%ED%81%AC%EB%A6%B0%EC%83%B7%202017-03-27%2016.02.26.png?dl=1)

링크를 따라가시면 구글 로그인을 요구합니다. 로그인을 하시면 아래와 같은 권한 요구 창이 뜨는데요, '허용'을 눌러주시면 됩니다.

![](https://www.dropbox.com/s/miin81iiovnj4cs/%EC%8A%A4%ED%81%AC%EB%A6%B0%EC%83%B7%202017-03-27%2016.03.21.png?dl=1)

허용을 누르면 아래와 같은 코드가 나옵니다. 이 코드를 아까 터미널 창에 복사-붙여넣기를 해주세요.

![](https://www.dropbox.com/s/5n8nmdgvgoj7gim/%EC%8A%A4%ED%81%AC%EB%A6%B0%EC%83%B7%202017-03-27%2016.04.52.png?dl=1)

만약 코드가 정상적이었다면 아래와 같이 최상위 디렉토리의 폴더/파일 리스트가 나타납니다.

![](https://www.dropbox.com/s/jbjehz3cc23ns5c/%EC%8A%A4%ED%81%AC%EB%A6%B0%EC%83%B7%202017-03-27%2016.08.40.png?dl=1)

## capture.sh파일 만들기

Gdrive가 정상적으로 구글 계정과 연결되었다면, 이제 `capture.sh`파일을 만들어야 합니다. 파일의 코드는 아래와 같습니다. 복사 하신 후 원하시는 위치에 넣어주세요. (저는 `~/capture.sh`로 두었습니다.)

```sh
#!/bin/bash
# ~/capture.sh
screencapture -tpng -i /tmp/temp_shot_gdrive.png
DATEFILENAME=`date +"%Y%m%d%H%M"`
# use -p id to upload to a specific folder
ID=`gdrive upload /tmp/temp_shot_gdrive.png --name screenshot${DATEFILENAME}.png --share | egrep "^Uploaded" | awk '{print $2}'`
URL="https://drive.google.com/uc?id=${ID}"

echo ${URL} | pbcopy
```

우선 이 스크립트 파일에 실행권한을 줘야 합니다.

```sh
chmod +x capture.sh
```

이제 `./capture.sh`명령을 입력하면 캡쳐메뉴로 진입하고, 캡쳐를 진행하고 잠시 기다리면(업로드 시간) 클립보드에 구글드라이브로 공유된 파일의 URL이 복사됩니다.

## rc파일(.zshrc/.bashrc)에 alias걸기

`capture.sh`파일을 둔 위치가 `~/capture.sh`라고 가정하고, `~/.zshrc`(혹은`~/.bashrc`) 파일을 수정해 주겠습니다.

항상 `./capture.sh`라고 입력하는 것은 귀찮은 일이기 때문에, alias를 통해 `cap`라는 명령어를 캡쳐 명령어로 지정해 봅시다.

`.zshrc`나 `.bashrc`파일 제일 아래에 아래 코드를 덧붙여주고 저장해줍시다.

```sh
alias cap="~/capture.sh"
```

터미널을 재실행한 후 `cap`라는 명령을 치면 캡쳐 도구가 뜹니다!

## 다음 가이드: 앱으로 만들어 단축키로 연결하기

기본 스크린샷처럼 키보드 단축키 만으로 스크린샷 링크를 가져올 수 있다면 훨씬 편리하겠죠?

다음 가이드에서는 이번에 만든걸 앱으로 만들어 스크린샷 단축키로 연결하는 과정을 다룹니다.

다음가이드: [편리한 깃헙페이지 블로깅을 위한 이미지서버, 구글드라이브: 앱으로 만들고 키보드 단축키 연결하기](/2017/03/28/Make-Capture-to-GDrive-App/)

> 완성된 앱도 함께 제공합니다!
