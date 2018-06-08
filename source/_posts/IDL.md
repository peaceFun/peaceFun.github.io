---
title: IDL
date: 2017-06-04 20:24:36
tags: [IDL,Remote Sensing]
categories: Develop
cover_picture: images/07.jpg
---

## 动机
求学期间，用过IDL一阵子。将零散的编录到博客，铭记时光。

## IDL概述

1. 首先看看IDL能干什么，《Solving Real Problems with Computer Graphics》ppt是英文的，很精彩。
1. 其次是IDL基础语法，辜智慧的IDL入门ppt，全面简练。有其他编程语言基础试写几段code就很容易上手。

<!-- more -->
由于其强大的功能和独特的特点，IDL语言可以应用于任何领域的三维数据可视化、数值计算、三维图形建模、科学数据读取等功能中。概括说来，在地球科学（包括气象、水文、海洋、土壤、地质、地下水等）、医学影像、图像处理、GIS系统、软件开发，大学教学，实验室，测试技术，天文，航空航天、信号处理，防御工程，数学统计及分析，环境工程等很多领域，IDL语言都可以得到广泛而又深远的应用。
目前应用IDL语言，已经开发出了ENVI、IMAGIS、RiverTools、医学等成熟产品。具体的应用实例也非常多，如在2000年澳大利亚悉尼奥运会综合预报系统、美国国家环境卫星数据和信息服务中心的厄尔尼诺现象分析等工作中得到了成功的应用。作为面向矩阵、语法简单的第四代可视化语言，IDL致力于科学数据的可视化和分析，是跨平台应用开发的最佳选择。它集可视化、交互分析、大型商业开发为一体，为用户提供完善、灵活、有效地开发环境。 
问问自己，准备要用IDL来干什么。要有的放矢才行。

## 找回桌面Envi快捷方式
1. envi快捷方式
> E:\ITT\IDL64\bin\bin.x86\idlrt.exe -nodemowarn -novm "E:\ITT\IDL64\lib\hook\envi.sav"

1. idl快捷方式
> E:\ITT\IDL64\bin\bin.x86\idlde.exe

1. idl+envi快捷方式
> E:\ITT\IDL64\bin\bin.x86\idlde.exe -minimized -noconfirmexit -nosplash @“E:\ITT\IDL64\products\envi44\bin\envi.run”
 
## myEclipse配置IDL开发环境
新安装了Envi5.0 IDL8.2，总结一下，JSP调用IDL的配置，jar包配置，环境变量配置，dll配置，tomcat路径配置，tomcat运行选项配置，jdk lib和bin配置。结果是要能自如地在jsp里面建立pro对应的java对象。
 
已经配置成功。汇总记录一下：
1. myEclipse Java Web Project添加javaidlb.jar包，这个毫无疑问，不添加编译工程都失败；
1. java 的jdk jre bin 和lib目录下不要有任何idl的dll或者jar包；
1. 环境变量path添加idl\bin和idl\bin\bin.x86，哪一个起作用我暂时没辨别；
1. myEclipse 中Tomcat选项添加了idl bin bin.x86 lib目录，是否起作用暂时没辨别；
1. myEclipse 中Installed Jre添加选项，就是IDL调试开关；
1. 重新安装一次Envi5（如实记录，不知是否起作用）；


