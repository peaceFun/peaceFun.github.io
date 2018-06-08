---
title: Office VBA例子
date: 2017-04-25 13:13:06
tags: [word,vba]
categories: Develop
cover_picture: images/10.jpg
---

## 替换多个Word文件中的字符串
### 动机
需替换多个doc文件中的地名等字符串，人工处理慢且容易出错。

<!--more-->
### 源码
``` vb

' -------------------------------------------------------------------------
' 用来替换文件夹多个doc中的字符串
' 作者：wishmo@tom.com
' 日期：2017年4月25日

Function docReplace(fullpath, searchStr, replaceStr)
    Application.ScreenUpdating = False
    Dim myDoc As Document
    Set myDoc = Documents.Open(FileName:=(fullpath))
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = searchStr
        .Replacement.Text = replaceStr
        .Forward = True
        .Wrap = wdFindAsk
        .Format = False
        .MatchCase = False
        .MatchWholeWord = False
        .MatchByte = True
        .MatchWildcards = False
        .MatchSoundsLike = False
        .MatchAllWordForms = False
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    myDoc.Save
    myDoc.Close
    Set myDoc = Nothing
    Application.ScreenUpdating = True
End Function

' ------------------------------------------------------------------------
Function getDir()
    Dim myPath As String
    ' 选择目标文件夹
    With Application.FileDialog(msoFileDialogFolderPicker)
        .Title = "选择目标文件夹"
        If .Show = -1 Then
            myPath = .SelectedItems(1)
        Else
            Exit Function
        End If
    End With
    getDir = myPath
End Function
' ---------------------------------------------------------------------------
' 批量替换多个doc中的字符串
' --------------------------------------------------------------------
Sub MultiDocReplace()
    Application.ScreenUpdating = True
    Dim fpath As String, myPath As String
    myPath = getDir()
    docFile = Dir(myPath & "\*.doc*", vbDirectory)    
    Do While docFile <> ""   ' 开始循环。
        fpath = myPath & "\" & docFile
        Call docReplace(fpath, "江苏", "安徽")
        docFile = Dir
    Loop
    Application.ScreenUpdating = True
End Sub
```

