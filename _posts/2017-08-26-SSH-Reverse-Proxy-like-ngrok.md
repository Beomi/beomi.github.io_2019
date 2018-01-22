---
title: "로컬 개발서버를 HTTPS로 세상에 띄우기(like ngork)"
date: 2017-08-26
layout: post
categories:
- tips
published: true
image: https://d1sr4ybm5bj1wl.cloudfront.net/img/2017-08-26-SSH-Reverse-Proxy-like-ngrok.jpg
---

> 이번 가이드를 따라가기 위해서는 HTTP(80/tcp) 포트가 열려있는 서버와 개인 도메인이 필요합니다.

## 들어가기 전

django, node.js, react, vue와 같은 웹 개발(Backend & Frontend)을 진행하다보면 모바일 디바이스나 타 디바이스에서 로컬 서버에 접근해야하는 경우가 있습니다. 

하지만 보통 개발환경에서는 개발기기가 공인 IP를 갖고 있는것이 아니라 내부 NAT에서 개발이 이루어지고, 웹과 내부 개발기기 사이에는 방화벽이 있습니다. 집에서 개발한다면 공유기가, 회사에서 개발한다면 회사의 라우터 정책 기준이 있습니다. 

일반적인 경우 네트워크 정책은 나가는(Outbound) 트래픽은 대부분의 포트가 열려있는 한편 들어오는(Inbound) 트래픽에는 극소수의 포트만 열려있습니다.

만약 로컬 서버에서 일반적으로 HTTP가 사용하는 80/tcp 포트로 서버를 띄어놓았다면 대부분의 경우 이 포트는 막혀있습니다. (개발용 서버인 8000/8080/4000/3000등도 마찬가지입니다. 극소수 빼고는 기본적으로 다 막아둡니다.)

이렇게 포트가 막혀있다면 우리가 로컬에 띄어둔 서버가 아무리 모든 IP에서의 접근을 허용한다고 해도 중간에 있는 라우터에서 막아버리기 때문에 LTE등의 모바일 셀룰러같은 외부에서의 접속은 사실상 불가능합니다.

따라서 이를 해결하기 위해 [ngrok](https://ngrok.com/)와 같은 SSH 터널링을 이용합니다. 하지만 ngrok 서비스 서버는 기본적으로 해외에 있고, 무료 Plan의 경우 분당 connection의 개수를 40개로 제한하고 있습니다. 만약 CSS나 JS, 이미지같은 static파일 요청 하나하나가 각각 connection을 사용한다면, 짧은 시간 내 여러번 새로고침은 수십개의 connection을 만들어버리고 ngrok은 요청을 즉시 차단해버립니다.

> 물론 `keep-alive`를 지원하는 클라이언트/서버 설정이 이루어지면 connection은 새로고침을 해도 늘어나지 않습니다. 하지만 모든 클라이언트가 `keep-alive`를 지원하지는 않습니다.

하지만 유료 플랜이라고 해서 무제한 connection을 지원하지는 않기 때문에 마음놓고 새로고침을 하기는 어렵습니다.

이번 가이드에서는 ngrok같이 로컬 개발 서버(장고의 runserver, webpack의 webpack-dev-server)를 다른 서버에 SSH Proxy를 통해 전달하는 법, 그리고 CloudFlare를 통해 HTTPS서버로 만드는 것까지를 다룹니다.

## 재료준비

### 80/tcp가 열린 서버가 있어야 합니다

이번 가이드에서는 80/tcp 포트가 열려있는 서버가 "꼭" 있어야 합니다. 물론 서버에는 공인 IP가 할당되어야 합니다. 그래야 나중에 CloudFlare에서 DNS설정을 해줄 수 있습니다.

> 만약 집에 이런 서버를 둔다면 포트포워딩을 통해 80/tcp만 열어줘도 됩니다.

한국서버가 가장 좋지만(물리적으로 가까우니까) 일본 VPS도 속도면에서 큰 손해를 보지는 않습니다. (물론 게임서버라면 약간 이야기가 다르지만, 웹 서버용으로는 충분합니다.)

이번엔 ubuntu server os를 세팅하는 방법으로 진행합니다. (ubuntu 14.04, 16.04 모두 가능합니다.)

### (HTTPS를 쓰려면) 도메인이 있어야 합니다

개인 도메인이 있어야 CloudFlare라는 DNS서비스에 등록을 하고 HTTPS를 이용할 수 있습니다. 도메인이 없거나 HTTPS를 사용하지 않아도 되는 상황이라면 공인 IP만 있어도 무방합니다.

## 만들어보기

ubuntu 서버와 도메인이 준비되었다면 이제 시작해봅시다!

### 서버 세팅하기

서버 세팅은 크게 어렵지 않습니다. ssh로 서버에 접속해 아래 명령어를 그대로 입력해보세요.

```bash
sshd -T | grep -E 'gatewayports|allowtcpforwarding'
```

위 명령어는 sshd의 `gatewayports`속성과 `allowtcpforwarding`속성값을 가져옵니다. 만약 여러분이 ubuntu를 설치하고 아무런 설정을 건드리지 않았다면 다음과 같이 뜰거에요.

```bash
gatewayports no
allowtcpforwarding yes
```

우리는 저 두개를 모두 `yes`로 만들어야 합니다. 아래 명령어를 ssh에 그대로 입력해주세요.

```bash
sudo echo "gatewayports yes\nallowtcpforwarding yes" >> /etc/ssh/sshd_config
```

물론 `/etc/ssh/sshd_config` 파일에서 직접 수정해주셔도 됩니다.

> 유의: 이와같이 사용하면 서버의 모든 유저가 SSH Proxy를 사용할수 있게 됩니다. 이를 막으려면 아래와 같이 `Match User 유저이름`을 넣고 진행해주세요. 
```
Match User beomi
  AllowTcpForwarding yes
  GatewayPorts yes
```

정말 간단하게 서버 설정이 끝났습니다 :)

