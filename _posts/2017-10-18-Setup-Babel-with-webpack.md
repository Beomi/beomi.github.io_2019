---
title: "Webpack과 Babel로 최신 JavaScript 웹프론트 개발환경 만들기"
date: 2017-10-18
layout: post
categories:
- JavaScript
- Webpack
published: true
image: /img/webpack-with-babel.jpg
---

> 이번 포스팅에서는 nodejs8.5.0, npm5.3.0 버전을 사용합니다.

## 들어가며

파이썬의 버전 2와 3이 다른 것은 누구나 알고 2017년인 오늘은 대부분 Python3버전을 이용해 프로젝트를 진행합니다. 하지만 자바스크립트에 버전이 있고 새로운 기능이 나온다 하더라도 이 기능을 바로 사용하는 경우는 드뭅니다. 물론 `node.js`를 이용한다면 자바스크립트의 새로운 버전의 기능을 바로바로 이용해볼 수 있지만 프론트엔드 웹 개발을 할 경우 새로 만들어진 자바스크립트의 기능을 사용하는 것은 상당히 어렵습니다.

```javascript
// 이런 문법은 사용하지 못합니다.
const hello = 'world'
const printHelloWorld = (e) => {
	console.log(e)
}
printHelloWorld(hello)
```

가장 큰 차이는 실행 환경의 문제인데요, 우리가 자주 사용하는 크롬브라우저의 경우에는 자동업데이트 기능이 내장되어있어 일반 사용자가 크롬브라우저를 실행만 해도 최신 버전을 이용하지만, 인터넷 익스플로러나 사파리와 같은 경우에는 많은 사용자가 OS에 설치되어있던 버전 그대로를 이용합니다. 물론 이렇게 사용하는 것도 심각한 문제를 가져오지는 않지만, 구형 브라우저들은 새로운 자바스크립트를 이해하지 못하기 때문에 이 브라우저를 사용하는 사용자들은 새로운 자바스크립트로 개발된 웹 사이트를 접속할 경우 전혀 다르게 혹은 완전히 동작하지 않는 페이지를 볼 수 있기 때문에 많은 일반 사용자를 대상으로 하는 서비스의 경우 새 버전의 자바스크립트를 사용해 개발한다는 것이 상당히 모험적인 성향이 강합니다.

![es2017](/img/es2017.png)

글쓴 시점인 2017년 10월 최신 자바스크립트 버전은 `ES2017`로 `ES8`이라 불리는 버전입니다. 하지만 이건 정말 최신 버전의 자바스크립트이고, 중요한 변화가 등장한 버전이 2015년도에 발표된 `ES2015`, 다른 말로는 `ES6`이라고 불리는 자바스크립트입니다. 하지만 인터넷익스플로러를 포함한 대부분의 브라우저들이 지원하는 자바스크립트의 버전은 `ES5`로 이보다 한단계 낮은 버전을 사용합니다. 따라서 우리는 `ES6`혹은 그 이상 버전의 자바스크립트 코드들을 `ES5`의 아래 버전 자바스크립트로 변환해 사용하는 방법을 사용할 수 있습니다.

## Babel

여기서 바로 Babel이 등장합니다. Babel은 최신 자바스크립트를 `ES5`버전에서도 돌아갈 수 있도록 변환(Transpiling)해줍니다. 우리가 자바스크립트 최신 버전의 멋진 기능을 이용하는 동안, Babel이 다른 브라우저에서도 돌아갈 수 있도록 처리를 모두 해주는 것이죠!

> 물론, Babel이 마법의 요술도구처럼 모든 최신 기능을 변환해주지는 못합니다. 하지만 아래 사진처럼 다양한 브라우저에 따라 최신 JavaScript문법 중 어떠 부분까지가 실행 가능한 범위인지 알려줍니다. ![Babel coverage](/img/babel_coverage.png)

## Webpack

`ES6`에서 새로 등장한 것 중 유용한 문법이 바로 `import .. from ..`구문입니다. 다른 언어에서의 `import`와 유사하게 경로(상대경로 혹은 절대경로)에서 js파일을 불러오는 방식으로 동작합니다.

예를들어 어떤 폴더 안에 `Profile.js`와 `index.js`파일이 있다고 생각해 봅시다.

```javascript
// Profile.js
export class Profile {
	constructor(name, email) {
		this.name = name
		this.email = email
	}

	hello() {
		return `Hello, ${this.name}(${this.email})`
	}
}
```

하는일이라고는 `name`, `email`을 받는 것, 그리고 `hello`하는 함수밖에 없지만 우선 `Profile`이라는 class를 하나 만들었습니다.

여기서 `Profile` 클래스 앞에 `export`를 해 주었는데, `export`를 해 줘야 다른 파일에서 `import`가 가능합니다.

