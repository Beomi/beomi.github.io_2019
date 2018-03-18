---
title: "GPU EC2 스팟 인스턴스에 Cuda/cuDNN와 Tensorflow/PyTorch/Jupyter Notebook 세팅하기"
date: 2018-03-18
layout: post
categories:
- python
- aws
published: true
image: https://d1sr4ybm5bj1wl.cloudfront.net/img/Create_GPU_spot_EC2_for_ML.png
---

## 들어가며

Tensorflow나 PyTorch등을 사용하며 딥러닝 모델을 만들고 학습을 시킬 때 GPU를 사용하면 CPU만 사용하는 것에 비해 몇배~몇십배에 달하는 속도향상을 얻을 수 있다는 것은 누구나 알고 있습니다.

그래서 비싼 GPU를 사용하고 낯선 리눅스 환경을 이용하기도 합니다. 하지만 실제로 GPU, 특히 Cuda를 이용한 GPU가속을 세팅하고 cuDNN등을 통해 각 머신러닝 라이브러리에서 속도를 향상시키려고 할 때는 항상 무언가 문제가 발생합니다. 물론 Floydhub혹은 AWS SageMaker와 같이 이미 GPU 가속 환경이 마련되어있는 경우는 필요가 없지만, GPU 인스턴스의 시간당 요금 자체가 상당히 높습니다. 

> `k80` GPU를 제공하는 경우 시간당 약 1~2달러의 비용이 발생합니다.

조금이라도 저렴하게 GPU를 사용하고, 한번 설정된 GPU 인스턴스를 그대로 유지하기 위해 스팟 인스턴스를 사용해 봅시다. 

> 오늘자(2018.03.18)기준 p2.xlarge(CPU 4 Core / RAM 60GB / GPU k80) 스팟 인스턴스 가격은 시간당 0.4395달러입니다. (원래 1.4650달러로, 70% 저렴하게 사용 가능합니다.)

## 만들기!

이번 글에서는 Ubuntu 16.04 LTS 위에 아래 패키지와 라이브러리들을 설치하는 내용을 다룹니다.

- Python 3.5
- Tensorflow 1.6.0 (GPU)
- PyTorch 0.3.1 (GPU)
- CUDA 9.0
- cuDNN 7.0.5 (for CUDA 9.0)

### 우분투 업데이트

우선 EC2를 처음 띄웠으니 패키지들을 모두 최신버전으로 업데이트 해 줍시다. 만약 작업 중 Dependencty 패키지의 버전을 업데이트 할 것이냐는 질문이 나오면 '로컬 버전 사용하기'를 눌러줍시다.

![sudo apt-get](/img/dropbox/2018-03-18%2017.06.44.png)

위 스크린샷과 같이 아래 명령어를 입력하고 잠시 기다리면 우분투 패키지가 모두 업데이트됩니다.

```sh
sudo apt-get update && sudo apt-get upgrade -y
```

### pip3 설치하기

Ubuntu16.04에는 Python3이 기본적으로 설치되어있지만 pip3은 설치되어있지 않습니다. 아래 명령어로 설치해 사용해봅시다.

```
sudo apt-get install -y python3-pip
```

### CUDA GPU 확인하기 (Optional)

현재 ubuntu에 붙어있는 GPU가 있는지 확인하려면 아래 명령어를 이용해 확인해 볼 수 있습니다. 물론 AWS p2 인스턴스로 띄우셨다면 당연히 CUDA를 지원하는 그래픽 카드가 붙어 있습니다 :)

```sh
lspci | grep -i nvidia
```

만약 아래 스크린샷과 같이 GPU가 나온다면 이 환경에서는 Cuda 가속을 이용할 수 있습니다!

![CUDA 지원GPU 확인하기](/img/dropbox/2018-03-18%2017.29.33.png)

### CUDA Toolkit 9.0 설치하기

CUDA를 사용하기 위해서 CUDA Toolkit 9.0을 설치해야 합니다. 아래 명령어를 하나씩 입력해 실행해주세요.

