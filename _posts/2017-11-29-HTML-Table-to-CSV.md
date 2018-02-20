---
title: "HTML Table을 CSV로 다운로드하기"
date: 2017-11-29
layout: post
categories:
- javascript
published: true
image: https://d1sr4ybm5bj1wl.cloudfront.net/img/table_to_csv.jpg
---

## 들어가며

웹 개발을 하다보면 `<table>`의 내용물을 모두 csv 파일로 받게 해달라는 요구사항이 종종 생깁니다.

가장 일반적인 방법은 csv 형태로 파일을 받을 수 있는 API를 서버가 제공해주는 방법입니다. (백엔드 개발자에게 일을 시킵시다.)

하지만 csv를 던져주는 API 서버가 없다면 프론트에서 보여지는 `<table>`만이라도 csv로 만들어줘야 합니다.

이번 글은 이럴때 쓰는 방법입니다.

## 소스코드

우선 이렇게 생긴 HTML이 있다고 생각해 봅시다.

본문이라고는 `#`, `title`, `content`가 들어있는 자그마한 `<table>` 하나가 있습니다.

```html
<!DOCTYPE html>
<html>
<head lang="ko">
    <meta charset="utf-8">
    <title>빈 HTML</title>
</head>
<body>
    <table id="mytable">
        <thead>
            <tr>
                <th>#</th>
                <th>title</th>
                <th>content</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>1</td>
                <td>Lorem Ipsum</td>
                <td>로렘 입섬은 빈칸을 채우기 위한 문구입니다.</td>
            </tr>
            <tr>
                <td>2</td>
                <td>Hello World</td>
                <td>헬로 월드는 언어를 배우기 시작할때 화면에 표준 출력을 할때 주로 사용하는 문구입니다.</td>
            </tr>
        </tbody>
    </table>

    <button id="csvDownloadButton">CSV 다운로드 받기</button>
</body>
</html>
```

테이블 엘리먼트의 id는 `mytable`이고, CSV 다운로드 버튼의 id는 `csvDownloadButton` 입니다.

이제 JS를 조금 추가해봅시다. ES6/ES5에 따라 선택해 사용해주세요.

아래 코드를 `<script></script>` 태그 사이에 넣어 `</body>` 바로 앞에 넣어주세요.

### ES6을 사용할 경우

```javascript
class ToCSV {
    constructor() {
        // CSV 버튼에 이벤트 등록
        document.querySelector('#csvDownloadButton').addEventListener('click', e => {
            e.preventDefault()
            this.getCSV('mycsv.csv')
        })
    }

    downloadCSV(csv, filename) {
        let csvFile;
        let downloadLink;

        // CSV 파일을 위한 Blob 만들기
        csvFile = new Blob([csv], {type: "text/csv"})

        // Download link를 위한 a 엘리먼스 생성
        downloadLink = document.createElement("a")

        // 다운받을 csv 파일 이름 지정하기
        downloadLink.download = filename;

        // 위에서 만든 blob과 링크를 연결
        downloadLink.href = window.URL.createObjectURL(csvFile)

        // 링크가 눈에 보일 필요는 없으니 숨겨줍시다.
        downloadLink.style.display = "none"

        // HTML 가장 아래 부분에 링크를 붙여줍시다.
        document.body.appendChild(downloadLink)

        // 클릭 이벤트를 발생시켜 실제로 브라우저가 '다운로드'하도록 만들어줍시다.
        downloadLink.click()
    }

    getCSV(filename) {
        // csv를 담기 위한 빈 Array를 만듭시다.
        const csv = []
        const rows = document.querySelectorAll("#mytable table tr")

        for (let i = 0; i < rows.length; i++) {
            const row = [], cols = rows[i].querySelectorAll("td, th")

            for (let j = 0; j < cols.length; j++)
                row.push(cols[j].innerText)

            csv.push(row.join(","))
        }

        // Download CSV
        this.downloadCSV(csv.join("\n"), filename)
    }
}

document.addEventListener('DOMContentLoaded', e => {
    new ToCSV()
})
```

### ES5를 사용하실 경우 

```javascript
function downloadCSV(csv, filename) {
    var csvFile;
    var downloadLink;

    // CSV 파일을 위한 Blob 만들기
    csvFile = new Blob([csv], {type: "text/csv"})

    // Download link를 위한 a 엘리먼스 생성
    downloadLink = document.createElement("a")

    // 다운받을 csv 파일 이름 지정하기
    downloadLink.download = filename;

    // 위에서 만든 blob과 링크를 연결
    downloadLink.href = window.URL.createObjectURL(csvFile)

    // 링크가 눈에 보일 필요는 없으니 숨겨줍시다.
    downloadLink.style.display = "none"

    // HTML 가장 아래 부분에 링크를 붙여줍시다.
    document.body.appendChild(downloadLink)

    // 클릭 이벤트를 발생시켜 실제로 브라우저가 '다운로드'하도록 만들어줍시다.
    downloadLink.click()
}

function getCSV(filename) {
    // csv를 담기 위한 빈 Array를 만듭시다.
    var csv = []
    var rows = document.querySelectorAll("#mytable table tr")

    for (var i = 0; i < rows.length; i++) {
        var row = [], cols = rows[i].querySelectorAll("td, th")

        for (var j = 0; j < cols.length; j++)
            row.push(cols[j].innerText)

        csv.push(row.join(","))
    }

    // Download CSV
    downloadCSV(csv.join("\n"), filename)
}

document.addEventListener('DOMContentLoaded', e => {
    // CSV 버튼에 이벤트 등록
    document.querySelector('#csvDownloadButton').addEventListener('click', e => {
        e.preventDefault()
        getCSV('mycsv.csv')
    })
})
```

