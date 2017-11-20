---
title: "깃헙 Pages에 깃북 배포하기"
date: 2017-11-20
layout: post
categories:
- Blog
- Github
published: true
image: /img/gitbook_on_github.jpg
---

## 들어가며

이번에 '나만의 웹 크롤러 만들기' 가이드 시리즈를 이 블로그에서 관리하던 중, 글이 파편화되어있는 상황이며 가이드가 유의미하게 이어진다는 느낌이 적어서 깃북을 통해 새로 가이드를 배포하기로 결정했다.

깃북의 경우 `https://gitbook.io`에서 제공하는 자체 호스팅 서비스가 있고 오픈소스로 정적 사이트를 제작하는 `Gitbook` 프로젝트도 있다.

깃북 웹 사이트의 경우 느려지는 경우도 종종 있어 좀 더 관리의 범위가 넓은 깃헙에서 깃북 레포를 통해 깃북을 관리하려고 생각했다.

## Gitbook 설치하기

우선 깃북의 경우 node.js기반이기 때문에 시스템에 `node`와 `npm`이 설치되어있어야 한다. npm은 node.js를 설치할때 보통 같이 설치된다. 글쓴날짜 기준 `9.2.0`버전이 node.js의 최신 버전이다.

> Node.js설치하기: https://nodejs.org/en/ 

시스템에 `npm`이 설치 완료되었다면 이제 아래 명령어로 `gitbook-cli`를 설치해 주자.

```shell
# 콘솔 / cmd / terminal에서 아래줄을 입력후 엔터!
npm install gitbook-cli -g
```

## Gitbook Init

깃북은 `SUMMARY.md`파일을 통해 화면 좌측의 내비게이션/목록 부분을 만든다.

한번에 폴더와 기본파일을 모두 생성하려면 아래 명령어를 입력해 주자.

```shell
# 콘솔 / cmd / terminal에서 아래줄을 입력후 엔터!
gitbook init my_gitbook
# 사용법: gitbook init 사용하려는폴더이름
```

위 명령어를 입력하면 현재 위치 아래 `my_gitbook`이라는 폴더가 생기고, 그 안에 `README.md`와 `SUMMARY.md`가 생긴다.