### 로컬 8000포트를 원격 80포트로 연결하기

로컬 터미널에서 아래와 같이 명령어를 입력하면 설정이 끝납니다.

```bash
# ssh 원격서버유저이름@서버ip -N -R 서버포트:localhost:로컬포트 
ssh beomi@47.156.24.36 -N -R 80:localhost:8000
```

위 명령어는 `47.156.24.36`라는 ip를 가진 서버에 `beomi`라는 사용자로 ssh접속을 하고, 로컬의 8000번 포트를 원격 서버의 80포트로 연결하는 명령어입니다.

즉, `localhost:8000` 은 `47.156.24.36:80`와 같아진거죠!

이제 모바일 디바이스에서도 `http://47.156.24.36`라고 입력하면 개발 서버에 들어올 수 있어요.

### CloudFlare로 SSL 붙이기 

만약 서버주소를 외우는게 불편하지 않으시고 & HTTPS가 필요하지 않으시다면, 아래부분은 진행하지 않아도 괜찮습니다.

이 챕터에서는 [CloudFlare](https://www.cloudflare.com/)에 도메인을 연결할 때 제공받을 수 있는 SSL서비스를 통해 HTTP로 서빙되는 우리 서비스를 '안전한' HTTPS로 서빙하도록 도와줍니다.

![]({{site.static_url}}/img/2017-08-26-SSH-Reverse-Proxy-like-ngrok-cloudflare-flexssl.png)

CloudFlare의 Flex SSL을 사용하면 우리 서버가 HTTPS가 아닌 HTTP로 서빙되더라도 클라우드 플레어에서 HTTPS로 만들어줍니다.

> 사실 이 기능은 보안을 위해서 있는 서비스라고 보기는 어렵습니다. 물론 브라우저/클라이언트와 CloudFlare 간 통신에서는 좀 더 안전한 통신이 가능하지만, 도메인별로 다른 SSL 인증서를 사용하지 않고 여러 도메인을 그룹핑한 인증서를 사용하고 있는 문제가 있고, 결국 CloudFlare와 우리 서버간에는 HTTP로 통신이 이루어지기 때문에 CloudFlare와 우리 서버 사이 Node에서 이루어지는 공격은 막기 어렵습니다. 따라서 이런 경우는 Geolocation와 같은 HTTPS 위에서만 사용할 수 있는 기능등을 테스트 서버를 통해 구동할 경우 유용합니다.

우선 CloudFlare에 가입하고 도메인을 CloudFlare에 등록해주세요.

도메인을 등록하고 `DNS` 탭에 들어가서 다음과 같이 서브 도메인(혹은 루트 도메인)을 서버 ip에 연결한 후 우측 하단의 구름모양을 켜 주세요. 이 구름모양을 켜 주면 이 도메인으로 온 요청은 CloudFlare의 CDN망을 통해 전달됩니다. (CSS/JS캐싱도 해줍니다!)

![]({{site.static_url}}/img/dropbox/Screenshot%202017-08-27%2014.08.01.png?dl=1)

도메인을 등록했으면 아래와 같이 `Crypto`탭에서 SSL을 `Flexible`로 바꿔주세요.

- off: 말 그대로 HTTPS를 끕니다.
- **flexible**: 우리 서버가 HTTP라도 클라우드플레어로 온 HTTPS요청을 우리서버에 HTTP로 바꿔서 보내줍니다.
- full: 우리 서버도 HTTPS가 지원되어야 하지만, 꼭 CA에게 인증된 '안전한' 인증서일 필요는 없습니다. 자체서명 인증서라도 괜찮아요.
- full (strict): 우리 서버가 CA에게 인증된 '안전한' 인증서를 통해 HTTPS로 서빙을 해야만 합니다. 자체서명 인증서는 쓸 수 없어요.

이 설정은 off에서 다른 옵션으로 바꿔주면 약간의 시간이 걸리지만 안전한 SSL 인증서를 CloudFlare에서 만들어줍니다.

![]({{site.static_url}}/img/dropbox/Screenshot%202017-08-27%2013.58.36.png?dl=1)

## `proxy` 명령어에 연결하기

보통 `runserver`와 같은 개발 서버를 띄우는 명령은 자주 사용하지만 우리가 사용하는 긴 명령어는 한번에 치기도 어렵고 옵션 기억하기도 귀찮은 경우가 많습니다. 쉘에서 지원하는 `alias`를 통해 아래와 같이 만들어줍시다.

```bash
# .zshrc / .bashrc / .bash_profile 와 같이 쉘이 켜질때 실행되는 부분에 넣어주세요

alias proxy="ssh beomi@47.156.24.36 -N -R 80:localhost:8000"
# alias proxy="ssh 원격서버유저이름@서버ip -N -R 서버포트:localhost:로컬포트"
``` 

이와 같이 입력하고 저장한 후 터미널을 다시 켜주면 이제 `proxy`라는 명령어를 치면 로컬 개발 서버가 HTTPS로 세상에 오픈되는 것을 볼 수 있습니다 :)

