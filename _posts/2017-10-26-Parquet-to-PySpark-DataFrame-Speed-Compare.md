---
title: "PySpark로 여러개의 parquet 자료 로딩 속도 비교: for loop vs multiple paths" 
date: 2017-10-26
layout: post
categories:
- python
- spark
- tips
published: false
image: /img/
---


## 들어가며 

PySpark로 AWS S3등에 올라가 있는 `.parquet`형태의 자료/로그를 읽어 Spark dataframe자료형으로 만들 때 여러개의 