```sh
# Nvidia Debian package Repo 등록 패키지 다운로드
wget http://developer.download.nvidia.com/compute/cuda/repos/ubuntu1604/x86_64/cuda-repo-ubuntu1604_9.0.176-1_amd64.deb
# Nvidia APT 키 등록하기
sudo apt-key adv --fetch-keys http://developer.download.nvidia.com/compute/cuda/repos/ubuntu1604/x86_64/7fa2af80.pub
# Nvidia Repo APT 등록하기
sudo dpkg -i cuda-repo-ubuntu1604_9.0.176-1_amd64.deb
# Cuda 9.0 설치하기
sudo apt-get update
sudo apt-get install cuda-9-0
# Cuda ToolKit 설치하기 (nvcc)
sudo apt install nvidia-cuda-toolkit
``` 

한줄씩 입력하면 약간의 시간이 지난 뒤 CUDA 9.0 설치가 끝납니다. 그리고 작업 중 추가적으로 그래픽카드 드라이버 최신버전도 함께 설치되기 때문에 그래픽 드라이버는 따로 설치하지 않아도 됩니다.

> 만약 무언가 문제가 발생한다면 [Nvidia CUDA Toolkit 9.0 Downloads](https://developer.nvidia.com/cuda-90-download-archive?target_os=Linux&target_arch=x86_64&target_distro=Ubuntu&target_version=1604&target_type=debnetwork)를 참고하세요.

### cuDNN 7.0.5 설치하기

cuDNN을 사용하기 위해서는 Nvidia Developer Membership에 가입해야 합니다. 가입은 nvidia 개발자 사이트에서 진행할 수 있으며, [cuDNN Download Page](https://developer.nvidia.com/rdp/cudnn-download)에서 바로 가입하실 수 있습니다.

이미 계정이 있다면 [cuDNN Download Page](https://developer.nvidia.com/rdp/cudnn-download)에서 cuDNN 7.0.5 for CUDA 9.0을 클릭해 주세요.

![cuDNN 7.0.5 클릭](/img/dropbox/2018-03-18%2017.45.59.png)

그리고 아래 스크린샷처럼 cuDNN v7.0.5 Library for Linux를 클릭해 주시면 파일이 다운로드 됩니다.

![클릭 후](/img/dropbox/2018-03-18%2017.47.46.png)

하지만 우리는 cuDNN을 서버에서 사용할 것이기 떄문에 해당 링크 주소를 복사해 사용해야 합니다.

> 만약 단순히 링크를 복사해 사용하면 403 Forbidden 에러가 뜹니다.

![cuDNN download url 복사하기](/img/dropbox/2018-03-18%2017.52.11.png)

따라서 위와 같이 파일의 다운로드 경로를 복사해옵시다. 경로를 복사하면 아래와 같이 복잡한 문자열이 붙은 URL이 됩니다.

```sh
# 예시 URL
http://developer.download.nvidia.com/compute/machine-learning/cudnn/secure/v7.0.5/prod/9.0_20171129/cudnn-9.0-linux-x64-v7.tgz?t8V0cLo2oAM-UT86ONPbFAF6Gae61AEK5a9KdkSzG9M5slquBxMffldmWEC8cNHOKiCpQWJx9WXgt6mKaFnDpq_zGVxVGTNyajaGQv4nQef2W0CBpe8Y9NKRycBGUF8k
```

이제 얻어온 URL을 이용해 cuDNN을 서버에 다운로드 받아줍시다. 아래 명령어로 위 링크를 다운로드받아줍시다. 

```sh
wget 위에서_받아온_URL
```

다운로드가 완료되면 아래 명령어를 차례대로 입력해 주세요.

```sh
mv cudnn* cudnn.tgz
tar -xzvf cudnn.tgz
sudo cp cuda/include/cudnn.h /usr/local/cuda/include
sudo cp cuda/lib64/libcudnn* /usr/local/cuda/lib64
sudo chmod a+r /usr/local/cuda/include/cudnn.h /usr/local/cuda/lib64/libcudnn*
```

이제 Tensorflow와 PyTorch를 설치해줍시다.

### Tensorflow-GPU 설치하기 

Tensorflow의 GPU버전도 pip3으로 쉽게 설치할 수 있습니다. 아래 명령어를 입력해 Tensorflow를 설치해주세요.

```sh
pip3 install tensorflow-gpu
```

### PyTorch-GPU 설치하기

PyTorch 역시 pip3으로 설치할 수 있습니다. 아래 명령어를 통해 PyTorch를 설치해주세요.

```sh
pip3 install http://download.pytorch.org/whl/cu90/torch-0.3.1-cp35-cp35m-linux_x86_64.whl 
pip3 install torchvision --user
```

### Jupyter Notebook 설치 및 설정

SSH만으로 작업하는 대신 Jupyter Notebook 서버를 띄워 이용해봅시다.

#### 설치 

아래 명령어로 Jupyter Notebook을 설치해주세요.

```sh
pip3 install jupyter --user
```

#### 서버 설정

Jupyter를 띄우고 패스워드로 접속하기 위해서는 아래 스크린샷처럼 설정파일을 만든 뒤 패스워드를 생성해야 합니다. 

![](/img/dropbox/2018-03-18%2018.30.44.png)

설정 파일 생성은 다음 명령어로 쉽게 만들 수 있습니다.

```sh
jupyter notebook --generate-config
```

그리고 원격 서버에서 접속할 때는 Jupyter Notebook의 토큰을 확인하기 어렵기 때문에 토큰 대신 지정한 패스워드를 이용하도록 바꿔줍시다.

먼저 패스워드를 생성해줍니다.

```sh
jupyter notebook password
```

Jupyter Notebook은 기본적으로 `localhost`에서의 요청만을 받습니다. 즉, 원격 브라우저에서의 접속이 기본적으로 되어있습니다. 따라서 이 설정값을 바꿔줍시다.

```sh
# localhost가 아닌 모든 ip를 듣기 
sed -i 's/#c.NotebookApp.ip = '"'"'localhost'"'"'/c.NotebookApp.ip = '"'"'*'"'"'/' ~/.jupyter/jupyter_notebook_config.py
# 자동으로 브라우저 켜는 기능 끄기
sed -i 's/#c.NotebookApp.open_browser = True/c.NotebookApp.open_browser = False/' ~/.jupyter/jupyter_notebook_config.py
```

#### Jupyter Notebook 데몬 서비스화 

이제 Jupyter Notebook 설정이 끝났습니다. 하지만 매번 서버를 켤 때마다 터미널에서 Jupyter Notebook을 켜고 작업하기는 귀찮으니 Deamon화를 해 봅시다.

```sh
sudo mkdir /usr/lib/systemd/system
sudo touch /usr/lib/systemd/system/jupyter.service
```

그리고 `vi` 등 편집기를 이용해 아래 내용을 넣어줍시다.

```
[Unit]
Description=Jupyter Notebook

[Service]
Type=simple
PIDFile=/run/jupyter.pid
ExecStart=/home/ubuntu/.local/bin/jupyter-notebook --config=/home/ubuntu/.jupyter/jupyter_notebook_config.py
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

그리고 아래 네가지 명령어를 입력해주시면 Jupyter Notebook이 서비스로 띄워진 것을 확인할 수 있습니다.

```sh
sudo systemctl enable jupyter.service
sudo systemctl daemon-reload
sudo systemctl restart jupyter.service
systemctl -a | grep jupyter
```

### EC2 접속해 확인하기

이제 해당 EC2로 들어가봅시다. 처음에 비밀번호를 입력하라고 뜨면 위에서 Jupyter Notebook 패스워드로 설정해준 값을 넣어 들어가봅시다.

GPU 가속까지 설정이 잘 된 것을 볼 수 있습니다. Yeah!

![](/img/dropbox/2018-03-18%2019.07.06.png)

> 이렇게 만든 EC2에 `8888` 포트를 Security Group에서 열어줘야 접근이 가능합니다. 혹시 접근이 되지 않는다면 Security Group을 확인하세요! 기본적으로 부여되는 Security Group은 `default`입니다.

## 커스텀 AMI 만들기

EC2를 새로 생성할 때는 커스텀 AMI를 사용해 띄울 수 있습니다. 커스텀 AMI는 EC2 볼륨 스냅샷을 기반으로 생성됩니다. 우리가 사용할 GPU 가속된 딥러닝 환경이 모두 세팅되었으니 이제 이 인스턴스의 볼륨을 스냅샷으로 찍어 새로 만드는 볼륨은 항상 이 스냅샷에서 시작하도록 만들어줍시다.

![](/img/dropbox/2018-03-18%2019.10.28.png)

아래와 같이 스냅샷을 생성해 줍시다.

![](/img/dropbox/2018-03-18%2019.11.04.png)

스냅샷 생성이 끝나면 AMI를 만들어줘야 합니다. 만들어진 스냅샷에 우측클릭을 하고 '이미지 생성'을 눌러주세요.

![](/img/dropbox/2018-03-18%2021.17.02.png)

다음과 같이 '이름'을 적어주고, '가상화 유형'은 `하드웨어 보조 가상화` 혹은 `hvm`을 선택하신 뒤 '생성'을 눌러주세요.

![](/img/dropbox/2018-03-18%2021.19.14.png)

> 주의: 가상화 유형에서 반가상화 (PV)를 선택하시면 EC2 인스턴스를 띄우실 수 없습니다.

시간이 조금 소요된 후 AMI가 성공적으로 생성되면 아래와 같이 '내 AMI' 목록에 방금 만들어준 이미지가 나타납니다.

![](/img/dropbox/2018-03-18%2021.28.40.png)

이렇게 생성된 AMI는 다음과 같이 새로운 온디맨드 EC2를 실행하거나 혹은 스팟 인스턴스를 요청하는데 사용할 수 있습니다.

![](/img/dropbox/2018-03-18%2021.29.55.png)

## 맺으며

이번 글에서는 AWS의 스팟 인스턴스를 통해 저렴한 (1/3도 안되는) 가격에 딥러닝을 위한 GPU 인스턴스를 띄우고 CUDA와 cuDNN, 그리고 Tensorflow와 PyTorch를 GPU 가속이 가능한 상태로 만드는 과정을 진행했습니다.

마지막 AMI를 만드는 과정까지 진행하시면 필요할 때 마다 온디맨드 혹은 스팟 요청을 통해 새로운 EC2를 켜더라도 이미 모델 개발을 위한 환경이 구축된 상태로 작업을 진행할 수 있습니다.

다만 스팟 요청은 EC2가 생성될 경우 매번 새로운 EBS(스토리지)를 생성하기 때문에 저 상태에서 사용했던 데이터가 유실됩니다. 따라서 재사용하고자 하는 데이터의 종류에 따라 다른 선택을 해야 합니다.

- 자주 사용하는 패키지를 모두 깔아두고 싶으신 경우:
  앞서 진행했던 '스냅샷 생성' => 'AMI 생성' 과정을 진행하기 전, 미리 패키지를 모두 깔아 두신 뒤 스냅샷과 AMI를 생성하시면 됩니다.
  사용한 데이터셋과 모델 파일 등은 유실되지만 패키지를 재설치할필요는 없습니다.
- 데이터도 보존하고 싶은 경우:
  현재 EC2를 만들 때 기존의 볼륨을 루트 디바이스로 붙이지는 못합니다. 또한 스팟 인스턴스에는 남는 볼륨(EBS)도 붙이지 못하기 때문에 이런 경우에는 스팟 인스턴스 대신 다른 전략을 사용해야 합니다. 
  즉, 일반 온디맨드 EC2로 켜야 합니다. 다만 온디맨드 인스턴스에는 CloudWatch를 이용해 n분 이상 idle 상태인 경우 인스턴스를 중지시켜 요금을 줄이는 방법이 있습니다.
- 데이터도 보존하고싶고 스팟인스턴스도 사용하고 싶은 경우:
  매 종료 전 AMI를 새로 생성하고 종료하면 되지만, s3 공간을 낭비하고 이 시간 자체가 비용이 되기 때문에 추천하지 않습니다 :(
