---
title: "PySpark & Hadoop: 1) Ubuntu 16.04에 설치하기"
date: 2017-11-09
layout: post
categories:
- Python
- Ubuntu
published: true
image: /img/PySpark_n_Hadoop_on_Ubuntu_16.jpg
---

## 들어가며

Spark의 Python버전인 PySpark를 사용할 때 서버가 AWS EMR등으로 만들어진 클러스터가 존재하고, 우리가 만든 프로그램과 함수가 해당 클러스터 위에서 돌리기 위해서는 PySpark를 로컬이 아니라 원격 서버에 연결해 동작하도록 만들어야 합니다. 

이번 글에서는 PySpark와 Hadoop을 설치하고 설정하는 과정으로 원격 EMR로 함수를 실행시켜봅니다.

> Note: 이번 글은 Ubuntu 16.04 LTS, Python3.5(Ubuntu내장)를 기준으로 진행합니다.

AWS에서 EC2를 생성해 주세요. VPC는 기본으로 잡아주시면 됩니다. 성능은 `t2-micro`의 프리티어정도도 괜찮습니다. 무거운 연산은 나중에 다룰 AWS EMR 클러스터에 올려줄 것이기 때문에, 클라이언트 역할을 할 EC2 인스턴스는 저성능이어도 괜찮습니다.

들어가기 전에 우선 apt 업데이트부터 진행해 줍시다.

```bash
sudo apt-get update && sudo apt-get upgrade -y
```

## PySpark 설치하기

Ubuntu 16 OS에는 기본적으로 Python3이 설치되어있습니다. 하지만 pip는 설치되어있지 않기 때문에 아래 명령어로 먼저 Python3의 pip를 설치해줍시다.

```bash
# pip/pip3을 사용가능하게 만듭니다.
sudo apt-get install python3-pip -y
```

설치가 완료되면 이제 Python3의 pip를 사용할 수 있습니다. 아래 명령어로 pip를 통해 PySpark를 설치해 봅시다.

```bash
# 최신 버전의 PySpark를 설치합니다.
pip3 install pyspark -U --no-cache
```

위 명령어에서 `-U`는 `--upgrade`의 약자로, 현재 설치가 되어있어도 최신버전으로 업그레이드 하는 것이고, `--no-cache`는 로컬에 pip 패키지의 캐싱 파일이 있더라도 pypi서버에서 다시 받아오겠다는 의미입니다.

> 현재 PySpark 2.2.0은 버전과 다르게 2.2.0.post0라는 버전으로 pypi에 올라가 있습니다. 이로인해 `pip install pyspark` 로 진행할 경우 `Memeory Error`가 발생하고 설치가 실패하므로, 2.2.0버전을 설치한다면 위 명령어로 설치를 진행해주세요.

## Hadoop 설치하기

### JAVA JDK 설치하기

Hadoop을 설치하기 위해서는 JAVA(JDK)가 먼저 설치되어야 합니다. 아래 명령어로 openjdk를 설치해주세요.

```bash
# Java 8을 설치합니다.
sudo apt-get install openjdk-8-jre -y
```

### Hadoop Binary 설치하기

Hadoop은 Apache의 홈페이지에서 [최신 릴리즈 링크](http://hadoop.apache.org/releases.html)에서 바이너리 파일의 링크를 가져옵시다.

![]({{site.static_url}}/img/dropbox/Screenshot%202017-11-09%2015.23.26.png)

원하는 Hadoop 버전의 `Binary` 링크를 클릭해 바이너리를 받을 수 있는 페이지로 들어갑시다. 글쓰는 시점에는 2.8.2가 최신 버전입니다. 링크를 타고 들어가면 아래와 같이 HTTP로 파일을 받을 수 있는 링크가 나옵니다.

![]({{site.static_url}}/img/dropbox/Screenshot%202017-11-09%2015.25.04.png)

글을 보는 시점에는 링크 주소는 다를 수 있지만, HTTP 링크 중 하나를 복사하고 진행하면 됩니다. 이 글에서는 네이버 서버의 미러를 이용합니다.

이제 다시 서버로 돌아가봅시다. 아래 명령어를 통해 wget으로 Hadoop Binary를 서버에 받아줍시다.

```bash
wget 여러분이_복사한_URL
# 예시
# wget http://mirror.navercorp.com/apache/hadoop/common/hadoop-2.8.2/hadoop-2.8.2.tar.gz
```

이제 압축을 풀어줍시다. 아래 명령어로 압축을 `/usr/local`에 풀어줍시다.

```bash
sudo tar zxvf ./hadoop-* -C /usr/local
```

압축을 풀면 `/usr/local/hadoop-2.8.2`라는 폴더가 생기지만 우리가 사용할때 버전이 붙어있으면 사용하기 귀찮으므로 이름을 `/usr/local/hadoop`으로 바꾸어줍시다.

```bash
sudo mv /usr/local/hadoop-* /usr/local/hadoop
```

이제 파일을 가져오고 설치는 완료되었지만, 실제로 Hadoop을 PySpark등에 붙여 사용하려면 `PATH`등록을 해줘야 합니다.

아래 명령어를 전체 복사-붙여넣기로 진행해 주세요.

```bash
echo "
export JAVA_HOME=$(readlink -f /usr/bin/java | sed "s:bin/java::")
export PATH=\$PATH:\$JAVA_HOME/bin
export HADOOP_HOME=/usr/local/hadoop
export PATH=\$PATH:\$HADOOP_HOME/bin
export HADOOP_CONF_DIR=\$HADOOP_HOME/etc/hadoop
export YARN_CONF_DIR=\$HADOOP_HOME/etc/hadoop
" >> ~/.bashrc
```

이제 ssh를 `exit`한 뒤 다시 서버에 ssh로 접속하신 후, 아래 명령어를 입력해 보세요. 아래 사진처럼 나오면 설치가 성공적으로 진행된 것이랍니다.

```bash
/usr/local/hadoop/bin/hadoop
```

![]({{site.static_url}}/img/dropbox/Screenshot%202017-11-09%2015.49.19.png)

## 끝이지만 끝이 아닌..

사실 PySpark와 Hadoop만을 사용하는 것은 큰 의미가 있는 상황은 아닙니다. AWS EMR와 같은 클러스터를 연결해 막대한 컴퓨팅 파워가 있는 서버에서 돌리는 목적이 Spark를 쓰는 이유입니다. 다음 글에서는 AWS EMR을 구동하고 우리가 방금 설정한 Ubuntu 서버에서 작업을 EMR로 보내는 내용을 다뤄봅니다.
