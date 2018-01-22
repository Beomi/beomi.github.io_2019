---
title: "PySpark & Hadoop: 2) EMR 클러스터 띄우고 PySpark로 작업 던지기"
date: 2017-11-27
layout: post
categories:
- Python
- PySpark
published: true
image: https://d1sr4ybm5bj1wl.cloudfront.net/img/PySpak_n_Hadoop_EMR_and_PySpark.png
---

> 이번 글은 [PySpark & Hadoop: 1) Ubuntu 16.04에 설치하기](/2017/11/09/Install-PySpark-and-Hadoop-on-Ubuntu-16-04)와 이어지는 글입니다.

## 들어가며

이전 글에서 우분투에 JAVA/Hadoop/PySpark를 설치해 spark를 통해 EMR로 작업을 던질 EC2를 하나 생성해보았습니다. 이번에는 동일한 VPC그룹에 EMR 클러스터를 생성하고 PySpark의 `yarn`설정을 통해 원격 EMR에 작업을 던져봅시다.

## EMR 클러스터 띄우기 

AWS 콘솔에 들어가 EMR을 검색해 EMR 대시보드로 들어갑시다.

![AWS 콘솔에서 EMR검색하기]({{site.static_url}}/img/dropbox/Screenshot%202017-11-27%2016.52.49.png)

EMR 대시보드에서 '클러스터 생성'을 클릭해주세요.

![EMR 대시보드 첫화면에서 클러스터 생성 클릭]({{site.static_url}}/img/dropbox/Screenshot%202017-11-27%2016.53.53.png)

이제 아래와 같이 클러스터이름을 적어주고, 시작 모드를 '클러스터'로, 릴리즈는 최신 릴리즈 버전(현 5.10이 최신)으로, 애플리케이션은 Spark를 선택해주세요.

그리고 EC2 키 페어를 갖고있다면 기존에 갖고있는 `.pem`파일을, 없다면 새 키를 만들고 진행하세요.

주황색 표시 한 부분 외에는 기본 설정값 그대로 두면 됩니다. 로깅은 필요한 경우 켜고 필요하지 않은 경우 꺼두면 됩니다.

그리고 할 작업에 따라 인스턴스 유형을 r(많은 메모리), c(많은 CPU), i(많은 스토리지), p(GPU)중 선택하고 인스턴스 개수를 원하는 만큼 선택해주면 됩니다.

많으면 많을수록 Spark작업이 빨리 끝나는 한편 비용도 그만큼 많이 듭니다. 여기서는 기본값인 `r3.xlarge` 인스턴스 3개로 진행해 봅시다. 인스턴스 3대가 생성되면 한대는 Master 노드가, 나머지 두대는 Core 노드가 됩니다. 앞으로 작업을 던지고 관리하는 부분은 모두 Master노드에서 이루어집니다.

![EMR Spark 클러스터 만들기]({{site.static_url}}/img/dropbox/Screenshot%202017-11-27%2016.55.59.png)

설정이 끝나고 나면 아래 '클러스터 생성' 버튼을 눌러주세요.

![클러스터 생성 클릭]({{site.static_url}}/img/dropbox/Screenshot%202017-11-27%2017.06.32.png)

클러스터가 시작되고 '준비' 단계가 될 때까지는 약간의 시간(1~3분)이 걸립니다. '마스터 퍼블릭 DNS'가 화면에 뜰 때까지 잠시 기다려 줍시다.

![클러스터: PySpark화면]({{site.static_url}}/img/dropbox/Screenshot%202017-11-27%2017.11.49.png)

클러스터가 준비가 완료되면 아래와 같이 '마스터 퍼블릭 DNS' 주소가 나옵니다. 

![클러스터: PySpark DNS나온 화면]({{site.static_url}}/img/dropbox/Screenshot%202017-11-27%2017.19.56.png)

'마스터 퍼블릭 DNS'는 앞으로 설정할때 자주 사용하기 때문에 미리 복사를 해 둡시다.

```bash
# 이번에 만들어진 클러스터의 마스터 퍼블릭 DNS
ec2-13-124-83-135.ap-northeast-2.compute.amazonaws.com
```

이렇게 나오면 우선 클러스터를 사용할 준비가 완료된 것으로 볼 수 있습니다. 이제 다시 앞 글에서 만든 EC2를 설정해봅시다.

## EC2 설정 관리하기 

이제 EMR 클러스터가 준비가 완료되었으니 EC2 인스턴스에 다시 ssh로 접속을 해 봅시다.

