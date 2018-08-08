# coding:utf-8
#
from xml.dom.minidom import parse
import codecs
# 获取 python节点下得所有id属性
def getTagId():
    # 获取test.xml文档对象
    doc = parse("test.xml")
    f=file('d:/test.xml', 'w')
    
    for node in doc.getElementsByTagName("symbol"):
        # 获取标签ID属性
        width = float(node.getAttribute("width"))
        height = float(node.getAttribute("height"))
        id = node.getAttribute("id")
        code = node.getAttribute("code")
        viewBox = ' '.join(map(lambda x: str(x),[width/2.0,height/2.0,width,height]))     
        node.setAttribute('viewBox',viewBox)
        node.setAttribute('name',id)
        node.setAttribute('id','sm'+code)
        # 打印输出
        print(viewBox)
    writer = codecs.lookup('utf-8')[3](f)
    doc.writexml(writer, encoding='utf-8')
    writer.close()
getTagId()




