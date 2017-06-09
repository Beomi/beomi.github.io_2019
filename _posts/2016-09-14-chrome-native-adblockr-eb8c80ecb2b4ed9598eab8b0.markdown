---
author: livingmethod
comments: true
date: 2016-09-14
layout: post
link: http://blog.jblee.kr/2016/09/14/chrome-native-adblockr-%eb%8c%80%ec%b2%b4%ed%95%98%ea%b8%b0/
slug: chrome-native-adblockr-%eb%8c%80%ec%b2%b4%ed%95%98%ea%b8%b0
title: Chrome Native Adblockr 대체하기
wordpress_id: 407
image: https://livingmethod.files.wordpress.com/2016/09/e18489e185b3e1848fe185b3e18485e185b5e186abe18489e185a3e186ba-2016-09-14-17-35-38.png
---

오늘 크롬을 켜고 인터넷 브라우징을 하는데 일상적으로라면 Native Adblockr로 인해 광고가 뜨지 않아야 하는 곳에서 광고가 떴다.

크롬에 들어가보니 크롬측에서 앱을 비활성화 한 것. 재활성화 하려 해도 크롬에서 중단시켰다며 활성화가 되지 않았다.

그래서 앱의 최근 리뷰 중 개발자 댓글로 프로그램이 구성된 방법이 uBlock + 커스텀필터 라고 하고, 커스텀 필터는 개발자 깃헙 소스인

    
    https://raw.githubusercontent.com/NativeHyun/HyunGuard/master/General/general.txt


이 파일을 참고해 작동한다고 했다.

그래서 커스텀 Chrome Native Adblockr를 구성해보기로 생각.

크롬 웹 스토어에서 uBlock을 검색, 두가지가 나왔다. uBlock orign와 uBlock.

전자가 더 많은 리뷰가 있어 전자로 다운받았다.

그리고 uBlock의 세팅(크롬 우측상단 앱 아이콘 클릭시 나오는 팝업의 좌측 상단에 작은 설정아이콘)에 들어가 아래와 같이 사용자 필터로 위의 깃헙소스를 추가해 준다.

![%e1%84%89%e1%85%b3%e1%84%8f%e1%85%b3%e1%84%85%e1%85%b5%e1%86%ab%e1%84%89%e1%85%a3%e1%86%ba-2016-09-14-17-35-38](https://livingmethod.files.wordpress.com/2016/09/e18489e185b3e1848fe185b3e18485e185b5e186abe18489e185a3e186ba-2016-09-14-17-35-38.png)

그러면 Native Adblockr와 정확히 동일하게 광고가 차단된다.

Ps. 왜 앱이 내려간건지 모르겠다..^^;;