## 根据清单生成GTD事项
### 动机
从工作表清单生成重要、紧急、次要、琐事4类事项
### 源码
```vb
' --------------------------------------------------------------------------------
' 用来从清单生成紧急、重要、次要、琐事4类清单，督促办理
' 作者：wishmo@tom.com
' 日期：2017年4月25日
' --------------------------------------------------------------------------------
' Sheet1第一行表头，至少包括以下几列
' 序号    主题    分项任务    详细说明    结果描述    联络人    提出时间    截止时间    完成时间    重要    紧急    备注
' --------------------------------------------------------------------------------
' 从本工作表生成数据库连接
' 作者：wishmo@tom.com
' 日期：2017年4月25日
' --------------------------------------------------------------------------------
Function connect()
    Dim conn As Object, PathStr As String, strConn As String, strSQL As String
    Set conn = CreateObject("ADODB.Connection")
    PathStr = ThisWorkbook.FullName   '设置工作簿的完整路径和名称
    Select Case Application.Version * 1    '设置连接字符串,根据版本创建连接
    Case Is <= 11
        strConn = "Provider=Microsoft.Jet.Oledb.4.0;Extended Properties=excel 8.0;Data source=" & PathStr
    Case Is >= 12
        strConn = "Provider=Microsoft.ACE.OLEDB.12.0;Data Source=" & PathStr & ";Extended Properties=""Excel 12.0;HDR=YES"";"""
    End Select
    conn.Open strConn
    Set connect = conn
End Function
' --------------------------------------------------------------------------------
' 删除工作表、新建工作表
' 作者：wishmo@tom.com
' 日期：2017年4月25日
' --------------------------------------------------------------------------------
Function renewSheet(shtname)
    On Error Resume Next
    Application.DisplayAlerts = False
    Set sht = Sheets(shtname)
    If Not IsNull(sht) Then
        sht.Delete
    End If
    Set sht = Sheets.Add()
    sht.Name = shtname
    Set renewSheet = sht
    Application.DisplayAlerts = True
End Function
' --------------------------------------------------------------------------------
' 在指定的工作表中填充4类事项
' 作者：wishmo@tom.com
' 日期：2017年4月25日
' --------------------------------------------------------------------------------
Sub divide(conn, targetShtName)
    'On Error Resume Next
    Dim firstrow As Integer, rst As Object
    Dim title(5) As String, cindex(5) As Integer, mode As Integer, i As Integer
    Dim SQL(5) As String, pre As String
    pre = "select 序号,主题,分项任务,详细说明,结果描述,联络人,提出时间,截止时间,备注 from [Sheet1$A1:M100] where 分项任务 is  not null and 完成时间 is null and "
    SQL(0) = pre + " len(重要) > 0 and len(紧急) >0"
    SQL(1) = pre + " len(重要) > 0  and 紧急 is null"
    SQL(2) = pre + " 重要 is null and len(紧急) > 0 "
    SQL(3) = pre + " 重要 is null and 紧急 is null "
    SQL(4) = "select 序号,主题,分项任务,详细说明,结果描述,联络人,提出时间,截止时间,备注 from [Sheet1$A1:M100] where 完成时间 is not null"
    
    cindex(0) = 3
    cindex(1) = 5
    cindex(2) = 6
    cindex(3) = 8
    cindex(4) = 10
    
    title(0) = "紧急"
    title(1) = "重要"
    title(2) = "琐事"
    title(3) = "小事"
    title(4) = "完结"
    
    
    Debug.Print targetShtName
    Set rst = CreateObject("ADODB.Recordset")
    Set sht = Sheets(targetShtName)
    firstrow = 1
    
    With sht
        rst.CursorLocation = 3
        For mode = 0 To 4 Step 1
            rst.Open SQL(mode), conn, adOpenKeyset
            
            If rst.Fields.Count > 1 Then
                Range(Cells(firstrow + 1, 1), Cells(firstrow + 1, rst.Fields.Count)).Merge
                .Cells(firstrow + 1, 1).Value = title(mode)
                .Cells(firstrow + 1, 1).RowHeight = 35
                .Cells(firstrow + 1, 1).HorizontalAlignment = xlCenter    ' 居中
                .Cells(firstrow + 1, 1).Interior.ColorIndex = cindex(mode)
                .Cells(2 + firstrow, i + 1).ColumnWidth = 10
                For i = 0 To rst.Fields.Count - 1    '填写标题
                    fdname = rst.Fields(i).Name
                    .Cells(2 + firstrow, i + 1).ColumnWidth = getWidth(fdname)
                    .Cells(2 + firstrow, i + 1).EntireRow.AutoFit
                    .Cells(2 + firstrow, i + 1) = fdname
                Next i
            End If
            
            ' 复制选择集数据
            Range("A" & (firstrow + 3)).CopyFromRecordset rst
            
            firstrow = firstrow + rst.RecordCount + 4
            
            rst.Close
        Next mode
        ' .Cells.EntireColumn.AutoFit  '自动调整列宽
        .Cells.WrapText = True
        
        Set rst = Nothing
    End With
End Sub
' --------------------------------------------------------------------------------
' 根据字段名获得列宽
' 作者：wishmo@tom.com
' 日期：2017年4月25日
' --------------------------------------------------------------------------------
Function  getWidth(fdname)
    dim wid as Integer
    wid = 10
    Select Case fdname
        Case "分项任务"
            wid = 20
        Case "详细说明"
            wid = 20
        Case "结果描述"
            wid = 30
        Case "备注"
            wid = 15
        Case Else
            wid = 10
    End Select
    getWidth = wid
End Function
' --------------------------------------------------------------------------------
' 用来从清单生成紧急、重要、次要、琐事4类清单，督促办理
' 作者：wishmo@tom.com
' 日期：2017年4月25日
' --------------------------------------------------------------------------------
Sub GTD()
    Dim conn As Object, rst As Object
    
    Set conn = connect()
    Set sht = renewSheet("4象限")
    Call divide(conn, "4象限")
    conn.Close
    Set conn = Nothing
    
End Sub
```

## 合并重复单元格
### 动机
要将内容相同的相邻单元格合并为1个
### 源码
```vb
Sub MergeCellsWithSameValue()
    Application.ScreenUpdating = False
    Application.DisplayAlerts = False
    
    Dim r As Integer
    Dim c As Integer
    
    Sheets("Sheet1").Activate
    
    
    For r = Sheet1.UsedRange.Rows.Count To 1 Step -1
        For c = Sheet1.UsedRange.Columns.Count To 1 Step -1
            If Not IsEmpty(Cells(r, c)) Then
                If Not IsNumeric(Left(Cells(r, c).Value, 1)) Then
                    If r > 1 Then
                        If Not IsEmpty(Cells(r - 1, c).Value) Then
                            If Cells(r, c) = Cells(r - 1, c) Then
                                Range(Cells(r, c), Cells(r - 1, c)).Merge
                                GoTo NEXTLOOP
                            End If
                        End If
                    End If
                    If c > 1 Then
                        If Not IsEmpty(Cells(r, c - 1).Value) Then
                            If Cells(r, c) = Cells(r, c - 1) Then
                                Range(Cells(r, c), Cells(r, c - 1)).Merge
                                GoTo NEXTLOOP
                            End If
                        End If
                    End If
                End If
            End If
NEXTLOOP:
        Next
    Next
    
    Sheet1.UsedRange.EntireRow.AutoFit
    Sheet1.UsedRange.EntireColumn.AutoFit
    Sheet1.UsedRange.HorizontalAlignment = xlCenter
    Sheet1.UsedRange.VerticalAlignment = xlCenter
    Application.DisplayAlerts = True
    Application.ScreenUpdating = True
    
End Sub
```