이전 편인 [PySpark & Hadoop: 1) Ubuntu 16.04에 설치하기](/2017/11/09/Install-PySpark-and-Hadoop-on-Ubuntu-16-04)글을 읽고 따라 왔다면 여러분의 EC2에는 아마 JAVA와 PySpark, 그리고 Hadoop이 설치가 되어있을겁니다.

우리는 Hadoop의 `yarn`을 통해서 EMR 클러스터에 spark작업을 던져주기 때문에 이 부분을 설정을 조금 해줘야 합니다.

이전 편을 따라왔다면 아래 두 파일을 수정해주면 되고, 만약 따로 Hadoop을 설치해줬다면 `which hadoop`을 통해서 나오는 주소를 약간 수정해 사용해주면 됩니다.

우선 앞서 우리가 Hadoop을 설치해준 곳은 `/usr/local/hadoop/bin/hadoop` 입니다.

![which hadoop]({{site.static_url}}/img/dropbox/Screenshot%202017-11-27%2017.32.44.png)

그리고 우리가 수정해줘야 하는 두 파일은 위와 같은 위치에 있는 `core-site.xml`파일, 그리고 `yarn-site.xml` 파일입니다. 즉, 절대 경로는 아래와 같습니다.

```bash
# core-site.xml
/usr/local/hadoop/etc/hadoop/core-site.xml
# yarn-site.xml
/usr/local/hadoop/etc/hadoop/yarn-site.xml
```

> 만약 다른 곳에 설치했다면 `/하둡을설치한위치/etc/hadoop/` 안의 `core-site.xml`와 `yarn-site.xml`을 수정하면 됩니다.

### `core-site.xml` 수정하기

이제 `core-site.xml`파일을 수정해 봅시다.

![core-site.xml 수정]({{site.static_url}}/img/dropbox/Screenshot%202017-11-27%2017.41.59.png)

`core-site.xml`에는 다음과 같이 `fs.defaultFS`라는 name을 가진 property를 하나 추가해주면 됩니다. 그리고 그 값을 `hdfs://마스터퍼블릭DNS`로 넣어줘야 합니다.

```xml
<!-- core-site.xml -->
<?xml version="1.0" encoding="UTF-8"?>
<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>
<configuration>
<property>
    <name>fs.defaultFS</name>
    <value>hdfs://ec2-13-124-83-135.ap-northeast-2.compute.amazonaws.com</value>
</property>
</configuration>
```

수정은 `vim`이나 `nano`등의 편집기를 이용해주세요.

### `yarn-site.xml` 수정하기

이제 다음 파일인 `yarn-site.xml`파일을 수정해 봅시다.

![yarn-site.xml 수정]({{site.static_url}}/img/dropbox/Screenshot%202017-11-27%2017.46.19.png)

`yarn-site.xml`에는 다음과 같이 두가지 설정을 마스터퍼블릭DNS로 넣어줘야 합니다. `address`에는 포트도 추가적으로 붙여줘야 합니다.

```xml
<?xml version="1.0"?>
<configuration>
<property>
    <name>yarn.resourcemanager.address</name>
    <value>ec2-13-124-83-135.ap-northeast-2.compute.amazonaws.com:8032</value>
</property>
<property>
    <name>yarn.resourcemanager.hostname</name>
    <value>ec2-13-124-83-135.ap-northeast-2.compute.amazonaws.com</value>
</property>
</configuration>
```

이렇게 두 파일을 수정해주었으면 EC2에서 설정을 수정할 부분은 끝났습니다.

## EMR 클러스터 설정 관리하기

### 같은버전 Python 설치하기

Spark에서 파이썬 함수(혹은 파일)을 실행할 때 Spark가 실행되고있는 파이썬 버전과 PySpark등을 통해 Spark 서버로 요청된 파이썬 함수의 버전과 일치하지 않으면 Exception을 일으킵니다.

![Python driver 3.4_3.5 Exception]({{site.static_url}}/img/dropbox/Screenshot%202017-11-27%2020.53.05.png)

현재 EMR에 설치되어있는 python3은 3.4버전인데, EC2(Ubuntu 16.04)의 파이썬 버전은 3.5버전이기 때문에 Exception이 발생합니다. 

아래 세 가지 방법 중 하나를 선택해 해결해주세요.

#### 첫번째 방법: Ubuntu EC2에 Python3.4를 설치하기

Ubuntu16은 공식적으로 Python3.4를 지원하지 않습니다. 하지만 간단한 방법으로 Python3.4를 설치할 수 있습니다.