![](https://www.dropbox.com/s/r6vvr0uovrshf7m/%EC%8A%A4%ED%81%AC%EB%A6%B0%EC%83%B7%202017-11-20%2021.05.27.png?dl=1)

## Git Init

깃북을 배포하려면 깃헙에 레포지토리를 만들고 파일을 올려야 하기 때문에 우선 `git init`으로 현재 폴더를 `git`이 관리하도록 만들어준다.

![](https://www.dropbox.com/s/uslcq36yn5vk0io/%EC%8A%A4%ED%81%AC%EB%A6%B0%EC%83%B7%202017-11-20%2021.06.31.png?dl=1)

## `gh-pages` 브랜치 만들기

Github Pages의 경우 크게 3가지 방법으로 호스팅을 진행한다.

1. `유저이름.github.io`라는 레포의 `master`브랜치 
2. 어떤 레포든 `docs` 폴더
3. 어떤 레포든 `gh-pages` 브랜치

위 세가지가 충족되는 경우 자동으로 깃헙 페이지용도로 인식하고 `https://유저이름.github.io/레포명` 주소로 정적 호스팅을 진행해 준다.

이번에는 세번째 방법인 `gh-pages` 브랜치를 이용한다. 

> 물론 1,2,3번 모두 커스텀 도메인 사용이 가능하다.

## `publish_gitbook.sh` 만들기

`README.md`가 있는 곳 옆에 `publish_gitbook.sh`파일을 다음 내용으로 만들어 주자.

```shell
# gitbook 의존 파일을 설치하고 gitbook 빌드를 돌린다.
gitbook install && gitbook build

# github pages가 바라보는 gh-pages 브랜치를 만든다.
git checkout gh-pages

# 최신 gh-pages 브랜치 정보를 가져와 rebase를 진행한다.
git pull origin gh-pages --rebase

# gitbook build로 생긴 _book폴더 아래 모든 정보를 현재 위치로 가져온다.
cp -R _book/* .

# node_modules폴더와 _book폴더를 지워준다.
git clean -fx node_modules
git clean -fx _book

# NOQA
git add .

# 커밋커밋!
git commit -a -m "Update docs"

# gh-pages 브랜치에 PUSH!
git push origin gh-pages

# 다시 master 브랜치로 돌아온다.
git checkout master
```

위와 같이 `publish_gitbook.sh`파일을 만들어 주면, 앞으로 작업을 끝낼때마다 `./publish_gitbook.sh`라는 명령어로 한번에 깃헙에 작업한 결과물을 빌드해 올릴 수 있다.

## SUMMARY.md 관리하기 

깃북이 파일을 관리하는 것은 폴더별 관리라기보다는 `SUMMARY.md`파일 내의 정보를 기반으로 URL을 만들고 글의 순서와 목차를 관리한다.

보통 카테고리/챕터별로 폴더를 만들어 관리하는 방법을 사용하는 것 같은데, [나만의 웹 크롤러 만들기 깃북](https://beomi.github.io/gb-crawling/)의 경우 아래와 같은 형태를 사용하고 있다.

```markdown
# Summary

- [나만의 웹 크롤러 만들기 시리즈](README.md)
    - [requests와 BeautifulSoup으로 웹 크롤러 만들기](posts/2017-01-20-HowToMakeWebCrawler.md)
    - [Session을 이용해 로그인하기](posts/2017-01-20-HowToMakeWebCrawler-With-Login.md)
    - [Selenium으로 무적 크롤러 만들기](posts/2017-02-27-HowToMakeWebCrawler-With-Selenium.md)
    - [Django로 크롤링한 데이터 저장하기](posts/2017-03-01-HowToMakeWebCrawler-Save-with-Django.md)
    - [웹페이지 업데이트를 알려주는 Telegram 봇](posts/2017-04-20-HowToMakeWebCrawler-Notice-with-Telegram.md)
    - [N배빠른 크롤링, multiprocessing](posts/2017-07-05-HowToMakeWebCrawler-with-Multiprocess.md)
    - [Headless 크롬으로 크롤링하기](posts/2017-09-28-HowToMakeWebCrawler-Headless-Chrome.md)

- Tips
    - [Selenium Implicitly wait vs Explicitly wait](posts/2017-10-29-HowToMakeWebCrawler-ImplicitWait-vs-ExplicitWait.md)
```

위와 같이 `-`를 사용해 글과 카테고리를 구별하고 스페이스를 통해 제목과 링크를 마크다운 문법으로 걸어주면 깃북이 이 파일을 읽고 각각의 파일을 `html`파일로 만들어준다.

## 유의할점

깃북에서 `![](이미지링크)`와 같은 방식을 사용하면 '/'로 시작하는 절대경로 URL을 상대경로인 '../'로 변환해버리는 문제가 있다.

따라서 `SUMMARY.md`파일과 같은 위치에 `book.json`파일을 만들어주고 전역 변수를 사용할 수 있다.

## `book.json` 관리하기 

깃북은 `book.json`파일이 세팅 파일이다. 플러그인을 넣고, 지우고, 전역 변수 등을 설정할 수도 있다.

다음은 Google Analytics 플러그인을 '넣고' 소셜 공유 아이콘을 '빼고', 'BASE_URL'에 블로그 절대경로를 만들기 위해 URL을 등록해둔 부분이다.

> 토큰은 Google Analytics에서 받아서 넣어주면 된다.

```json
{
    "plugins": ["ga", "-sharing"],
    "pluginsConfig": {
        "ga": {
            "token": "UA-12341234-1"
        }
    },
    "variables": {
        "BASE_URL": "https://beomi.github.io"
    }
}
```
