---
title: '[React Native 번역]#01: 시작하기'
date: 2016-11-15 16:00:00+09:00
layout: post
categories:
- Translation
image: /img/old_post/react-native.png
---

React Native의 ​Tutorial번역 시리즈입니다.
[원문: getting-started](http://facebook.github.io/react-native/releases/0.37/docs/getting-started.html)
이번 번역은 현재(2016.11.15) 최신 Stable인 0.37버전의 문서를 번역하였습니다.

# \#01: 시작하기

React Native에 오신 것을 환영합니다!
이번 게시글에서는 React Native를 여러분의 시스템에 설치하고 곧바로 실행 할 수 있도록 안내합니다.
만약 여러분이 이미 React Native를 설치해두셨다면, 이번 게시글을 건너뛰고 [튜토리얼]()로 가셔도 됩니다.

이번 게시글은 여러분이 어떤 시스템을 사용하는지에 따라 약간 내용이 다르고, iOS/Android중 어떤 것을 사용하느냐에 따라서도 내용이 다르답니다.
iOS와 Android 모두 개발하는 것도 당연히 가능합니다! 여기서는 그냥 시작을 어떤 환경으로 할지 정하는 것 뿐입니다.

```
주의: iOS개발은 Xcode가 깔려있는 macOS(OS X)환경에서만 가능합니다.
```

## 필요한 의존패키지들 설치하기(macOS/OS X에서)

> 윈도우에서 의존 패키지를 설치하는 것은 문서 아래쪽의 [윈도 의존 패키지 설치하기]()를 참고해주세요.

React Native를 개발하기 위해서
여러분은 node.js와 Watchman, React Native command line interface와 Xcode가 필요합니다.

### Node, Watchman, react-native-cli 설치하기 (iOS, Android 공통)

node와 Watchman을 [Homebrew](http://brew.sh/)를 통해 설치하는 것을 권장합니다.
터미널에서 아래와 같이 입력해 설치할 수 있답니다.

```
brew install node
brew install watchman
```

> [Watchman](https://facebook.github.io/watchman)은 facebook에서 파일 시스템의 변화를 감시하는 용도로 사용하는 툴입니다.
더 나은 퍼포먼스를 위해 사용을 강력히 추천합니다!

위에서 node와 함께 npm이 자동적으로 설치되었을거랍니다. 아래 명령어로 react-native-cli를 설치해주세요!

```
npm install -g react-native-cli
```

> (번역주)-g 옵션은 시스템 전체에서 사용할 수 있도록 시스템 영역에 설치한다는 뜻입니다.

> 만약, 권한 문제로 설치에 실패하신다면 `sudo npm install -g react-native-cli`로 설치해보세요!

> 만약 `Cannot find module 'npmlog'`같은 에러를 만나셨다면, npm을 다음 명령어로 수동 설치해보세요.: `curl -0 -L http://npmjs.org/install.sh | sudo sh`.

### Xcode 설치하기 (iOS개발환경)

Xcode를 설치하는 가장 쉬운 방법은 [Mac App Store](https://itunes.apple.com/us/app/xcode/id497799835?mt=12)에서 받는 방법입니다. 앱스토어에서 Xcode를 설치하면 iOS시뮬레이터와 iOS App빌드를 위한 여러 툴들이 자동으로 함께 설치됩니다.

### Android Studio 설치하기 (안드로이드 개발환경)

만약 여러분이 안드로이드를 개발하는 것이 처음이라면, 개발환경을 갖추는 것은 약간 까다로울 수 있습니다.
이미 안드로이드 개발을 하고있던 환경이라면, 설정을 거의 건드리지 않아도 React Native로 개발을 시작하실 수 있습니다.
둘 중 어떻든, 아래 과정을 확인해보세요.

#### 1. Android Studio 받고 설치하기.

[Android Studio](https://developer.android.com/studio/install.html)는 여러분의 React Native앱을 실행시킬 Android SDK와 AVD(안드로이드 VM)를 제공해줍니다.

> Android Studio는 [Java Development Kit (JDK)](https://www.java.com/en/download/mac_download.jsp) version 1.8 이상을 필요로 합니다. 터미널에서 `javac -version` 명령어로 몇 버전의 JDK가 깔려있는지 확인해보세요!

#### 2. AVD, HAXM 설치하기

Android Studio 설치를 시작할 때 `custom`옵션으로 설치를 진행해 주세요.
다음 문항들이 다 체크되어있는지 꼭 확인해보세요:
- `Android SDK`
- `Android SDK Platform`
- `Performance (Intel ® HAXM)`
- `Android Virtual Device`

다 체크되어있다면, "Next"를 눌러 설치를 진행해 주세요.

> (역자주) HAXM이 없어도 여전히 사용은 가능합니다. 그러나 안드로이드 가상머신의 성능이 저하될 수 있고, 이 옵션은 사용하시는 시스템에 따라 사용가능 유무가 달라지므로 크게 신경쓰지 않으셔도 됩니다.

> 만약 Android Studio를 이미 설치하셨더라도, Android Studio 재설치 없이 [HAXM 설치](https://software.intel.com/en-us/android/articles/installation-instructions-for-intel-hardware-accelerated-execution-manager-windows)를 하실 수 있습니다.

#### 3. Android 6.0 (마시멜로) SDK 설치하기

안드로이드 스튜디오에서는 기본적으로 최신 버전의 Android SDK를 설치해줍니다. 하지만 React Native(0.37)에서는 안드로이드6.0(마시멜로) SDK`(역자주)정확히는 v23.1`를 사용합니다. 이 SDK는 "Welcome to Android Studio" 화면에서 SDK Manager를 실행하고, Configure탭에서 설치하실 수 있습니다.

> 또다른 방법으로는, 안드로이드 스튜디오의 "Preferences" 메뉴 아래 **Appearance & Behavior** → **System Settings** → **Android SDK** 으로 들어갈 수 있습니다.

![](http://facebook.github.io/react-native/releases/0.37/img/react-native-android-studio-configure-sdk.png)

SDK Manager에서 "SDK Platforms"을 누른 후, "Show Package Details"를 눌러보세요. `Android 6.0 (Marshmallow)`를 찾으신 후, 아래 목록들이 모두 체크되어있는지 확인해 보세요:

- `Google APIs`
- `Intel x86 Atom System Image`
- `Intel x86 Atom_64 System Image`
- `Google APIs Intel x86 Atom_64 System Image`

![](http://facebook.github.io/react-native/releases/0.37/img/react-native-sdk-platforms.png)

위 그림에서는 7.0만 설치되어있는걸 보실 수 있습니다. 6.0을 체크해주세요!

다 체크되어있다면, "SDK Tools"탭을 눌러보세요. "Android SDK Build Tools"를 펼쳐보시고, `Android SDK Build-Tools 23.0.1`가 깔려 있는지(체크되어있는지) 확인해 보세요.

마지막으로, Apply버튼을 눌러 SDK와 빌드 도구를 설치해주세요.

#### 4. ANDROID_HOME 환경변수 설정하기

React Native command-line interface는 `ANDROID_HOME` 환경변수를 필요로 합니다.

아래 코드들을 `~/.bashrc` (혹은 이와 같은 것들)의 마지막에 넣어주세요.

```
export ANDROID_HOME=~/Library/Android/sdk
export PATH=${PATH}:${ANDROID_HOME}/tools
export PATH=${PATH}:${ANDROID_HOME}/platform-tools
```

> `ANDROID_HOME`이 저 위치가 맞는지 꼭! 확인해주세요. 만약, Homebrew를 통해서 Android SDK를 설치하셨다면 아마도 `/usr/local/opt/android-sdk`가 ANDROID_HOME이 될겁니다.

등록한 환경변수는 터미널을 재실행 한 이후에 적용됩니다.

#### 5. 안드로이드 가상 머신 시작하기

![Android Studio AVD Manager](http://facebook.github.io/react-native/releases/0.37/img/react-native-tools-avd.png)

안드로이드 스튜디오에서 "AVD Manager"를 열어보면 지금 시스템에 깔려있는 이용가능한 안드로이드 VM의 목록이 나타납니다.
아래 명령어를 터미널에서 입력해도 볼 수 있어요.

```
android avd
```

"AVD Manager"에 들어가신 후 AVD를 선택하고 "Start..."를 클릭하시면 안드로이드 VM이 실행됩니다.

> 보통의 경우 안드로이드 스튜디오 설치 중 AVD도 설치되지만, 안드로이드 스튜디오 설치 중 AVD가 설치되지 않는 경우는 흔한 경우랍니다. 다음 가이드[Android Studio User Guide](https://developer.android.com/studio/run/managing-avds.html)를 따라서 새로운 AVD를 수동으로 만드실 수도 있습니다.

## React Native 설치 테스트하기 (iOS VM으로 확인하기)

React Native command line interface를 이용해 새로운 React Native 프로젝트를 시작해볼게요.
"AwesomeProject"라는 멋진 이름을 가진 프로젝트로요 :)
다음 명령어들을 따라치면 프로젝트가 생기고 가상 iOS머신에서 우리의 프로젝트가 곧장 실행될거에요!

```
react-native init AwesomeProject
cd AwesomeProject
react-native run-ios
```

조금만 기다리면 우리의 AwesomeProject가 실행된 모습을 보실 수 있을거에요.

`react-native run-ios`명령어는 우리의 앱을 실행하는 방법 중 하나일 뿐이랍니다. Xcode에서 실행하셔도 되고, [Nuclide](https://nuclide.io/)를 통해 실행하셔도 됩니다.

## React Native 설치 테스트하기 (Android VM으로 확인하기)

만약 바로 위에있는 iOS로 테스트를 해본 상태라면, 마지막 줄의 `react-native run-android`만 입력하세요.
React Native command line interface를 이용해 새로운 React Native 프로젝트를 시작해볼게요.
"AwesomeProject"라는 멋진 이름을 가진 프로젝트로요 :)
다음 명령어들을 따라치면 프로젝트가 생기고 가상 안드로이드 머신에서 우리의 프로젝트가 곧장 실행될거에요!

```
react-native init AwesomeProject
cd AwesomeProject
react-native run-android
```

만약 모든 환경이 제대로 설정되었다면, 안드로이드 VM하나가 실행되고 우리 앱이 안드로이드에 뜰거랍니다.
`react-native run-android`명령어는 우리 앱을 실행하는 방법 중 하나일 뿐이랍니다. Android Studio에서 실행하셔도 되고, [Nuclide](https://nuclide.io/)를 이용하셔도 됩니다.


### 앱 수정해보기

만약 위에서 성공적으로 앱이 실행되었다면, 약간 수정을 해봅시다!

1. iOS 앱 수정하기
  - `index.ios.js` 파일을 열고 몇몇 줄을 수정해 보세요.
  - `Command⌘ + R`을 눌러서 iOS Simulator를 다시 로딩해 어떤 변화가 있는지 확인해보세요.

2. Android 앱 수정하기
  - `index.android.js` 파일을 열고 몇몇 줄을 수정해 보세요.
  - `R`키를 두번 누르거나 `Reload`를 개발자메뉴에서 눌러 어떤 변화가 있는지 확인해보세요.


### 이게 끝이에요!

축하합니다! 여러분은 성공적으로 React Native앱을 실행하고 수정까지 해 보셨어요.

<center><img src="http://facebook.github.io/react-native/releases/0.37/img/react-native-congratulations.png" width="150"></img></center>


## 이젠 뭘해야할까요?

- 만약 이미 존재하는 앱에 React Native를 적용하고 싶으시다면, [Integration guide](docs/integration-with-existing-apps.html) 문서를 확인해보세요.

- 만약 위 튜토리얼이 제대로 실행되지 않았다면, [Troubleshooting](docs/troubleshooting.html#content) 문서를 확인해 보세요.

- 만약 React Native에 대해 좀 더 알고싶으시다면, [Tutorial](docs/tutorial.html)문서를 확인해보세요.
