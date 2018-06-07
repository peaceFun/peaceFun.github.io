---
title: WebGIS
date: 2017-06-04 20:28:03
tags: WebGIS
categories: Develop
---


## 缘起
在SuperMap学习工作中收获颇多：
1. 产品体系和企业愿景；
2. 团队敏捷开发和行业耕耘；
3. 国家科技支撑项目、4R管控培训和锦江之星白金卡。

记录WebGIS研发的点滴，整理行囊，轻装前行。
<!-- more -->
## SuperPy Tif影像拼接
### 影像像素位深检查
1. 采用开源库GDAL的gdalinfo.exe读取GeoTiff文件的信息，如类型、投影，范围等。
1. 采用DOS脚本遍历所有GeoTiff文件，输出各个GeoTiff文件的信息到日志。
1. 统计GeoTiff文件个数，Type=Byte的文件的个数。数目一致表明全部GeoTiff像素类型一致。
```DOS
for /f %i in ('dir /b /s d:\tifdata\*.tif ') do @(
    e:\gdal1.4.2\bin\gdalinfo.exe %i >> e:\tifstats.log
    )
```

### 影像拼接处理
采用SuperMapPy脚本处理影像拼接。先安装Python2.7.3和Deskpro环境。
流程如图
![](http://images2015.cnblogs.com/blog/583396/201510/583396-20151020151646630-204827930.gif)

脚本如下：
``` python
# coding: GB2312
 
#===================================================
#影像成批导入SuperMap UDB格式工具.
#基本流程:
#1、扫描目录，或者根据经纬度按照块的高宽生成文件列表。
#2、扫描存在的文件，获取最大的坐标范围。
#3、扫描存在的文件，获取像素格式。
#4、遍历文件列表，对于存在的文件追加到打开的数据库UDB中。
#5、创建金字塔索引，以加快显示速度。（可选的过程）
#===================================================
 
import sys
import string
import re
import os
import time
 
def getType(ext):
    if ext.lower() == 'tif':
        return 'fileTIF'
    elif ext.lower() == 'img':
        return 'fileIMG'
 
 
 
#匹配正则表达式，符合条件的append到datafiles，用于追加   
def walkPath(type, path):
    datafiles = []
    reMatch = '[\d\D]*.tif$'
    if type=='img':
        reMath = '[\d\D]*.img$'
   
    for root, dirs, files in os.walk(path):
        for file in files:
            if (re.match(reMatch,file)):
                datafiles.append(os.path.join(root, file))
    print len(datafiles)               
    return datafiles
 
def calcDatasetInfo(type, datafiles):
    L=[]       
    left=[]
    top=[]
    right=[]
    bottom=[]
    ratiox=[]
    ratioy=[]
 
    #获取每个影像文件的左右地理范围，保存到数组
    for file in datafiles:
        L= smu.GetImageGeoRef(type,file)
        print L
        l=float(L[0][0])
        t=float(L[0][1])
        r=float(L[0][2])
        b=float(L[0][3])
        w=int(L[1][0])
        h=int(L[1][1])
        x=(r-l)/w
        y=(t-b)/h
       
        left.append(l)
        right.append(r)
        top.append(t)
        bottom.append(b)
        ratiox.append(x)
        ratioy.append(y)
 
        #获取左右上下边界
        dLeft=min(left)
        dRight=max(right)
        dTop=max(top)
        dBottom=min(bottom)
       
        #获取分辨率，影像最小分辨率作为数据集分辨率
        dRatioX = min(ratiox)
        dRatioY = min(ratioy)
       
        #计算影像数据集宽度和高度
        nWidth = int((dRight-dLeft)/dRatioX)
        nHeight = int((dTop-dBottom)/dRatioY)
       
        #重新计算，保证分辨率正确
        dRight=dLeft+dRatioX*nWidth
        dBottom=dTop-dRatioY*nHeight
        L = [nWidth, nHeight, dLeft, dTop, dRight, dBottom]
   
    return L
 
def toDB(server, user, pwd, engType, fileType, path):
    files=[]
    files=walkPath(fileType, path)
    print len(files)
    if len(files)>0:
        L=[]
        L = calcDatasetInfo(fileType, files)
        pixType = smu.GetImagePixelFormatName(fileType, files[0])
 
        odsAlias='test'
        if len(L)==6:
            nWidth=L[0]
            nHeight=L[1]
            dLeft=L[2]
            dTop=L[3]
            dRight=L[4]
            dBottom=L[5]
            dtName='test'
            isOpen=smu.OpenDataSource(server,user,pwd, engType, odsAlias)
            smu.DeleteDataset(odsAlias, dtName)
            bCreate = smu.CreateDatasetRaster(odsAlias,dtName,
                    'Image', 'encDCT', pixType,nWidth,nHeight,
                    dLeft, dTop,dRight,dBottom,256)
            writeLog("log.log","calcDatasetInfo 成功")       
            for file in files:
                writeLog("log.log",file+"开始处理")   
                smu.AppendRasterFile(odsAlias,dtName,fileType, file)
                writeLog("log.log",file+"处理完毕\n\n")      
            bBuild=smu.BuildPyramid(odsAlias,dtName)#创建影像金字塔
            if bBuild == 1:
                print "创建金字塔成功"
            else:
                print "创建影像金字塔失败！"
            smu.CloseDataSource(odsAlias)
 
 
#=====================================
def writeLog(logPath, tmpstr):
    time_str = time.strftime("%Y-%m-%d %H:%M:%S ",time.localtime())
    logstr = str(tmpstr) + time_str +'\n'
    print(logstr)
    f = open(logPath, "a")
    f.write(logstr)
    f.close()
 
 
help =u"----------------------------------------------------------\n\
说明:可导入udb或oracle引擎\n\
导入到UDB用法: AppendRasterFile.py ugoPath tif c:/data\n\
导入到Oracle用法: AppendRasterFile.py ugoPath server user pwd tif c:/data\n\
----------------------------------------------------------\n"
 
if __name__=='__main__':
    if len(sys.argv)>2:
        ugo=sys.argv[1]
        if os.path.exists(ugo):
            sys.path.append(ugo)
            import smu
        else:
            print u'组件路径不存在.'
            sys.exit()
    else:
        print help
        sys.exit()
 
    if len(sys.argv) == 4:
        engType='sceUDB'
        fileType=sys.argv[2]
        fileType=getType(fileType)
        path=sys.argv[3]
       
        udb = path+'/test.udb'
        udd = path+'/test.udd'
        if os.path.exists(udb):
            os.remove(udb)
        if os.path.exists(udd):
            os.remove(udd)
 
        print 'toDB ing'
        toDB(udb, '', '', engType, fileType, path)
        smu.Exit()#清空环境，释放内存
    elif len(sys.argv) == 7:
        engType='sceOraclePlus'
        server=sys.argv[2]
        user=sys.argv[3]
        pwd=sys.argv[4]
        fileType=sys.argv[5]
        fileType=getType(fileType)
        path=sys.argv[6]
        toDB(server, user, pwd, engType, fileType, path)
        smu.Exit()#清空环境，释放内存
```



## 手工合成WMTS调用路径
### 动机
一般OGC WMTS地图只提供了xml描述，地图应用常常要合成WMTS完整的调用URL。
我们需要获知以下参数：

1. BaseURL:例如 “http://10.36.5.46:8080/iserver/services/map-JXDJS/wmts100”
1. SERVICE：“WMTS“，常量，服务类型，在此设置为WMTS
1. VERSION：“1.0.0“，常量，版本号，一般1.0.0
1. REQUEST：“GetTile“，常量，获取地图瓦片操作
1. LAYER：“SR“，变量，地图图层名。从xml中提取
1. FORMAT：“image/png“，变量，从xml中提取。一般是image/png或image/tile等
1. TILEMATRIXSET：“Custom_SR“，分块矩阵名称，从xml中提取。
1. OFFLEVEL：“0“，分辨率分级偏移，扩展字段，用于项目中叠加天地图地图。

### 步骤
1. 获取baseurl
首先先拿到WMTS描述xml路径，如http://localhost:8090/iserver/services/map-china400/wmts100
2. 获取xml文件内容
在浏览器中打开xml路径，如http://localhost:8090/iserver/services/
![](http://images2015.cnblogs.com/blog/583396/201510/583396-20151020092920286-906872499.png)
3. 提取参数
![](http://images2015.cnblogs.com/blog/583396/201510/583396-20151020092920833-1560746790.png)
4. 拼接url
url = 'http://10.36.5.46:8080/iserver/services/map-JXDJS/wmts100' + '?' +
'&SERVICE=WMTS'
'&VERSION=1.0.0'
'&REQUEST=GetTile'
'&LAYER=SR'
'&FORMAT=image/png'
'&TILEMATRIXSET=Custom_SR'
'&OFFLEVEL=0'

最终即为所得
url=http://10.36.5.46:8080/iserver/services/map-JXDJS/wmts100?&SERVICE=WMTS&VERSION=1.0.0&REQUEST=GetTile&LAYER=SR&FORMAT=image/png&TILEMATRIXSET=Custom_SR&OFFLEVEL=0


## Leaflet 示例
### 动机
1. 加载本地png瓦片
1. 加载GeoJson
1. 点要素自动聚类

### 源码
```html
<!DOCTYPE html>
<html>
<head>
    <title>Leaflet debug page</title>
    <link rel="stylesheet" href="../dist/leaflet.css" />
    <script src="../dist/leaflet.js"></script>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="screen.css" />
    <link rel="stylesheet" href="../dist/MarkerCluster.css" />
    <link rel="stylesheet" href="../dist/MarkerCluster.Default.css" />
    <script src="../dist/leaflet.markercluster-src.js"></script>
    <script type="text/javascript" src="geojson-sample.js"></script>
</head>
<body>
    <div id="map"></div>
    <span>Mouse over a cluster to see the bounds of its children and click a cluster to zoom to those bounds</span>
    <script type="text/javascript">
        var geoJsonData = {
            "type": "FeatureCollection", 
            "features": [
                { "type": "Feature", "id":"1", "properties": { "address": "2"   }, "geometry": { "type": "Point", "coordinates": [113.2209316333,31.2210922667 ] } },
                { "type": "Feature", "id":"2", "properties": { "address": "151" }, "geometry": { "type": "Point", "coordinates": [114.2238417833,31.20975435   ] } },
                { "type": "Feature", "id":"3", "properties": { "address": "21"  }, "geometry": { "type": "Point", "coordinates": [112.2169955667,31.218193     ] } },
                { "type": "Feature", "id":"4", "properties": { "address": "14"  }, "geometry": { "type": "Point", "coordinates": [112.2240856667,31.2216963    ] } },
                { "type": "Feature", "id":"5", "properties": { "address": "38B" }, "geometry": { "type": "Point", "coordinates": [113.2196982333,31.2188702167 ] } },
                { "type": "Feature", "id":"6", "properties": { "address": "38"  }, "geometry": { "type": "Point", "coordinates": [113.2209942   ,31.2192782833 ] } }
            ]
        };
        <!-- var mymap = L.map('map').setView([31, 113], 10); -->
        var tiles = L.tileLayer('http://localhost/roadmap/{z}/{x}/{y}.png', {
            maxZoom: 15,
            attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
        }),latlng = L.latLng(31, 113);
        var map = L.map('map', {center: latlng, zoom: 10, layers: [tiles]});
        var geojson = L.geoJson(geoJsonData, {
            style: function (feature) {
                return {color: feature.properties.color};
            },
            onEachFeature: function (feature, layer) {
                var popupText = 'geometry type: ' + feature.geometry.type;
                if (feature.properties.address) {
                    popupText += '<br/>address: ' + feature.properties.address;
                }
                layer.bindPopup(popupText);
            }
        });
        geojson.addLayer(new L.Marker(new L.LatLng(31.745530718801952, 113.194091796875)));
        var eye1 = new L.Marker(new L.LatLng(30.7250783020332547, 111.8212890625));
        var eye2 = new L.Marker(new L.LatLng(30.7360637370492077, 113.2275390625));
        var nose = new L.Marker(new L.LatLng(31.3292264529974207, 112.5463867187));
        var mouth = new L.Polygon([
            new L.LatLng(30.3841426927920029, 111.7333984375),
            new L.LatLng(30.6037944300589726, 111.964111328125),
            new L.LatLng(31.6806671337507222, 112.249755859375),
            new L.LatLng(31.7355743631421197, 112.67822265625),
            new L.LatLng(31.5928123762763,    113.0078125),
            new L.LatLng(30.3292264529974207, 113.3154296875)
        ]);
        var markers = L.markerClusterGroup();
        markers.addLayer(geojson).addLayers([eye1,eye2,nose,mouth]);
        map.addLayer(markers);
    </script>
</body>
</html>
```

## 江西水利一张图调用示例

### 源码 
```html
<head>   
     <meta http-equiv="content-type" content="text/html; charset=utf-8">
    <title>江西地图服务调用测试</title>
    <!--引用需要的脚本-->
    <script src="./libs/SuperMap.Include.js"></script>
    <script type="text/javascript">
    //声明变量map、layer、url
    function init()
    {    
        var map, layer;
        map = new SuperMap.Map("map",{controls: [                      
            new SuperMap.Control.ScaleLine(),
            new SuperMap.Control.Zoom(),
            new SuperMap.Control.Navigation({
                dragPanOptions: {
                                    enableKinetic: true
                                }
            })]
        });
        // 多个图层叠加，设置allOverlays开关为true
        map.allOverlays = true;  
        //当前图层的分辨率数组信息,和matrixIds一样，
        // 需要用户从wmts服务获取并明确设置,resolutions数组和matrixIds数组长度相同
        var scales=[2.958293554545656E8,
                    1.479146777272828E8,
                    7.39573388636414E7,
                    3.69786694318207E7,
                    1.848933471591035E7,
                    9244667.357955175   ,
                    4622333.678977588   ,
                    2311166.839488794   ,
                    1155583.419744397   ,
                    577791.7098721985   ,
                    288895.85493609926  ,
                    144447.92746804963  ,
                    72223.96373402482   ,
                    36111.98186701241   ,
                    18055.990933506204  ,
                    90279.95466753103   ,
                    4513.997733376551   ,
                    2256.998866688275   ,
                    1128.499433344138   ,
                    564.2497166720688];
        // SuperMap发布的    wmtsTDT接口的地图服务，设置对应的matrixID和resolution数组        
        var matrixIds=[],temp,resolutions=[];
        for(var i=6;i<scales.length;i++){
            temp=SuperMap.Util.getResolutionFromScaleDpi(scales[i],96,"degree",6378137);
            resolutions.push(temp);
            matrixIds[i-6]={identifier:i};//天地图的identifier是从1开始的
        }
        
        //河流图层
        layer0 = new SuperMap.Layer.WMTS({
              url: "http://10.36.5.46:8080/iserver/services/map-JX_LINE/wmtsTDT",
              layer: "LINE_V",
              style: "default",
              matrixSet: "Custom_LINE_V",
              format: "image/png",
              resolutions:resolutions,
              matrixIds:matrixIds,
              opacity: 1,
              requestEncoding:"KVP"});
        // 湖泊图层      
        layer1 = new SuperMap.Layer.WMTS({
              url: "http://10.36.5.46:8080/iserver/services/map-JX_LAKE/wmtsTDT",
              layer: "LAKE_V",
              style: "default",
              matrixSet: "Custom_LAKE_V",
              format: "image/png",
              resolutions:resolutions,
              matrixIds:matrixIds,
              opacity: 1,
              requestEncoding:"KVP"});
        
        // 天地图分辨率resolution数组和matrixID数组
        matrixSetTDT = [];
        resolutionsTDT = [];        
        for(var i=6;i<17;i++){
            temp=SuperMap.Util.getResolutionFromScaleDpi(scales[i],96,"degree",6378137);
            resolutionsTDT.push(temp);
            matrixSetTDT[i-6]={identifier:i+1};//天地图的identifier是从1开始的
        }    
        // 天地图行政界线底图服务
        layer2 = new SuperMap.Layer.WMTS({
              url: "http://10.36.5.70:9010/ZHL140325/wmts",
              layer: "vec20140318",
              style: "vec20140318",
              matrixSet: "Matrix_0",
              format: "image/tile",
              resolutions:resolutionsTDT,
              matrixIds:matrixSetTDT,
              opacity: 1,
              requestEncoding:"KVP"});
        // 天地图交通底图服务
        layerJT = new SuperMap.Layer.WMTS({
              url: "http://10.36.5.70:9010/JTL140325/wmts",
              layer: "Road325",
              style: "Road325",
              matrixSet: "Matrix_0",
              format: "image/tile",
              resolutions:resolutionsTDT,
              matrixIds:matrixSetTDT,
              opacity: 1,
              requestEncoding:"KVP"});
        // 天地图行政界线底图服务
        layerXZ = new SuperMap.Layer.WMTS({
              url: "http://10.36.5.70:9010/ZHL140325/wmts",
              layer: "vec20140318",
              style: "vec20140318",
              matrixSet: "Matrix_0",
              format: "image/tile",
              resolutions:resolutionsTDT,
              matrixIds:matrixSetTDT,
              opacity: 1,
              requestEncoding:"KVP"});
        //    行政注记 （影像）  
        layerPOI7_14 = new SuperMap.Layer.WMTS({
              url: "http://10.36.5.70:9010/POI7_17/wmts",
              layer: "POI7_14",
              style: "POI7_14",
              matrixSet: "Matrix_0",
              format: "image/tile",
              resolutions:resolutionsTDT,
              matrixIds:matrixSetTDT,
              opacity: 1,
              requestEncoding:"KVP"});
        //     天地图影像底图服务 
        layerIMGL7_L17s = new SuperMap.Layer.WMTS({
              url: "http://10.36.5.70:9010/IMGL7_L17/wmts",
              layer: "IMGL7_L17s",
              style: "IMGL7_L17s",
              matrixSet: "Matrix_0",
              format: "image/tile",
              resolutions:resolutionsTDT,
              matrixIds:matrixSetTDT,
              opacity: 1,
              requestEncoding:"KVP"});
        //       天地图行政注记（矢量）
        layerPoi325 = new SuperMap.Layer.WMTS({
              url: "http://10.36.5.70:9010/ZHLZJ140325/wmts",
              layer: "Poi325",
              style: "Poi325",
              matrixSet: "Matrix_0",
              format: "image/tile",
              resolutions:resolutionsTDT,
              matrixIds:matrixSetTDT,
              opacity: 1,
              requestEncoding:"KVP"});
            
                  
        //矢量底图          
        map.addLayers([layerXZ ,layer0 ,layer1 ,layer2 ,layerJT ,layerPoi325 ]);      
        //影像底图
        <!-- map.addLayers([layerIMGL7_L17s,layer0 ,layer1 ,layer2 ,layerJT, layerPOI7_14  ]);       -->
        map.setCenter(new SuperMap.LonLat(114, 26), 0);          
    }
    </script>
    
    
</head>
<body onload="init()">
    <!--地图显示的div-->
    <div id="map" width="100%" height="100%" >             
    </div>    
</body>  
```

![](http://images2015.cnblogs.com/blog/583396/201512/583396-20151207165038511-1521268624.png)