아래 세 줄을 입력해주세요.

```shell
sudo add-apt-repository ppa:fkrull/deadsnakes
sudo apt-get update
sudo apt-get install python3.4 -y
```

이렇게 하면 Python3.4를 사용할 수 있습니다.

막 설치해준 Python3.4에는 아직 `pyspark`가 설치되어있지 않으니 아래 명령어로 `pyspark`를 설치해 줍시다.

```shell
python3.4 -m pip install -U pyspark --no-cache
```

이제 EMR 클러스터에 작업을 던져줍시다.

#### 두번째 방법: EMR을 이루는 인스턴스에 원하는 Python버전(3.5)를 설치하기

EMR에 python3.5를 설치해 문제를 해결해 봅시다.

> 만약 여러분이 Ubuntu 17버전을 사용한다면 기본적으로 Python3.6이 설치되어있기 때문에 아래 코드에서 `35` 대신 `36`을 이용해주시면 됩니다.

이제 SSH를 통해 EMR Master에 접속해 봅시다.

```shell
chmod 400 sshkey.pem # ssh-add는 권한을 따집니다. 400으로 읽기권한만 남겨두세요.
ssh-add sshkey.pem # 여러분의 .pem 파일 경로를 넣어주세요.
ssh hadoop@ec2-13-124-83-135.ap-northeast-2.compute.amazonaws.com
```

![SSH Login EMR]({{site.static_url}}/img/dropbox/Screenshot%202017-11-27%2020.35.28.png)

로그인을 하고 나서 파이썬 버전을 알아봅시다. 파이썬 버전은 아래 사진처럼 볼 수 있습니다.

![EMR python은 3.4버전]({{site.static_url}}/img/dropbox/Screenshot%202017-11-27%2017.24.59.png)

파이썬이 3.4버전인것을 확인할 수 있습니다.

한편, EC2의 파이썬은 아래와 같이 3.5버전입니다.

![EC2 python은 3.5버전]({{site.static_url}}/img/dropbox/Screenshot%202017-11-27%2017.25.24.png)

이제 EMR에 Python3.5를 설치해 줍시다.

```shell
sudo yum install python35
```

위 명령어를 입력하면 python3.5버전이 설치됩니다.

![yum install python35]({{site.static_url}}/img/dropbox/Screenshot%202017-11-27%2020.41.22.png)

Y/N을 물어보면 y를 눌러줍시다.

![Press y to install]({{site.static_url}}/img/dropbox/Screenshot%202017-11-27%2020.42.03.png)

`python3 -V`를 입력해보면 성공적으로 파이썬 3.5버전이 설치된 것을 볼 수 있습니다.

![Python3.5.1]({{site.static_url}}/img/dropbox/Screenshot%202017-11-27%2020.44.05.png)

> 이 과정을 Master / Core 각 인스턴스별로 진행해주시면 됩니다. SSH로 접속 후 `python35`만 설치하면 됩니다.

이제 EMR 클러스터에 작업을 던져줍시다.

#### 세번째 방법: EMR 클러스터 부트스트랩 이용하기 

두번째 방법과 같이 EMR 클러스터를 이루는 인스턴스 하나하나에 들어가 설치를 진행하는 것은 굉장히 비효율적입니다.

그래서 EMR 클러스터가 생성되기 전에 두번째 방법에서와 같이 EMR 클러스터 내에 Python35, Python36을 모두 설치해두면 앞으로도 문제가 없을거에요.

이때 사용할 수 있는 방법이 'bootstrap action' 입니다. bootstrap action은 EMR 클러스터가 생성되기 전 `.sh`같은 쉘 파일등을 실행할 수 있습니다.

우선 우리가 실행해줄 `installpy3536.sh` 파일을 로컬에서 하나 만들어 줍시다.

```bash
#!/bin/bash

sudo yum install python34 -y
sudo yum install python35 -y
sudo yum install python36 -y
```

EMR 클러스터는 아마존리눅스상에서 돌아가기 때문에 `yum`을 통해 패키지를 설치할 수 있습니다. 각각 python3.4/3.5/3.6버전을 받아 설치해주는 명령어입니다.

이 파일을 s3에 올려줍시다.

우선 빈 버킷 혹은 기존 버킷에 파일을 올려주세요.

![빈 s3 버킷 만들기]({{site.static_url}}/img/dropbox/Screenshot%202017-11-28%2013.13.13.png)

파일 권한은 기본 권한 그대로 두면 됩니다. 그리고 이 파일은 AWS 외부에서 접근하지 않기 때문에 퍼블릭으로 해둘 필요는 없습니다.

