---
title: "TreeShaking으로 webpack 번들 결과 용량 줄이기"
date: 2017-11-29
layout: post
categories:
- JavaScript
published: true
image: /img/treeshaking.png
---

> 이번 글은 webpack을 사용하고 있다고 가정합니다. 만약 webpack이 뭔지 아직 모르시거나 설치하지 않으셨다면 [Webpack과 Babel로 최신 JavaScript 웹프론트 개발환경 만들기](/2017/10/18/Setup-Babel-with-webpack/)를 먼저 읽고 따라가보세요.

## 들어가며

웹 프론트 개발을 할 때 npm과 webpack을 통해 `bundle.js`와 같은 번들링된 js파일 하나로 만들어 싱글 페이지 앱을 만드는 경우가 많습니다.

우리가 사용하는 패키지들을 찾아 간단하게 묶고 babel을 통해 하위버전 브라우저에서도 돌아가도록 만들어주는 작업은 마치 마법과 같이 편리합니다.

하지만 이 마법같은 번들링에도 심각한 문제점이 있습니다. 바로 용량이 어마어마해진다는 것이죠.

![](/img/tree-shaking-before.png)

아무런 처리를 하지 않고 webpack으로 빌드를 할 때의 용량은 스크린샷에 나온 것처럼 무려 1.61MB됩니다.

사실 아직 `lodash`, `bootstrap3`, `axios`와 같은 아주 기본적인 라이브러리들만 넣었음에도 다음과 같이 어마어마하게 무거운 js파일이 생성됩니다.

이제 이 파일을 1/3 크기로 줄여봅시다.

## uglifyjs-webpack-plugin

webpack과 함께 파일의 용량을 줄여주는 도구인 `uglifyjs`를 사용해봅시다.

우선 다음 명령어로 `uglifyjs-webpack-plugin`를 설치해주세요.

```shell
npm install --save-dev uglifyjs-webpack-plugin
```

## webpack 실행시 자동으로 용량줄이기

여러분이 webpack을 사용하고 있다면 아마 다음과 같은 `webpack.config.js`파일을 만들어 사용하고 있을거에요. (세부적인 설정은 다를 수 있어요.)

```js
const webpack = require('webpack');
const path = require('path');

module.exports = {
    entry: './src/js/index.js',
    output: {
        path: path.resolve(__dirname, 'dist'),
        publicPath: '/dist/',
        filename: 'bundle.js'
    },
    module: {
        rules: [
            {
                test: /\.js$/,
                include: path.join(__dirname, 'src'),
                exclude: /(node_modules)|(dist)/,
                use: {
                    loader: 'babel-loader',
                    options: {
                        presets: [
                            ["env"]
                        ]
                    }
                }
            }
        ]
    }
}
```

위 설정은 단순히 `src`파일 안의 js들을 `dist`폴더 안의 `bundle.js`파일로 묶어주고 있습니다.

이제 여기에서 몇줄만 추가해 주면 됩니다.

```js
const webpack = require('webpack');
const path = require('path');
// 1. UglifyJSPlugin을 가져오세요.
const UglifyJSPlugin = require('uglifyjs-webpack-plugin');

module.exports = {
    entry: './src/js/index.js',
    output: {
        path: path.resolve(__dirname, 'dist'),
        publicPath: '/dist/',
        filename: 'bundle.js'
    },
    module: {
        rules: [
            {
                test: /\.js$/,
                include: path.join(__dirname, 'src'),
                exclude: /(node_modules)|(dist)/,
                use: {
                    loader: 'babel-loader',
                    options: {
                        presets: [
                            ["env", {
                                "targets": {
                                    "browsers": ["last 2 versions", "safari >= 7"]
                                }
                            }]
                        ]
                    }
                }
            }
        ]
    },
    // 2. plugins를 새로 만들고, new UglifyJsPlugin() 을 통해
    // UglifyJS를 빌드 과정에 합쳐주세요.
    plugins: [
        new UglifyJsPlugin()
    ]
}
```

이제 빌드를 실행해보면 아래 스크린샷과 같이 `bundle.js`파일의 용량이 획기적으로 줄어든 것을 볼 수 있습니다. 용량이 1.6MB에서 667KB로 1/3정도로 줄어든 것을 볼 수 있습니다. 간단하죠?

![](/img/tree-shaking-after.png)

하지만 여기에는 작은 함정이 있습니다. 바로 `time`, 즉 빌드시마다 걸리는 시간도 그에따라 늘어난 것인데요, 만약 여러분이 `webpack-dev-server`와 같이 실시간으로 파일을 감시하며 변화 발생시마다 빌드하는 방식을 사용하고 있다면 코드 한줄, 띄어쓰기 하나 수정한 정도로 무려 12초에 달하는 빌드 시간을 기다려야 합니다. (treeshaking 하기 전에는 3초정도밖에 걸리지 않았습니다.)

그래서 항상 treeshaking을 해주는 대신 빌드작업, 즉 서버에 실제로 배포하기 위해 `bundle.js`파일을 생성할 때만 treeshaking을 해주면 개발도 빠르고 실제 배포시에도 빠르게 작업이 가능합니다.

## 빌드할때만 사용하기

앞서 다뤘던 `package.json`파일 중 `script`부분 아래 `build`를 다음과 같이 수정해주세요. 

```js
{
    ...
    "scripts": {
        "build": "webpack --optimize-minimize",
    },    
    ...
}
```

그리고 `webpack.config.js` 파일 중 위에서 넣어주었던 `plugins`를 통채로 지워주세요.(더이상 필요하지 않아요!)

만약 여러분이 `webpack.config.js`파일을 정확히 설정해 `webpack`이라는 명령어가 성공적으로 실행되고있던 상태라면 `--optimize-minimize`라는 명령어만 뒤에 붙여주면 곧바로 실행됩니다.

이제 여러분이 개발할 때 `webpack-dev-server`를 통해 빌드가 실행될때는 treeshaking이 되지 않고, 대신 배포를 위해 빌드를 할 때는 최소화된 작은 번들된 js파일을 가질 수 있게 됩니다.

## 마무리

여러분이 위 과정을 모두 따라왔다면 아마 `package.json`과 `webpack.config.js`파일은 이와 유사하게 생겼을거에요.

```js
// 앞뒤생략한 package.json
{
    ...
    "scripts": {
        "build": "webpack --optimize-minimize",
        "devserver": "webpack-dev-server --open"
    },    
    ...
}
```

```js
// webpack.config.js 파일
const webpack = require('webpack');
const path = require('path');
const UglifyJSPlugin = require('uglifyjs-webpack-plugin');

module.exports = {
    entry: './src/js/index.js',
    output: {
        path: path.resolve(__dirname, 'dist'),
        publicPath: '/dist/',
        filename: 'bundle.js'
    },
    module: {
        rules: [
            {
                test: /\.js$/,
                include: path.join(__dirname, 'src'),
                exclude: /(node_modules)|(dist)/,
                use: {
                    loader: 'babel-loader',
                    options: {
                        presets: [
                            ["env", {
                                "targets": {
                                    "browsers": ["last 2 versions", "safari >= 7"]
                                }
                            }]
                        ]
                    }
                }
            }
        ]
    }
    // Plugin은 필요한 것만 넣어주세요. UglifyJSPlugin은 필요없어요!
}
```