## TM3、4波段GeoTiff数据计算NDVI
NDVI是遥感图像处理最常见的![NDVI](http://i.weather.com.cn/images/henan/nyqx/ygjc/nyyg/2011/05/22/6731D1A3076F2F3187AF7FE47EE34B76.jpg)

``` Fortran
PRO TIFF_NDVI,F1,F2,FOUT 
    F1 = DIALOG_PICKFILE(TITLE = 'B4 TIFF',FILTER='*.TIF',/READ) 
    F2 = DIALOG_PICKFILE(TITLE = 'B3 TIFF',FILTER='*.TIF',/READ) 
    FOUT =DIALOG_PICKFILE(TITLE = 'RESULT PATH',FILTER='*.TIF',/WRITE) 
    
    IF(FILE_TEST(F1) GT 0 AND FILE_TEST(F2) GT 0) THEN BEGIN 
        B1 = READ_TIFF(F1,GEOTIFF=GE1) 
        B2 = READ_TIFF(F2,GEOTIFF=GE2) 
        HELP,B1,B2 
        C = 0.001 
        WRITE_TIFF,FOUT,-1.0>( (FLOAT(B1)-FLOAT(B2))/(FLOAT(B1)+FLOAT(B2) + C) )<1.0,/FLOAT,GEOTIFF=GE2 
        PRINT,'OK 
    ENDIF 
END 
```

## IDL PCA主成分分析
在多元统计分析中，主成分分析（Principal components analysis，PCA）是一种分析、简化数据集的技术。主成分分析经常用于减少数据集的维数，同时保持数据集中的对方差贡献最大的特征。【wiki】

在遥感影像解译与分类中，PCA是经常用到的降维滤噪处理技术。现在实现这个处理流程，便于熟悉和掌握IDL矩阵乘除运算操作。

``` fortran
Pro Pca,Data,Eigenvalues = Egvalues,Eigenvectors = Egvec,Percent = Percent,_Extra=Extra
  Get_Sz,Data,Ns=Ns,Nl=Nl,Nb=Nb,Type= Type
  
  If Isa(Data,/Number) And Nb Gt 1 And Size(Data,/N_Dimensions) Eq 3 Then Begin
    Data = Transpose(Reform(Data,Ns*Nl,Nb))
    Corr = Correlate(Data,/Covariance)
    Egvalues = Eigenql( Corr, Eigenvectors=Egvec,/Double ,/Absolute)
    Absegvalue = Abs(Egvalues)
    Percent = Absegvalue / Total(Absegvalue);
    ; Egvec Format
    ;Egvec = [  Egvec1
    ;           Egvec2
    ;           Egvec3
    ;           ...
    
    Data = Temporary(Reform(Transpose(Egvec) ## Transpose(Data),Ns,Nl,Nb))
  Endif
End
;---------------------------------------
Pro Get_Sz,Data,Ns=Ns,Nl=Nl,Nb=Nb,Type = Type

  Sz = Size(Data)
  
  Type = Sz[0] Ge 1 ? Sz[-2] : 0
  Ns = Sz[0] Ge 1 ? Sz[1] : 1
  Nl = Sz[0] Ge 2 ? Sz[2] : 1
  Nb = Sz[0] Ge 3 ? Sz[3] : 1
  
End
```

## IDL EOF分析
关于EOF详细介绍请wiki http://en.wikipedia.org/wiki/Empirical_orthogonal_functions或者Google之。

与PCA一样，EOF也是遥感多维变量的一种线性变换，同样可以达到降维的目的。EOF多用于气象要素场等包含了时间、空间信息的数据，例如可以根据多年气象站的降雨监测资料，提取出空间“主成分”，即若干个主要的大面积降雨或者干旱的地区；时间“主成分”，即降雨年际周期或者年内周期。

EOF是一种极有效的数据处理手段，可以直接得到有物理意义的结果。

``` fortran
Pro Get_Sz,Data,Ns=Ns,Nl=Nl,Nb=Nb,Type = Type

  Sz = Size(Data)
  
  Type = Sz[0] Ge 1 ? Sz[-2] : 0
  Ns = Sz[0] Ge 1 ? Sz[1] : 1
  Nl = Sz[0] Ge 2 ? Sz[2] : 1
  Nb = Sz[0] Ge 3 ? Sz[3] : 1
  
End


Pro Eofs,Data,Eof,Pcs
  ;Svdc,Data(*,*),W,U,V,/Column
  ;Eofs=Reform(U(*,*),Nlons,Nlats,Cutoff)
  ;Pcs=V
  ;Svls=W
  Eof = -1
  Pcs = -1
  Get_Sz,Data,Ns=Ns,Nl=Nl,Nb=Nb,Type = Type
  
  If Isa(Data,/Number) And Nb Gt 1 And Size(Data,/N_Dimensions) Eq 3 Then Begin
    Svdc,Data,W,U,V,/Column
    Data = Transpose(Reform(Data,Ns*Nl,Nb))
    Eof=Reform(U,Ns,Nl,Nb)
    Pcs = V
  Endif
End
```

## IDL 求坡度坡向

``` fortran
Pro Aspect_Slope,Dem,Aspect = Aspect,Slope=Slope,Pixelsize = Pixelsize
  ;Ref To Doi:10.1016/J.Cageo.2003.07.005
  Aspect = -1
  Slope = -1
  Pixelsize = [30.,30.]
  Get_Sz,Dem,Ns=Ns,Nl=Nl,Nb=Nb,Type = Type
  If Isa(Dem,/Number) And Nb Eq 1 And Size(Dem,/N_Dimensions) Eq 2 Then Begin
    K_X = Transpose([-1,1])
    K_Y = [-1.0,1.0]
    Dx = Convol(Dem,K_X,/Edge_Truncate,/Nan)/Pixelsize[1] ; Mei Cuo ,
    Dy = Convol(Dem,K_Y,/Edge_Truncate,/Nan)/Pixelsize[0]
    Pi = Acos(-1.0d)
    Help,Dx,Dy
    Slope = Atan( Sqrt(Dx*Dx + Dy * Dy)) * 180.0 / Pi
    Aspect = 270 + Atan(Dy*1.0 /Dx) - 90.0 * Fix(Dx / Abs(Dx))
  Endif
End

Pro Get_Sz,Data,Ns=Ns,Nl=Nl,Nb=Nb,Type = Type

  Sz = Size(Data)
  
  Type = Sz[0] Ge 1 ? Sz[-2] : 0
  Ns = Sz[0] Ge 1 ? Sz[1] : 1
  Nl = Sz[0] Ge 2 ? Sz[2] : 1
  Nb = Sz[0] Ge 3 ? Sz[3] : 1
  
End
```

## IDL 求TVDI
介绍参见[ENVI下温度植被干旱指数(TVDI)功能模块](http://blog.sina.com.cn/s/blog_764b1e9d0100wdrr.html)

1. 主要是如何求得散点图上下两条边，我的策略是竖着切开散点，分作n个柱子。每个柱子如果总点数大于200，就统计最大最小的50个点作为干湿边的组成部分。

1. sort排序函数，where查找满足条件的元素的下标和个数，linefit线性拟合，poly根据拟合结果和x求得y。具体的多看帮助,那里说的详细,还有例子。

``` fortran
Pro Tvdi,Ndvi,Lst,Nbins,Res
  Res = -1
  
  Sz1 = Size(Ndvi,/Dimensions)
  Sz2 = Size(Lst,/Dimensions)
  If N_Elements(Sz1) Ne 2 Or N_Elements(Sz2) Ne 2 Then Return
  If Total(Abs(Sz1 - Sz2)) Ne 0 Then Return
  If ~Isa(Ndvi,/Number) And ~Isa(Lst,/Number) Then Return
  
  ;Find Dyr Wet Pts
  Range = [0.0,1.0]
  Npt_Filter = 200
  Pts = 50
  Dry_Pts = [0]
  Wet_Pts = [0]
  
  Idx = Floor(Ndvi * Nbins)
  For I = 0, Nbins Do Begin
    Pt = Where(Idx Eq I,Cnt)
    If(Cnt Gt Npt_Filter) Then Begin
      Ii = Sort(Lst[Pt])
      Dry_Pts = [ Dry_Pts,Pt[Ii[Indgen(Pts)]] ]
      Wet_Pts = [ Wet_Pts,Pt[Ii[-Indgen(Pts)]] ]
    Endif
  End
  
  If N_Elements(Dry_Pts) Le 1 Then Return
  
  Dry_Pts = Dry_Pts[1:*]
  Wet_Pts = Wet_Pts[1:*]
  
  Wet = Linfit(Ndvi[Wet_Pts],Lst[Wet_Pts])
  Dry = Linfit(Ndvi[Dry_Pts],Lst[Dry_Pts])
  
  Good = Where(Ndvi Ge Range[0] And Ndvi Le Range[1],Cnt)
  If Cnt Le 0 Then Return
  
  Res = Make_Array(Size = Size(Ndvi))
  Res[Good] = (Lst - Poly(Ndvi[Good],Wet)) / (Poly(Ndvi[Good],Dry) - Poly(Ndvi[Good],Wet) )
  
End
```

## IDL建立影像金字塔

形成按目录放好的，类似于Google Map Tile的金字塔瓦片Jpg。

``` fortran
Pro Tsplit
  ; 读入jpeg格式文件
  Szfile = 'E:\Test.Jpg'; Dialog_Pickfile(Title = 'Input Data')
  Read_Jpeg,Szfile,Image,True = 3
  ; 切割5级
  Nlevel = 5;
  ;
  For Ilevel = 0,Nlevel-1 Do Begin
      Split,Image,Ilevel,Ib
  Endfor
  Return
End

Pro Split,Image,Level,Iband
  Src = 'E:\Src'
  Ns0 = 512
  Nl0 = 512
  N0 = 2^Level
  Sz = Size(Image,/Dimensions)
  Help,Sz
  Print,Sz
  Nx = Sz[0]
  Ny = Sz[1]
  Xspan = Nx*1.0/N0;
  Yspan = Ny*1.0/N0;
  Imglet = Bytarr(Ns0,Nl0,3)

  Fmt = '(%"%S\\%D\\Img_%D_%D.Jpg")';
  For Is = 0l,N0-1 Do Begin
      For Il = 0l,N0 -1 Do Begin
          X = Indgen(Ns0)#Replicate(1,Nl0)*Xspan/Ns0 + Is*Xspan
          Y = Replicate(1,Ns0)#Indgen(Nl0)*Yspan/Nl0 + Il*Yspan
          For Ib = 0,2 Do Begin
              Imglet[*,*,Ib] = Bilinear(Image[*,*,Ib],X,Y)
          Endfor
          Fileout = String(Src,Level,N0-Il-1,Is,Format =Fmt)
          Dir = File_Dirname(Fileout)
          If(File_Test(Dir,/Directory) Lt 1) Then File_Mkdir,Dir
          Write_Jpeg,Fileout,Imglet,True = 3
      Endfor
  Endfor
End

; 主程序
Pro Pyrmid

  Tsplit
  Print,'Done
End
```

## 按经纬度批量下载MODIS产品

Modis免费分发，光谱通道丰富，产品体系成熟，在多个行业和领域有广泛成功的应用。已成为重要的遥感数据源之一。一般若需获取modis数据，要注册wist账号，查询订购（免费）并等待回复mail，整个流程一般约需数小时。为了避免等待，本文用IDL语言实现了modis产品的地理范围查询，返回的url直接添加到迅雷下载任务列表。
![](http://images.cnitblog.com/blog/583396/201311/18161902-2988572b59ca46cdabffb013ca0372a3.jpg)
运行环境：IDL7.0以上版本，迅雷5.0版本以上

### 原理
1. Modis官方ftp站点实时记录了5分钟产品的经纬度范围，并保存在txt文件中。Txt各列以逗号分隔，可以用记事本查看。
1. Modis官方ftp站点还保存有全部常规产品hdf格式文件。
1. IDL对象IDLnetUrl可以获取ftp站点目录列表，运行ftp命令，获得http协议url指向的文件。
1. IDL对象IDLcomIDispatch对象可以调用com /ole对象；迅雷ThunderAgent.Agent是一种ole组件，可用于新建添加迅雷下载任务。

### 流程
1. ) 指定日期、经纬度多边形polygon
1. ) 获得指定日期5分钟产品的地理范围txt文件，获得指定日期5分钟产品列表（简洁模式）
![](http://images.cnitblog.com/blog/583396/201311/20132851-03d184fa364745519d43217049bdfab3.gif)
1. ) 解析txt中各5分钟产品经纬度范围、日夜模式，判断与指定的经纬度polygon是否相交；有交集则记录5分钟产品的url
1. ) 将所有符合要求的hdf文件url添加为迅雷下载任务