![파일 업로드 완료]({{site.static_url}}/img/dropbox/Screenshot%202017-11-28%2013.13.46.png)

이제 EMR을 실행하러 가 봅시다.

앞서서는 '빠른 옵션'을 이용했지만 이제 '고급 옵션'을 이용해야 합니다.

![새 EMR 클러스터 만들기]({{site.static_url}}/img/dropbox/Screenshot%202017-11-28%2013.15.11.png)

고급 옵션에서 소프트웨어 구성을 다음과 같이 체크하고 '다음'을 눌러줍시다. 

![단계1: 소프트웨어 및 단계]({{site.static_url}}/img/dropbox/Screenshot%202017-11-28%2013.17.53.png)

다음 단계인 '하드웨어'는 기본값 혹은 필요한 만큼 설정해준 뒤 '다음'을 눌러줍시다. 여기서는 기본값으로 넣어줬습니다.

![단계2: 하드웨어]({{site.static_url}}/img/dropbox/Screenshot%202017-11-28%2013.20.01.png)

이번 단계인 '일반 클러스터 설정'이 중요합니다. 여기에서 '부트스트랩 작업'을 누르고 '사용자 지정 작업'을 선택해주세요.

![단계3: 일반 클러스터 설정]({{site.static_url}}/img/dropbox/Screenshot%202017-11-28%2013.21.20.png)

'사용자 지정 작업'을 선택한 뒤 '구성 및 추가'를 눌러주세요.

![구성 및 추가]({{site.static_url}}/img/dropbox/Screenshot%202017-11-28%2013.22.06.png)

추가를 누르면 다음과 같이 '이름', '스크립트 위치'를 찾아줘야 합니다. 이름을 `InstallPython343536`이라고 지어봅시다.

![]({{site.static_url}}/img/dropbox/Screenshot%202017-11-28%2013.23.32.png)

이제 스크립트 옆 폴더 버튼을 눌러줍시다.

![]({{site.static_url}}/img/dropbox/Screenshot%202017-11-28%2013.25.01.png)

아까 만든 `installpy3536.sh`파일이 있는 버킷에 찾아들어가 `installpy3536.sh` 파일을 선택해줍시다.

![]({{site.static_url}}/img/dropbox/Screenshot%202017-11-28%2013.25.18.png)

선택을 눌러준 뒤 '추가'를 눌러줍시다.

![]({{site.static_url}}/img/dropbox/Screenshot%202017-11-28%2013.26.51.png)

아래와 같이 '부트스트랩 작업'에 추가되었다면 '다음'을 눌러 클러스터를 만들어 줍시다.

![]({{site.static_url}}/img/dropbox/Screenshot%202017-11-28%2013.28.00.png)

이제 마지막으로 SSH접속을 위한 키 페어를 선택한 후 '클러스터 생성'을 눌러줍시다.

![]({{site.static_url}}/img/dropbox/Screenshot%202017-11-28%2013.29.15.png)

이제 생성된 EMR 클러스터에는 python3.4/3.5/3.6이 모두 설치되어있습니다. 이 버전 선택은 아래 `PYSPARK_PYTHON` 값을 설정할때 변경해 사용하면 됩니다.

### `ubuntu` 유저 만들고 `hadoop`그룹에 추가하기

python 설치를 마쳤다면 이제 `ubuntu`유저를 만들어줘야 합니다.

EMR 클러스터 마스터 노드에 작업을 추가해 줄 경우 기본적으로 작업을 실행한 유저(우분투 EC2에서 요청시 기본 유저는 `ubuntu`)의 이름으로 마스터 노드에서 요청한 유저의 홈 폴더를 찾습니다.

만약 EC2에서 EMR로 요청한다면 `ubuntu`라는 계정 이름으로 EMR 마스터 노드에서 `/home/ubuntu`라는 폴더를 찾아 이 폴더에 작업할 파이썬 파일과 의존 패키지 등을 두고 작업을 진행합니다. 하지만 EMR은 기본적으로 `hadoop`이라는 계정을 사용하고, 따라서 `ubuntu`라는 유저는 추가해줘야 합니다. 그리고 우리가 새로 만들어준 `ubuntu` 유저는 하둡에 접근할 권한이 없기 때문에 이 유저를 `hadoop`그룹에 추가해줘야 합니다.

![우분투 계정 만들고 하둡 그룹에 추가]({{site.static_url}}/img/dropbox/Screenshot%202017-11-27%2019.52.07.png)