자, 아래와 같이 index.js파일을 하나 만들어 봅시다.

```javascript
// index.js
import { Profile } from './Profile'

const pf = new Profile('Beomi', 'jun@beomi.net')
console.log(pf.hello())
```

이 파일은 현재 경로의 `Profile.js`파일 중 `Profile` 클래스를 import해와 새로운 인스턴스를 만들어 사용합니다.

하지만 안타깝게도 이 `index.js`파일은 실행되지 않습니다. 아직 `webpack`으로 처리를 해주지 않았기 때문이죠!

## webpack-dev-server

webpack은 파일을 모아 하나의 js파일로 만들어줍니다.(보통 `bundle.js`라는 이름을 많이 씁니다.) 하지만 실제 개발중 js파일을 수정할 때마다 Webpack을 실행해 번들작업을 해준다면 시간도 많이 걸리고 매우 귀찮습니다. 이를 보완해 주는 패키지가 바로 `webpack-dev-server` 인데요, 이 패키지를 사용하면 여러분이 실제 빌드를 해 `bundle.js`파일을 만들지 않아도 메모리 상에 가상의 `bundle.js`파일을 만들어 여러분이 웹 사이트를 띄울때 자동으로 번들된 js파일을 띄워줍니다. 그리고 소스가 수정될 때 마다 업데이트된(번들링된) `bundle.js`파일로 띄워주고 화면도 새로고침해줍니다!

> NOTE: webpack-dev-server는 `build`를 자동으로 해주는 것은 아닙니다. 단지 미리 지정해둔 경로로 접근할 경우 (실제로는 파일이 없지만) `bundle.js`파일이 있는 것처럼 파일을 보내주는 역할을 맡습니다. 개발이 끝나고 실제 서버에 배포할때는 이 패키지 대신 실제 webpack을 통해 빌드 작업을 거친 최종 결과물을 서버에 올려야 합니다.

## 설치하기

우선 `npm`프로젝트를 생성해야 합니다. `index.js`파일을 만든 곳(어떤 폴더) 안에서 다음 명령어로 "이 폴더는 npm프로젝트를 이용하는 프로젝트다" 라는걸 알려주세요.

```bash
# -y 인자를 붙이면 모든 설정이 기본값으로 됩니다.
npm init -y
```

![](/img/dropbox/Screenshot%202017-10-19%2010.23.18.png?dl=1)

이 명령어를 치면 폴더 안에 `package.json`파일이 생성되었을 거에요.

![](/img/dropbox/Screenshot%202017-10-19%2010.23.52.png?dl=1)

이제 다음 명령어로 Babel과 webpack등을 설치해 봅시다.

```bash
# babel과 webpack은 개발환경에서 필요하기 때문에 --save-dev로 사용합니다.
npm install --save-dev babel-loader babel-core babel-preset-env
npm install --save-dev webpack webpack-dev-server
```

![](/img/dropbox/Screenshot%202017-10-19%2010.25.30.png?dl=1)

`babel-loader`는 `webpack`이 .js 파일들에 대해 babel을 실행하도록 만들어주고, `babel-core`는 babel이 실제 동작하는 코드이고, `babel-preset-env`는 babel이 동작할 때 지원범위가 어느정도까지 되어야 하는지에 대해 지정하도록 만들어주는 패키지입니다.

이렇게 설치를 진행하고 나면 Babel과 Webpack을 사용할 준비를 마친셈입니다.

> NOTE: `package.json`뿐 아니라 `package-lock.json`파일도 함께 생길수 있습니다. 이 파일은 npm패키지들이 각각 수많은 의존성을 가지고 있기 때문에 의존성 패키지들을 다운받는 URL을 미리 모아둬 다른 컴퓨터에서 `package.json`을 통해 `npm install`로 패키지들을 설치시 훨씬 빠른 속도로 패키지를 받을 수 있도록 도와줍니다.

이제 설정파일 몇개를 만들고 수정해줘야 해요.

## 설정파일 건드리기

### package.json

`package.json`파일은 파이썬 pip의 `requirements.txt`처럼 패키지버전 관리만 해주는 것이 아니라 npm와 결합해 특정 명령어를 실행하거나 npm 프로젝트의 환경을 담는 파일입니다.

```bash
npm run 명령어이름
```

위와 같은 명령어를 사용할 수 있도록 만들어 주기도 합니다.

현재 `package.json`파일은 아래와 같은 형태로 되어있을거에요.

