---
title: 搭建Hexo，在不同机器上编辑博客
date: 2017-06-03 18:55:11
tags: [hexo,博客]
categories: 搭建hexo
cover_picture: https://img.zcool.cn/community/01b503554bf99f000001bf72403d70.jpg@1280w_1l_2o_100sh.webp
---


在有git环境，可连github的网络机器上，无缝无痛更新hexo博客。具体包括：
1. 可取回hexo source，并剔除node_modules目录；
2. 可取回theme目录，并剔除对应的node_module目录；
3. 另外机器上的编辑，可正常upload；
<!--more-->

### 安装NodeJS
 下载NodeJS安装包 
设置taobao registry

> 1. npm install -g nrm --registry=https://registry.npm.taobao.org
> 1. nrm use taobao

### 安装hexo
> 1. npm i hexo -g
> 1. hexo init yourblogpath
> 1. cd yourblogpath
> 1. hexo clean
> 1. hexo g
> 1. hexo s
> 1. hexo d

 
### Git环境
安装[GitforWindows](https://npm.taobao.org/mirrors/git-for-windows/)
 
配置github.com的hosts

#### git常用操作
> 1. git init 
> 1. git status
> 1. git add --all
> 1. git commit -m 'test'
> 1. git remote add origin git@github.com:peaceFun/hexo-src.git
> 1. git push -f --set-upstream origin master

#### 测试连接github.com
打开Git Bash环境
> 1. ssh -T git@github.com
 
#### permission denied问题排除
``` bash
git config --global user.name "Git账号" git config --global user.email "Git邮箱"
ssh-keygen -t rsa -C "your_email@example.com"
将SSH公钥添加到GitHub账户
eval `ssh-agent`
ssh-add ~/.ssh/id_rsa
ssh-add -l
ssh -T git@github.com
```

### git下载博客内容

> 1. git clone -b hexo-src https://github.com/peaceFun/hexo-src.git hexoblog
> 1. cd hexoblog
> 1. npm i
> 1. 内容文件编辑
> 1. hexo clean
> 1. hexo g
> 1. hexo s
> 1. 检查页面显示正常
> 1. hexo clean
> 1. git add --all
> 1. git commit -m 'something...'
> 1. git push -f --set-upstream origin hexo-src:hexo-src
> 1. hexo d

打开查看更新后的[Geo-I站点](http://peacefun.github.io)

### 参考：
[hexo 设置](https://hexo.io/zh-cn/docs/)
[hexo 主题设置](https://hexo.io/zh-cn/docs/themes) 
[miho主题](https://github.com/WongMinHo/hexo-theme-miho) 
[图站](http://www.zcool.com) 
