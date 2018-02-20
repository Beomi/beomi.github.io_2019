---
title: "편리한 깃헙페이지 블로깅을 위한 이미지서버, 구글드라이브: 앱으로 만들고 키보드 단축키 연결하기"
date: 2017-03-28
layout: post
categories:
- tips
- githubpages
published: true
image: https://d1sr4ybm5bj1wl.cloudfront.net/img/Tips/app_store.jpg
---

> 본 가이드는 MacOS에서 이용가능합니다.

이전 가이드: [편리한 깃헙페이지 블로깅을 위한 이미지서버, 구글드라이브: 업로드 ShellScript편](/2017/03/27/Use-GoogleDrive-as-Image-Server/)

> 터미널에서 `gdrive list`라고 했을때 에러가 나지 않는 상태에서 아래 가이드를 진행해주세요.

## 들어가며

이전 가이드에서 스크린샷을 찍고 구글드라이브에 올린 후 이미지의 공유 URL을 가져오는 스크립트를 작성했습니다.

하지만 키보드 Shortcuts를 이용한 편리성에는 따라가기가 어렵죠. `.sh`스크립트를 키보드로 연동하는 방법 중 여러가지 방법이 있지만, 이번에는 `MacOS App`으로 만든 후 앱을 실행하는 것을 `서비스`에 등록하고 `Automator`를 통해 키보드와 앱실행 서비스를 연동하는 과정을 다룹니다.

> 만약 잘 동작하는 맥용 앱을 바로 다운받으시려면 [CaptureToGdrive.zip](/others/CaptureToGdrive.zip)을 받아주신 후 압축을 푸신 후 앱을 Application폴더로 옮기신 후 [[백투더맥 Q&A] 키보드 단축키로 응용 프로그램을 실행하는 바로 가기 만들기](http://macnews.tistory.com/4277) 과정을 따라가시면 됩니다.

## SH파일을 앱으로 만들기

우선 `.sh`파일로 된 스크립트를 맥용 앱으로 Wrapping해주는 작업이 필요합니다. 이번 가이드에서는 이 작업을 간소화해주는 [platypus](http://sveinbjorn.org/platypus)를 이용합니다.

platypus는 [platypus.zip](http://sveinbjorn.org/files/software/platypus.zip)을 받고 압축을 풀어 사용하시면 됩니다.

앱을 실행하면 아래와 같은 화면이 뜹니다.

![](https://drive.google.com/uc?id=0B91qXw6kE4VfWWV2RWpnX056X2s)

App Name을 `CaptureToGdrive`로, Script Type을 `bash`로, Script Path는 아래의 `+New`를 눌러 아래와 같이 코드를 입력해 줍시다.

```sh
#!/bin/bash

screencapture -tpng -i /tmp/temp_shot_gdrive.png
DATEFILENAME=`date +"%Y%m%d%H%M"`
ID=`/usr/local/bin/gdrive upload /tmp/temp_shot_gdrive.png --name screenshot${DATEFILENAME}.png --share | egrep "^Uploaded" | awk '{print $2}'`
URL="https://drive.google.com/uc?id=${ID}"

echo ${URL} | pbcopy
```

위 코드는 이전 가이드에서 다뤘던 것과 약간 다른데요, `gdrive`명령어의 위치를 명확히 `/usr/local/bin/gdrive`로 바꿔준점이 다릅니다. 쉘 스크립트를 사용할 때 명확히 하지 않으면 gdrive의 PATH를 잡지 못해 에러가 나기 때문입니다.

> 만약 다른 위치에 까셨다면 `which gdrive`명령을 통해 그 위치로 변경해주시면 됩니다.

![](https://drive.google.com/uc?id=0B91qXw6kE4VfRElUbERjYjhmSnM)

스크립트를 입력하고 나면 AppName이 초기화되는 사소한 문제가 있으니 다시 AppName을 등록해 줍시다.

스크린샷 촬영은 인터페이스가 필요없기 때문에 `Interface`는 `None`으로, root권한이 필요없고 백그라운드일 필요도 없고 프로그램이 굳이 계속 떠 있을 필요가 없기때문에 모든 체크박스는 아래와 같이 체크해제 해두시면 됩니다.

![]({{site.static_url}}/img/dropbox/2017-03-28%2015.07.29.png)

이제 CreateApp을 클릭하고 아래와 같이 클릭한 후 Create를 누르면 앱이 만들어집니다 :)

![]({{site.static_url}}/img/dropbox/2017-03-28%2015.15.22.png)

만들어진 앱을 실행해 보시고 잘 되시는지 확인해보세요.

## 앱을 키보드로 연결하기

이 부분은 좀 더 잘 정리되어있는 [[백투더맥 Q&A] 키보드 단축키로 응용 프로그램을 실행하는 바로 가기 만들기](http://macnews.tistory.com/4277)을 참고하시기 바랍니다.

## 마치며

이번 가이드에서는 업로드 되는 폴더를 정확히 명시하지는 않았습니다. `gdrive`패키지에서 `-p`를 이용하면 폴더를 지정가능하다고 하지만 테스트 결과 제대로 업로드 되지 않는 것을 확인했기 때문에, 현재 주로 사용하지는 않는 다른 구글 아이디에 gdrive를 연결해 두었습니다.

Imgur, Dropbox등 여러 이미지 Serving 업체들이 있지만, 구글이 가진 구글 Fiber망과 서비스의 안정성은 여타 서비스들이 따라가기 어려운 점이라고 생각합니다 :)


