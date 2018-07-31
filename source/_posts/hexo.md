---
title: 搭建Hexo，在不同机器上编辑博客
date: 2017-06-03 18:55:11
tags: [hexo,博客]
categories: 搭建hexo
cover_picture: https://img.zcool.cn/community/01b503554bf99f000001bf72403d70.jpg@1280w_1l_2o_100sh.webp
---


### 初次同步

> https://github.com/peaceFun/hexo-src.git
> 
> 1. git init 
> 1. git add .
> 1. git commit -m 'test'
> 1. git remote add origin git@github.com:peaceFun/hexo-src.git
> 1. git push -f --set-upstream origin master
> 

### 再次同步
> 1. hexo clean 
> 1. git push -f --set-upstream origin master


<!--more-->
### 新环境下获取

1. hexo init hexo
2. git clone https://github.com/peaceFun/hexo-src.git rt
3. cp -Rf rt/. hexo
4. rm -rf rt


### NPM taobao环境
> http://npm.taobao.org
> 
```
npm install -g cnpm --registry=https://registry.npm.taobao.org

cnpm install -g hexo
cnpm install -g hexo-generator-feed
cnpm install -g hexo-generator-sitemap
cnpm install -g hexo-deployer-git
cnpm install -g hexo-generator-tag
cnpm install -g hexo-cli
```