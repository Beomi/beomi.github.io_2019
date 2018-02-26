---
title: "PySpark: 손상된 parquet파일 무시하기"
date: 2018-02-26
layout: post
categories:
- python
- pyspark
- tips
published: true
image: https://d1sr4ybm5bj1wl.cloudfront.net/img/2018-02-26-PySpark-Read-Parquet-ignoreCorruptedFiles.png
---

## 문제

PySpark를 이용해 파일을 읽어와 DataFrame 객체로 만드는 경우 읽어오는 파일이 parquet 파일이라면 이 파일이 어떤 형식으로 되어있는지(어떤 Column/Type으로 이루어져있는지)에 대한 정보를 필요로 합니다.

보통 parquet파일에 이 파일에 대한 스키마가 저장되어있어 파일을 읽고 쓰는데 지장이 없습니다. 하지만 간혹 parquet파일이 깨져있는 경우가 있습니다.

```python
# spark 는 SparkSession 객체
path = [
    's3a://some-bucket/brokenfile.parquet', # Broken!
]

df = spark.read.parquet(*path) # SparkException!
``` 

위와 같은 코드를 실행할 경우 아래와 같이 깨진 파일이 속한 parquet파일들을 읽으려 할 경우 아래와 같이 `org.apache.spark.SparkException`이 발생합니다.

![SparkException]({{site.static_url}}/img/dropbox/2018-02-26 PM 2.54.19.png)

로그를 살펴보면 "Could not read footer for file" 이라는 문구가 보입니다. 즉, parquet파일의 footer가 손상되어 파일을 읽어오지 못합니다. 하지만 이 파일 하나만 문제가 있다 하더라도 전체 과정이 멈춰버립니다. 더 심각한 문제는 만약 `*path`중 첫 번째 파일의 footer가 정상적이었다면 저 `path` 리스트 중 한 파일이 문제가 있다 하더라도 Spark의 lazy loading, lazy computing으로 인해 `.show()`나 `.count()`와 같이 실제 데이터가 필요한 코드를 실행하기 전까지는 데이터를 불러오지 않고 메타게이터만 연결된 DataFrame 객체를 사용하기 때문에 파이썬 코드들이 정상적으로 작동하더라도 실제 parquet파일이 깨졌다는 사실을 알 수가 없다는 것입니다.

```python
path = [
    's3a://some-bucket/normal1.parquet', # 정상
    's3a://some-bucket/normal2.parquet', 
    's3a://some-bucket/normal3.parquet', 
    's3a://some-bucket/brokenfile.parquet', # Broken!
    's3a://some-bucket/normal4.parquet', 
    # ...
]

df = spark.read.parquet(*path) # 정상적으로 실행된다.
```

## 해결 방법

우선 손상된 parquet파일을 무시하고 나머지 정상적인 파일이라도 불러와 DataFrame을 만들어봅시다.

아래 설정은 스파크 세션을 생성할 때 설정값으로 넣거나, 혹은 세션을 만든 뒤 만들어진 `spark`와 같은 `SparkSession`객체에 설정으로 진행해도 됩니다. 이번에는 이미 생성된 `spark` 객체에 설정값을 바꿔 사용해봅니다. `.read.parquet(*path)`를 실행하기 전에 아래와 같이 설정을 넣어줍시다.

```python
spark.conf.set("spark.sql.files.ignoreCorruptFiles","true")
```

아래와 같이 코드를 만들어 줍시다. 

```python
path = [
    's3a://some-bucket/normal1.parquet', # 정상
    's3a://some-bucket/normal2.parquet',
    's3a://some-bucket/normal3.parquet',
    's3a://some-bucket/brokenfile.parquet', # Broken!
    's3a://some-bucket/normal4.parquet',
    # ...
]

spark.conf.set("spark.sql.files.ignoreCorruptFiles","true")
df = spark.read.parquet(*path) # 정상적으로 실행된다.
```

이제 무시된 파일의 데이터는 제외하고 나머지 파일의 데이터로 이루어진 정상적인 DataFrame객체가 생성됩니다.

## 남은 문제

만약 parquet파일의 리스트인 `path`가 모두 손상된 파일로 이루어졌다면 아래와 같은 `AnalysisException` 에러가 발생합니다.

![AnalysisException]({{site.static_url}}/img/dropbox/2018-02-26 PM 2.51.24.png)

`ignoreCorruptFiles` 옵션을 `true`로 설정하고 작업을 진행할 경우 에러가 있는 파일 부분은 읽지 않아 만약 위와 같이 단 하나의 파일만 읽을 경우 빈 Spark DataFrame객체가 생성되는데, 이때 DataFrame의 Scheme이 없기 때문에(읽은 파일이 없으니까!) 'Unable to infer schema for Parquet. It must be specified manually.;' 라는 에러가 발생하게 됩니다.
