---
author: livingmethod
comments: true
date: 2016-08-09 15:11:27+00:00
layout: post
link: http://blog.jblee.kr/2016/08/10/customac-%ec%84%a4%ec%b9%98-%eb%b6%84%ed%88%ac%ea%b8%b0/
slug: customac-%ec%84%a4%ec%b9%98-%eb%b6%84%ed%88%ac%ea%b8%b0
title: CustoMac  설치 분투기
wordpress_id: 330
categories:
- DevEnv
- MacOS
image: /img/old_post/os_x_el_capitan_roundup.jpg
---

기본적으로 커스텀맥(해킨토시) 설치는 큰 어려움이 따른다.

그런데, 이번에 설치한  OS X El Capitan은 기본적인 설정만으로도 상당히 쉽게 설치되었기 때문에(그래도 약간의 설정은 필요하다) 매우 놀랐다.

설치 PC사양은 다음과 같다.

    
    CPU: I5-4670 (Haswell, 하스웰)
    RAM: DDR3 8Gx2 (<span id="grpDescrip_">G.SKILL Ripjaws X Series 16GB (2 x 8GB)</span>)
    M/B: ASRock ASRock H87 Performance 에즈윈
    HDD: WD Blue 1TB (8MB cache / 2.5")
    VGA: AMD HD7970 3G (HIS 라데온 HD 7970 기가에디션 OC D5 3GB IceQ X² 잘만테크)


설치를 시도한 OS는 OS X 10.11.6 (El Capitan)버전이었고, 설치 디스크 제작은 순정 맥을 이용해 제작했다.

설치에 사용한 Kext와 여러 프로그램들은 아래 드롭박스 링크에서 받을 수 있다. PW:installosx

[[ 다운로드 ]](https://www.dropbox.com/s/adcn375wywotkxm/InstallOSX.zip?dl=0)




## [설치 과정]


가장 먼저 해야 하는 것은 바로 순정 설치 디스크를 제작하는 것이다.

순정 El Capitan을 받기 위해 맥의 AppStore에서 El Capitan을 다운로드 하면 LaunchPad에 저장된다.

저장이 완료되면 설치 창이 뜨는데, 간단히 무시하고 TonyMac의 [Unibeast](http://tonymacx86.com/resources/unibeast-6-2-0.314/)를 통해 GUI로 부팅 디스크를 만든다.

El Capitan / UEFI만 선택하면 부팅 디스크를 아주 깔끔하게 만들어준다.

부팅 및 설치는 전면 USB3.0단자를 이용해 이루어졌다.(혹자는 usb2.0으로 진행하라고 했지만, 큰 문제 없이 진행되었다.)

USB에는 여러 프로그램(MultiBeast / Clover / CloverConfigurator / 기타 kexts/Scripts)을 담아두면 OS X 설치 이후에 좀더 편안하게 설치 마무리를 진행할 수 있다.

위쪽에 올려둔 드롭박스 링크의 압축파일에는



	
  * [Clover Configuator](http://mackie100projects.altervista.org/download-clover-configurator) : EFI 파티션 자동인식 및 마운트 기능 / config.plist 수정기능 제공 / Clover 자동 확인 및 업데이트 제공

	
  * [Clover](https://sourceforge.net/projects/cloverefiboot/) : 클로버 부트로더. OS X으로 부팅 가능하게 만들어준다.

	
  * [MultiBeast](http://tonymacx86.com/resources/multibeast-el-capitan-8-2-3.319/) : OS X의 각종 드라이버(kext파일들)를 EFI파티션에 잡아준다. 이번설치에서는 굳이 쓰지 않아도 성공적으로 설치됨.

	
  * Kext파일들 : 위 HW에 필요했던 기본적인 kext들. EFI파티션의 KEXTS폴더에 10.11버전 폴더에 넣어주면 된다.

	
  * [MenuMeters](http://member.ipmu.jp/yuji.tachikawa/MenuMetersElCapitan/) : OS X 설치 후 시스템 상태를 메뉴바에서 그래픽으로 볼 수 있게 지원. OS X설치후 항상 쓰는 프로그램이라 넣었을 뿐, 운영체제 설치 자체와는 관련이 전혀 없다.

	
  * [AudioCloverHDMI](https://github.com/toleda/audio_CloverHDMI) : OS X에서 기본적으로 지원하지 않는 HDMI 오디오 출력을 가능하게 만들어준다. 스크립트형.


이렇게 구성되어있다.

+alpha:

이번에 사용한 메인보드가 ASRock보드인데, 부트로더가 efi파일을 잡지 않아 버그가 난  경우가 있었다.

https://www.x86.co.kr:447/qa/1274453

클로버를 저렇게 설치해주면 된다.