### 源码

``` fortran
;-----------------------------------------------------------------

Pro Modistest
  Query_Download,2010,7,18,[110,110,117,117],[34,30,30,34],Productname='021km'
End
;-----------------------------------------------------------------

Pro Query_Download,Year,Month,Day,Xpoly,Ypoly,Productname=Productname

  Get_Modis_Metafile,Year,Month,Day,Geometa1,Modlist,/Terra,Productname=Productname
  Query_Modis,Geometa1,Modlist,Xpoly,Ypoly
  
  Get_Modis_Metafile,Year,Month,Day,Geometa2,Mydlist,/Aqua,Productname=Productname
  Query_Modis,Geometa2,Mydlist,Xpoly,Ypoly
  
  If Size(Modlist,/Type) Eq 7 Then L = [Modlist]
  If Size(Mydlist,/Type) Eq 7 Then L = [L,Mydlist]  
  If N_Elements(L) Gt 0 Then Add_Download,L
  
End
;-----------------------------------------------------------------

Pro Query_Modis,Data,Filelist,Xpoly,Ypoly
  
  Flist =Filelist
  Filelist = -1
  If Size(Data,/Type) Ne 7 Or Size(Flist,/Type) Ne 7 Or N_Elements(Xpoly) Ne N_Elements(Ypoly) Then Return
  
  G = {Geometa,G_Id:'',Starttime:'',Set:0b,Orbit_Number:1l,Daynight:0b,Box:Dindgen(4),X:Dindgen(4),Y:Dindgen(4)}
  Meta = [G]
  
  For I = 3,N_Elements(Data)-1 Do Begin
    If N_Elements(Data) Le 3 Then Return;
    
    Tmp = Strsplit(Data[I],",",/Extract)
    If N_Elements(Tmp) Eq 17 Then Begin    
      G.G_Id = (Strsplit(Tmp[0],'.',/Extract))[2]
      G.Starttime = Tmp[1]
      G.Set = Tmp[2]
      G.Orbit_Number = Tmp[3]
      G.Daynight = Byte(Tmp[4])
      G.Box = Tmp[5:8]
      G.X = Tmp[9:12]
      G.Y = Tmp[13:16]
      Meta = [Meta,G]
    Endif
  Endfor
  
  If N_Elements(Meta) Gt 1 Then Meta = Meta[1:*] Else Return
 
  Idx = Intarr(480);    
  I = Fix(Strmid(File_Basename(Flist),18,4))/5
  Idx[I] = Indgen(N_Elements(I))
 
  Ret = ['']
  For I = 0,N_Elements(Meta)-1 Do Begin
    Id = Idx[Fix(Meta[I].G_Id)/5]
    ;
    ;换日线附近一般不满足要求
    If (Max(Meta[I].X) - Min(Meta[I].X)) Gt 300 Then Continue      
    ;
    If Total(Inside(Xpoly,Ypoly,Meta[I].X,Meta[I].Y)) Gt 0 $
      And  Meta[I].Daynight Lt Byte('N') $
      And  Id Gt 0  Then Ret = [Ret,Flist[Id]]      
  Endfor
  
  Filelist = N_Elements(Ret) Gt 1 ? Ret[1:*] : -1
 
End
;-----------------------------------------------------------------

Pro Get_Modis_Metafile,Year,Month,Day,Geometa,Flist,Terra=Terra,Aqua=Aqua,Productname=Productname
  Geometa = -1
  Flist = -1;
  
  Catch, Errorstatus
  If (Errorstatus Ne 0) Then Begin
    Catch, /Cancel
    R = Dialog_Message(!Error_State.Msg, Title='Url Error', $
      /Error)
    Print, !Error_State.Msg
    Return
  Endif
    
  Case 1 Of
    Keyword_Set(Terra):Begin
      Prefix = 'Mod'
      Satellite = 'Terra'      
      Break
    End
    Keyword_Set(Aqua):Begin
      Prefix = 'Myd'
      Satellite = 'Aqua'     
      Break
    End
    Else:Return   
  Endcase
  Productname = Keyword_Set(Productname) ? Productname : '021km'
  
  Site = 'Ftp://Ladsweb.Nascom.Nasa.Gov'
  Jday = Julday(Month,Day,Year,0,0,0) - Julday(1,1,Year,0,0,0)
  Format = '("Geometa/6/'+Satellite+'/",I4,"/","'+Prefix+'03_",I4,"-",I02,"-",I02,".Txt")
  Dir_Fmt = '("/Alldata/5/","'+Prefix+Productname+'/",I4,"/",I03,"/")'
  
  Url = String([Year,Year,Month,Day],Format=Format)
  Dir = Site+ String([Year,Jday],Format = Dir_Fmt)       
      
  ; Create A New Url Object
  Ourl = Obj_New('Idlneturl',$
    Callback_Function ='Ddcall',$
    Url_Scheme = 'Ftp',$
    Url_Host = 'Ladsweb.Nascom.Nasa.Gov',$
    Url_Path = Url,$
    Url_Username = 'Anonymous',$
    Url_Password = '',$
    Ftp_Connection_Mode = 0)
  
  
  Geometa = Ourl->Get( /String_Array ) 
  Flist = Dir + Ourl->Getftpdirlist(Url=Dir,/Short)  
  
  Ourl->Closeconnections  
  Obj_Destroy, Ourl

End
;-----------------------------------------------------------------

Function Ddcall, Status, Progress, Data
  Print, Status
  Return, 1
End
;-----------------------------------------------------------------

Pro Add_Download,Url

  Othunder = Obj_New('Idlcomidispatch$Progid$Thunderagent_Agent');
  
  If Obj_Valid(Othunder) Then Begin
    For I = 0,N_Elements(Url)-1 Do Othunder->Addtask,Url[I],"","","","",1,0,5
    Othunder->Committasks,1
    Obj_Destroy ,Othunder
  Endif
End
;-----------------------------------------------------------------

Function Inside, X, Y, Xpts, Ypts, Index=Index

    On_Error, 1

    Sx = Size(Xpts)
    Sy = Size(Ypts)
    If (Sx[0] Eq 1) Then Nx=Sx[1] Else Message, 'X Coordinates Of Polygon Not A Vector.'
    If (Sy[0] Eq 1) Then Ny=Sy[1] Else Message, 'Y Coordinates Of Polygon Not A Vector.'
    If (Nx Eq Ny) Then N = Nx Else Message, 'Incompatable Vector Dimensions.'

    ; Close The Polygon.
    Tmp_Xpts = [Xpts, Xpts[0]]
    Tmp_Ypts = [Ypts, Ypts[0]]

    ; Set Up Counters.
    I = Indgen(N)
    Ip = Indgen(N)+1

    Nn = N_Elements(X)
    X1 = Tmp_Xpts(I)  # Replicate(1,Nn) - Replicate(1,N) # Reform([X],Nn)
    Y1 = Tmp_Ypts(I)  # Replicate(1,Nn) - Replicate(1,N) # Reform([Y],Nn)
    X2 = Tmp_Xpts(Ip) # Replicate(1,Nn) - Replicate(1,N) # Reform([X],Nn)
    Y2 = Tmp_Ypts(Ip) # Replicate(1,Nn) - Replicate(1,N) # Reform([Y],Nn)

    Dp = X1*X2 + Y1*Y2 ; Dot-Product
    Cp = X1*Y2 - Y1*X2 ; Cross-Product
    Theta = Atan(Cp,Dp)

    Ret = Replicate(0l, N_Elements(X))
    I = Where(Abs(Total(Theta,1)) Gt 0.01, Count)
    If (Count Gt 0) Then Ret(I)=1

    ; Make This A Scalar Value If There Is Only One Value.
    If (N_Elements(Ret) Eq 1) Then Ret=Ret[0]

    ; If The Index Keyword Is Set, Then Return Indices.
    If (Arg_Present(Index)) Then Ret=(Indgen(/Long, N_Elements(X)))(Where(Ret Eq 1))

    Return, Ret

End
```