위 사진처럼 두 명령어를 입력해 줍시다.

```shell
sudo adduser ubuntu
sudo usermod -a -G hadoop ubuntu
```

첫 명령어는 `ubuntu`라는 유저를 만들고 다음에서 `hadoop`이라는 그룹에 `ubuntu`유저를 추가합니다.

이제 우리는 EC2에서 EMR로 분산처리할 함수들을 보낼 수 있습니다.

## 마무리: 파이(pi) 계산 예제 실행하기 

한번 PySpark의 기본 예제중 하나인 `pi`(원주율) 계산을 진행해 봅시다.

공식 예제: [https://github.com/apache/spark/blob/master/examples/src/main/python/pi.py](https://github.com/apache/spark/blob/master/examples/src/main/python/pi.py)

공식 예제는 스파크와 하둡을 로컬에서 사용합니다. 하지만 우리는 EMR 클러스터에 작업을 던져줄 것이기 때문에 약간 코드를 변경해줘야 합니다.

```python
# pi.py
import sys
from random import random
from operator import add
import os

os.environ["PYSPARK_PYTHON"] = "/usr/bin/python34" # python3.5라면 /usr/bin/python35

from pyspark.sql import SparkSession

if __name__ == "__main__":
    """
        Usage: pi [partitions]
    """
    # 이 부분을 추가해주시고
    spark = SparkSession \
        .builder \
        .master("yarn") \
        .appName("PySpark") \
        .getOrCreate()
    
    # 이부분을 주석처리해주세요.
    #spark = SparkSession\
    #    .builder\
    #    .appName("PythonPi")\
    #    .getOrCreate()
    
    partitions = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    n = 100000 * partitions

    def f(_):
        x = random() * 2 - 1
        y = random() * 2 - 1
        return 1 if x ** 2 + y ** 2 <= 1 else 0

    count = spark.sparkContext.parallelize(range(1, n + 1), partitions).map(f).reduce(add)
    print("Pi is roughly %f" % (4.0 * count / n))

    spark.stop()
```

기존 코드는 `builder`를 통해 로컬에서 작업을 던져주지만 이렇게 `.master("yarn")`을 추가해주면 yarn 설정을 통해 아래 작업이 EMR 클러스터에서 동작하게 됩니다.

EC2상에서 아래 명령어로 위 파이썬 파일을 실행해 봅시다.

```
python3.4 pi.py
```

실행을 해 보면 결과가 잘 나오는 것을 볼 수 있습니다.

![pi is roughly 3.144720]({{site.static_url}}/img/dropbox/Screenshot%202017-11-28%2010.29.40.png)

> 만약 두번째/세번째 방법으로 Python3.5를 설치해주셨다면 별다른 설정 없이 `python3 pi.py`로 실행하셔도 됩니다.

### 자주 보이는 에러/경고

#### WARN yarn.Client: Same path resource

새 task를 Spark로 넘겨줄 때 마다 패키지를 찾기 때문에 나오는 에러입니다. 무시해도 됩니다.

#### Initial job has not accepted any resources

EMR 설정 중 `spark.dynamicAllocation.enabled`가 `True`일 경우 생기는 문제입니다.

위 `pi.py`파일 코드를 일부 수정해주세요.

기존에 있던 `spark` 생성하는 부분에 아래 `config` 몇줄을 추가해주세요.

```python
# 기존 코드를 지우고
# spark = SparkSession \
#     .builder \
#     .master("yarn") \
#     .appName("PySpark") \
#     .getOrCreate()

# 아래 코드로 바꿔주세요.
spark = SparkSession.builder \
    .master("yarn") \
    .appName("PySpark") \
    .config("spark.executor.memory", "512M") \
    .config("spark.yarn.am.memory", "512M") \
    .config("spark.executor.cores", 2) \
    .config("spark.executor.instances", 1) \
    .config("spark.dynamicAllocation.enabled", False) \
    .getOrCreate()
```

이때 각 config별로 설정되는 값은 여러분이 띄운 EMR에 따라 설정해줘야 합니다. 만약 여러분이 `r3.xlarge`를 선택했다면 8개의 vCPU, 30.5 GiB 메모리를 사용하기 때문에 저 설정 숫자들을 높게 잡아도 되지만, 만약 `c4.large`를 선택했다면 2개의 vCPU, 3.8 GiB 메모리를 사용하기 때문에 코드에서 설정한 CPU코어수 혹은 메모리 용량이 클러스터의 CPU개수와 메모리 용량을 초과할 경우 에러가 납니다.
