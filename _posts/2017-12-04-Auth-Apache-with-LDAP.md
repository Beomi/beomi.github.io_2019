---
title: "LDAP로 Apache 웹서비스 로그인 인증하기"
date: 2017-12-04
layout: post
categories:
- Apache
- Ubuntu
- LDAP
published: false
image: https://beomi-tech-blog.s3.ap-northeast-2.amazonaws.com/img/ldap-logo.png
---

## 배경

사내용 웹 서비스 하나를 완성하고 나서 붙게 된 수요: "로그인한 사용자만 이용하게 해야해요."

즉, 인증 시스템을 붙여야 하는 상황. 하지만 독자적인 인증 시스템(Django의 유저 등)을 사용하지는 못하고 ActiveDirectory라는 인증 시스템을 이용해야 했다.

ActiveDirectory는 LDAP와 호환되기 때문에 LDAP 프로토콜로 접속하면 Apache2단에서 인증을 붙일 수 있을 것 같았다.

## 환경

### 웹 서버

- Apache2.4

- Ubuntu 16.04 LTS

### LDAP(Active Directory) 서버

- AD Proxy로 동작 

- LDAPS로만 동작

- 아는정보
  - LDAPS URL
  - BindDN
  - BindPassword

- 필요한파일
  - LADP서버 접속용 인증서(`.crt`)파일들

### 사전 설치

우선 LDAP를 Apache2가 사용할 수 있도록 모듈 두개를 활성화 시켜줘보았다. (ldap authnz_ldap 두개는 apache2를 설치시 함께 설치된다.)

```sh
sudo a2enmod ldap authnz_ldap
sudo service apache2 restart
```

그리고 VirtualHost(.conf)파일을 아래와 같이 수정해보았다.

```sh {% raw %}
LoadModule ldap_module modules/mod_ldap.so
LoadModule authnz_ldap_module modules/mod_authnz_ldap.so
<VirtualHost *:80>
    ServerName myserver.domain.com # VirtualHost 서비스도메인
    DocumentRoot /home/ubuntu/myserver # 프로젝트폴더
    <Directory /home/ubuntu/myserver >
        Require all granted
    </Directory>
    ErrorLog ${APACHE_LOG_DIR}/error.log
    CustomLog ${APACHE_LOG_DIR}/access.log combined
    <Location "/"> # '/', 즉 모든 URL에 대해 인증 요구 
        AuthType Basic
        AuthBasicProvider ldap
        AuthName "Need Login"
        AuthLDAPURL "ldaps://ladp-server-url.com:636" # 제공받은 ladps URL
        AuthLDAPBindDN "DN_Value" # 제공받은 LADP접속용 DN
        AuthLDAPBindPassword "DN_Password" # 제공받은 LADP접속용 패스워드
        Require valid-user
    </Location>
</VirtualHost> {% endraw %}
```

### 그러나 에러..

이제 Apache2에서 AD 서버에 인증 요청만 붙이면 될 것이라 생각했지만 500 Internal Server Error만 난다.

![]({{site.static_url}}/img/dropbox/Screenshot%202017-12-05%2015.46.17.png)

`tail -f /var/log/apache2/error.log`을 통해 Apache의 로그를 찍어보려고 해도 에러가 전혀 찍히지 않는 상황.

![]({{site.static_url}}/img/dropbox/Screenshot%202017-12-05%2015.48.36.png)

무엇이 문제인가... 조금 더 까보기로 했다.

## 원인분석

### LogLevel debug

우선 로그가 찍히지 않는 이유를 생각해보았다. 보통 아파치의 `error.log`는 웹앱 서버에서 난 에러와 아파치 자체에서 난 에러는 확인할 수 있지만, 아파치 외부, 즉 AWS를 예로 들면 ELB등의 LoadBalancer에서 난 에러는 확인하지 못한다. 하지만 현재 가장 앞쪽에 놓여진 프로세스는 아파치이기 때문에 이 가능성은 낮다고 보았다.

그렇다면 다음으로는 로그 레벨을 의심해봐야 한다. 기본적으로 아파치는 LogLevel이 `warn`으로 되어있기 때문에 혹시 에러가 났지만 `warn`이나 `error`레벨이 아닌 더 낮은 레벨로 로그가 찍혔을 수도 있기 때문.

따라서 Apache2의 VirtualHost(sites-available 안 .conf파일)에서 LogLevel을 debug로 올려줘 로그를 더 자세히 확인해보자 생각했다.

```sh
LogLevel debug # 이 줄 추가 
LoadModule ldap_module modules/mod_ldap.so
LoadModule authnz_ldap_module modules/mod_authnz_ldap.so
# 이하 생략...
```

자세한 로그를 찍어보니 아래와 같이 `auth_ldap`에서 `Can't contact LDAP server`에러가 나는 것을 확인할 수 있었다.

```
[Tue Dec 05 07:28:44.920138 2017] [authnz_ldap:debug] [pid 3320:tid 140351109019392] mod_authnz_ldap.c(516): [client 211.39.137.9:6540] AH01691: auth_ldap authenticate: using URL ldaps://ladp-server-url.com
[Tue Dec 05 07:28:45.181978 2017] [authnz_ldap:info] [pid 3320:tid 140351109019392] [client 211.39.137.9:6540] AH01695: auth_ldap authenticate: user beomi authentication failed; URI / [LDAP: ldap_simple_bind() failed][Can't contact LDAP server]
```

즉, 아파치가 LDAP서버에 접속을 하지 못하고 있었다.

의심되는 상황은 여러개였다.

### 포트가 열려있나? telnet 

가장 의심이 되는 것은 방화벽이나 SecurityGroup 설정 등으로 인해 아파치가 올라간 EC2에서 LDAP로 접속하지 못하는 경우였다.

따라서 telnet으로 서버와 포트가 열려있는지 확인해보고자 했다. telnet은 프로토콜과 관계없이 서비스가 열려있는지 아닌지를 확인할 수 있기 때문.

```sh
telnet ladp-server-url.com 636
```

![]({{site.static_url}}/img/dropbox/Screenshot%202017-12-05%2016.33.26.png)

하지만 접속이 잘 된다. 그렇다면 방화벽이나 SG문제는 아닌것인데..

### 인증서버에 접속이 되나? ldapsearch

서버와 LDAP가 접속 자체는 되야한다면 뭔가 아파치에 설정을 잘못해준 것일 수 있으니, `ldapsearch`라는 도구를 이용해 아파치와 관계없이 접속이 '되는지'부터 확인해보고자 했다.

```sh
ldapsearch -d 1 -xLL -H ldaps://ladp-server-url.com:636 -D "DN_VALUE" -w "DN_PASSWORD"
```

![]({{site.static_url}}/img/dropbox/Screenshot%202017-12-05%2017.20.54.png)

에러 없이 잘 가져오는 듯 하다. (No such object는 유저 필터가 없어서 생김)

## 해결하기 

### ldap.conf에 .crt 등록

답은 정말 의외의 장소에 있었다.

`/etc/ldap/ldap.conf`파일에 아래와 같이 인증서 파일들을 넣어줘야 했다.

```sh
# TLS certificates (needed for GnuTLS)
TLS_CACERT      /home/ubuntu/PrimaryRootCA.crt
TLS_CACERT      /home/ubuntu/SSLCA-G2.crt
TLS_CACERT      /etc/ssl/certs/ca-certificates.crt
```