```json
{
  "name": "npm_blog",
  "version": "1.0.0",
  "description": "",
  "main": "index.js",
  "scripts": {
    "test": "echo \"Error: no test specified\" && exit 1"
  },
  "keywords": [],
  "author": "",
  "license": "ISC",
  "devDependencies": {
    "babel-core": "^6.26.0",
    "babel-loader": "^7.1.2",
    "babel-preset-env": "^1.6.1",
    "webpack": "^3.8.1",
	"webpack-dev-server": "^2.9.2"
  }
}
```

이제 `package.json`파일을 열어 `"scripts"`부분을 다음과 같이 `build`와 `devserver`명령어를 추가해 줍시다.

```json
{
  "name": "npm_blog",
  "version": "1.0.0",
  "description": "",
  "main": "index.js",
  "scripts": {
    "build": "webpack",
    "devserver": "webpack-dev-server --open --progress"
  },
  "keywords": [],
  "author": "",
  "license": "ISC",
  "devDependencies": {
    "babel-core": "^6.26.0",
    "babel-loader": "^7.1.2",
    "babel-preset-env": "^1.6.1",
    "webpack": "^3.8.1",
    "webpack-dev-server": "^2.9.2"
  }
}
```

이제 여러분이 `npm run build`를 할 때는 `webpack`이 실행되고, `npm run devserver`를 할 때는 개발용 서버가 띄워질거에요.

### webpack.config.js

`webpack.config.js` 파일은 앞서 설치해준 `webpack`을 실행 시 어떤 옵션을 사용할지 지정해주는 js파일입니다.

우리 프로젝트 폴더에는 아직 `webpack.config.js` 파일이 없을거에요. `package.json`와 같은 위치에 `webpack.config.js`파일을 새로 만들어 아래 내용으로 채워줍시다.

```javascript
const webpack = require('webpack');
const path = require('path');

module.exports = {
    entry: './index.js',
    output: {
        path: path.resolve(__dirname, 'dist'),
        publicPath: '/dist/',
        filename: 'bundle.js'
    },
    module: {
        rules: [
            {
                test: /\.js$/,
                include: path.join(__dirname),
                exclude: /(node_modules)|(dist)/,
                use: {
                    loader: 'babel-loader',
                    options: {
                        presets: ['env']
                    }
                }
            }
        ]
    }
};
```

위 파일은 `entry`에 현재 위치의 `index.js`파일을 들어가 모든 `import`를 찾아오고, `module -> rules -> include`에 있는 `.js`로 된 모든 파일을 babel로 처리해줍니다.(`exclue`에 있는 부분인 `node_modules`폴더와 `dist`폴더는 제외합니다.)

### index.html

사실 우리는 아직 번들링된 js파일을 보여줄 HTML파일이 없습니다! 우선 `bundle.js`를 보여주기만 할 단순한 HTML파일을 하나 만들어 봅시다.(`index.js`와 같은 위치)

```html
<!-- index.html -->
<!DOCTYPE html>
<html>
<head>
	<title>NPM Webpack</title>
</head>
<body>
Webpack용 HTML
<script type="text/javascript" src="/dist/bundle.js"></script>
</body>
</html>
```

webpack을 사용하지 않았다면 HTML파일 아래 `script`태그의 src에 index.js를 넣어야 하지만, 우리는 webpack과 webpack-dev-server를 사용하기때문에 번들링된 파일의 위치인 `/dist/bundle.js`을 넣어줍니다.

## devserver 띄우기

자, 이제 아래 명령어로 devserver를 띄워봅시다!

```bash
npm run devserver
```

브라우저의 개발자 도구를 열어보면 아래와 같이 로그가 잘 찍힌걸 확인해 볼 수 있을거에요.

![](/img/dropbox/Screenshot%202017-10-19%2010.56.16.png?dl=1)

이제 여러분이 `index.js`파일이나 `Profile.js`등을 수정하면 곧바로 새로고침되고 새로운 `bundle.js`를 라이브로 불러올거에요.

## 배포용으로 만들기

여러분이 프로젝트 개발을 끝내고 실제 서버에 배포할 때는 devserver가 아니라 실제로 번들링된 파일인 `bundle.js`를 만들어야 합니다.

아래 명령어로 현재 위치의 `dist`폴더 안에 `bundle.js` 파일을 만들어 줍시다.

```bash
npm run build
```

![](/img/dropbox/Screenshot%202017-10-19%2010.59.35.png?dl=1)

위와 같이 나온다면 성공적으로 webpack이 마쳐진 것이랍니다! 그리고 여러분 프로젝트 폴더 안에 `dist`폴더가 생기고 그 안에 `bundle.js`파일이 생겼을 거에요.

![](/img/dropbox/Screenshot%202017-10-19%2011.00.42.png?dl=1)

이제 여러분은 `index.html`파일과 `dist`폴더를 묶어 서버에 올리면 페이지가 잘 동작하는것을 확인할 수 있을거에요!