### 전체 예시

> [예제 html_to_csv.html](/others/html_to_csv.html)에서 직접 동작하는 것을 확인해 보세요!

```html
<!DOCTYPE html>
<html>
<head lang="ko">
    <meta charset="utf-8">
    <title>빈 HTML</title>
</head>
<body>
    <table id="mytable">
        <thead>
            <tr>
                <th>#</th>
                <th>title</th>
                <th>content</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>1</td>
                <td>Lorem Ipsum</td>
                <td>로렘 입섬은 빈칸을 채우기 위한 문구입니다.</td>
            </tr>
            <tr>
                <td>2</td>
                <td>Hello World</td>
                <td>헬로 월드는 언어를 배우기 시작할때 화면에 표준 출력을 할때 주로 사용하는 문구입니다.</td>
            </tr>
        </tbody>
    </table>

    <button id="csvDownloadButton">CSV 다운로드 받기</button>
</body>
<script type="text/javascript">
    class ToCSV {
        constructor() {
        // CSV 버튼에 이벤트 등록
        document.querySelector('#csvDownloadButton').addEventListener('click', e => {
            e.preventDefault()
            this.getCSV('mycsv.csv')
        })
    }

    downloadCSV(csv, filename) {
        let csvFile;
        let downloadLink;

        // CSV 파일을 위한 Blob 만들기
        csvFile = new Blob([csv], {type: "text/csv"})

        // Download link를 위한 a 엘리먼스 생성
        downloadLink = document.createElement("a")

        // 다운받을 csv 파일 이름 지정하기
        downloadLink.download = filename;

        // 위에서 만든 blob과 링크를 연결
        downloadLink.href = window.URL.createObjectURL(csvFile)

        // 링크가 눈에 보일 필요는 없으니 숨겨줍시다.
        downloadLink.style.display = "none"

        // HTML 가장 아래 부분에 링크를 붙여줍시다.
        document.body.appendChild(downloadLink)

        // 클릭 이벤트를 발생시켜 실제로 브라우저가 '다운로드'하도록 만들어줍시다.
        downloadLink.click()
    }

    getCSV(filename) {
        // csv를 담기 위한 빈 Array를 만듭시다.
        const csv = []
        const rows = document.querySelectorAll("#mytable tr")

        for (let i = 0; i < rows.length; i++) {
            const row = [], cols = rows[i].querySelectorAll("td, th")

            for (let j = 0; j < cols.length; j++)
                row.push(cols[j].innerText)

            csv.push(row.join(","))
        }

        // Download CSV
        this.downloadCSV(csv.join("\n"), filename)
    }
}

document.addEventListener('DOMContentLoaded', e => {
    new ToCSV()
})
</script>
</html>
```

하지만 이렇게하면 한글이 깨지는 문제가 있습니다.

## 한글 깨지는 문제 해결하기 

앞서 한글이 깨지는 이유는 기본적으로 엑셀이 인코딩을 UTF-8로 인식하지 않기 때문에 문제가 발생합니다.

이때 아래 코드를 csv blob을 만들기 전 추가해주면 됩니다.

```js
// 한글 처리를 해주기 위해 BOM 추가하기
const BOM = "\uFEFF";
csv = BOM + csv
```

```javascript
// downloadCSV 함수를 이렇게 수정해 주세요.
downloadCSV(csv, filename) {
    let csvFile;
    let downloadLink;

    // 한글 처리를 해주기 위해 BOM 추가하기
    const BOM = "\uFEFF";
    csv = BOM + csv

    // CSV 파일을 위한 Blob 만들기
    csvFile = new Blob([csv], {type: "text/csv"})

    // Download link를 위한 a 엘리먼스 생성
    downloadLink = document.createElement("a")

    // 다운받을 csv 파일 이름 지정하기
    downloadLink.download = filename;

    // 위에서 만든 blob과 링크를 연결
    downloadLink.href = window.URL.createObjectURL(csvFile)

    // 링크가 눈에 보일 필요는 없으니 숨겨줍시다.
    downloadLink.style.display = "none"

    // HTML 가장 아래 부분에 링크를 붙여줍시다.
    document.body.appendChild(downloadLink)

    // 클릭 이벤트를 발생시켜 실제로 브라우저가 '다운로드'하도록 만들어줍시다.
    downloadLink.click()
}
```