## 마치며

ngrok는 아주 간편하고 좋은 서비스입니다. 하지만 모바일과 PC 웹을 동시에 테스트 하는 경우 connection개수를 금방 넘어버리고 ngrok를 새로 실행할 때마다 도메인 이름이 바뀌는점이 불편해 위와 같이 Proxy서버를 만들어 개발하는데 사용합니다.

다만 CloudFlare의 CSS/JS캐싱 전략에 의해 변경된 파일이 가져와지지 않는 점은 있는데, 이때는 Apache등의 웹서버에서 제공하는 virtualhost기능과 let's encrypt의 무료 SSL 서비스를 조합해 사용하면 CloudFlare없이도 동일하게 환경을 만들어 줄 수 있습니다. 하지만 웹서버 자체에 대한 이해가 필요하며 SSL을 붙이는 일도 상당히 귀찮기때문에 단순하게 CloudFlare에서 도에인 모드를 아래와 같이 'Development Mode'로 설정해 주면 캐싱 하는 것을 방지할 수 있습니다.

![]({{site.static_url}}/img/dropbox/Screenshot%202017-08-27%2014.42.36.png?dl=1)

### 여담

django의 경우에는 `settings.py`파일의 `ALLOWED_HOSTS`에 우리가 지정한 도메인 (ex: shop.testi.kr)을 추가해줘야 합니다.

```python
# settings.py

ALLOWED_HOSTS = ['*'] # 모든 Host에서의 접근을 허용
# ALLOWED_HOSTS = ['shop.testi.kr'] # shop.testi.kr 도메인 host를 통한 접근을 허용
```

webpack의 webpack-dev-server에서 위와같이 사용하려면 `webpack.config.js`파일을 아래와 같이 만들어주면 됩니다.

```javascript
// webpack.config.js
const path = require('path');

module.exports = {
    entry: './src/index.js',
    output: {
        path: path.resolve(__dirname, 'dist'),
        filename: 'bundle.js'
    },
    devServer: {
        host: "0.0.0.0", // 모든 host에서의 접근을 허용
        disableHostCheck: true // Host Check를 끕니다
    }
```