# coding:utf-8
#

import petl as etl
import os,sys,json,sqlite3,re,redis,uuid
from itertools import izip, starmap, imap
import operator,time,math

pool= redis.ConnectionPool(host='127.0.0.1',port=6379,decode_responses=True)

r=redis.Redis(connection_pool=pool)
r2=redis.Redis(connection_pool=pool)


#
# 双向字典

class BiDict(object):
    '''
    双向字典，用于存储多对多关联关系
    '''
    def __init__(self):
        self._uuid = uuid.uuid1()
        ## 正向字典
        self._dict = {}
        ## 反向字典
        self._invdict = {}
        
    def addkeyvalue(self,key,value):
        self._dict.setdefault(key,set()).add(value)
        self._invdict.setdefault(value,set()).add(key)
    
    def keys(self):
        return self._dict.keys()
    
    def values(self):
        return self._invdict.keys()
        
    def getkeys(self,value):
        return self._invdict.get(value,[])
        
    def getvalues(self,key):
        return self._dict.get(key,[])
    
    
    # 获取关联列表
    def getKeyKeyRel(self):
        ret = {}
        for k1 in self._dict:
            v1 = self._dict.get(k1,[])
            for k2 in v1:
                ret.setdefault(k1,set()).update(self._invdict.get(k2,[]))
            ret.get(k1).remove(k1)
        return ret
            
    def getValueValueRel(self):
        ret = {}
        for v1 in self._invdict:
            k1 = self._invdict.get(v1,[])
            for k2 in k1:
                ret.setdefault(v1,set()).update(self._dict.get(k2,[]))
            ret.get(v1).remove(v1)
        return ret
        
class BiDictRedis(object):
    '''
    双向字典，用于存储多对多关联关系
    '''
    def __init__(self):
        self._uuid = uuid.uuid1()
        ## 正向字典
        self._dict = {}
        ## 反向字典
        self._invdict = {}
        
    def addkeyvalue(self,key,value):
        self._dict.setdefault(key,set()).add(value)
        self._invdict.setdefault(value,set()).add(key)
    
    def keys(self):
        return self._dict.keys()
    
    def values(self):
        return self._invdict.keys()
        
    def getkeys(self,value):
        return self._invdict.get(value,[])
        
    def getvalues(self,key):
        return self._dict.get(key,[])
    
    
    # 获取关联列表
    def getKeyKeyRel(self):
        ret = {}
        for k1 in self._dict:
            v1 = self._dict.get(k1,[])
            for k2 in v1:
                ret.setdefault(k1,set()).update(self._invdict.get(k2,[]))
            ret.get(k1).remove(k1)
        return ret
            
    def getValueValueRel(self):
        ret = {}
        for v1 in self._invdict:
            k1 = self._invdict.get(v1,[])
            for k2 in k1:
                ret.setdefault(v1,set()).update(self._dict.get(k2,[]))
            ret.get(v1).remove(v1)
        return ret
class OidRidRel(object):
    def __init__(self):
        self._oidDict = {}
        self._ridDict = {}
    
    def add(self,tb,oid,rid):
        self._oidDict.setdefault(oid,{}).setdefault(tb,rid)
        self._ridDict.setdefault(rid,{'oid':oid,'tb':tb})
    
    def getRid(self,oid,tb):        
        return self._oidDict.get(oid,{}).get(tb,-1)        
        
    def get(self,key):
        vv = self._oidDict.get(key,{})
        k = vv.keys()[0]
        v = vv.values()[0]
        return k,v
        
    def getOidTb(self,rid):
        ro = self._ridDict.get(rid,{})
        oid = ro.get('oid',-1)
        tb = ro.get('tb','')
        return oid,tb
    
class NodeFinder:
    def __init__(self):
        self._ridRel = {}
        
    def __del__(self):
        self.cur.close()
        self.conn.close()
        
    def _initdb(self):
        self.conn = sqlite3.connect("F:\\仙桃中低压20180611\\仙桃中低压20180807-test.db")
        self.conn.text_factory = str
        self.cur = self.conn.cursor()
        
    def _getTableFields(self):
        self._fdDict = BiDict()
        self._tbIDDict = BiDict()
        sql = "select tbl_name from sqlite_master where tbl_name like 'T_TX_%'"
        t0 = list(etl.data(etl.fromdb(self.cur,sql)))  
        
        for idx in xrange(len(t0)):
            s = t0[idx]
            tbsql = "select * from {} limit 2".format(s[0])
            fd = etl.fieldnames(etl.fromdb(self.cur,tbsql))
            for field in fd:
                self._fdDict.addkeyvalue(s[0],field)
            self._tbIDDict.addkeyvalue(s[0],idx)

    def _getRowidRel(self):  
        bdzsql = ''' select oid from T_TX_ZNYC_DZ where sbzlx in (30000000) ''' #union all select oid from T_TX_ZNYC_DZ0 where sbzlx in (30000000) '''        
        self._bdzSet = set(etl.values(etl.fromdb(self.cur,bdzsql), 0))
 
        _RidDZHDict = BiDict()    
        dzfield = 'DZH'
        dztbs = self._fdDict.getkeys(dzfield)
        for tb in dztbs:
            sql = "select row,dzh from {tb} where length(dzh) > 15 ".format(tb=tb)
            dt = list(etl.data(etl.fromdb(self.cur,sql)))
            for row,dzh in dt:
                rid = self._getRowid(row,tb)
                dzh = self._getDZH(dzh)
                for dz in dzh:
                    if dz <= 0 :continue
                    _RidDZHDict.addkeyvalue(rid,dz)
            dt = None
        self._ridRel = _RidDZHDict.getKeyKeyRel()
        _RidDZHDict = None        
        
        dzsql = " select oid,row from T_TX_ZNYC_DZ where yxdw in ('D320B66EDF35400B983FB9DEEABB061F','83331E305C354A4BA528B9701CDF68EA','67F9C1FADB5949599C6A23B018FB6EC3','E59C0F0283D44B8B9F1504CD22D46613','ff80808160bb54520162be5396912713','2C2D16780C504B4CB7611D47CCCE99B1','ADE62BEBE59E4EA887DC1C90EB2B2B3A')"
        dzDict = dict(etl.data(etl.fromdb(self.cur,dzsql)))
        gtsql = "select oid,row from T_TX_DYSB_DYWLG where yxdw='D320B66EDF35400B983FB9DEEABB061F'"        
        dygtDict = dict(etl.data(etl.fromdb(self.cur,gtsql)))
        gtsql = "select oid,row from T_TX_ZWYC_WLG where yxdw='D320B66EDF35400B983FB9DEEABB061F'"
        gtDict = dict(etl.data(etl.fromdb(self.cur,gtsql)))
        
        yxgtsql = "select oid,row from T_TX_DYSB_DYYXGT where yxdw='D320B66EDF35400B983FB9DEEABB061F'"       
        dyyxgtDict = dict(etl.data(etl.fromdb(self.cur,yxgtsql)))
        yxgtsql = "select oid,row from T_TX_ZWYC_YXGT where yxdw='D320B66EDF35400B983FB9DEEABB061F'"  
        yxgtDict = dict(etl.data(etl.fromdb(self.cur,yxgtsql)))
        
        for tb in self._fdDict.getkeys('SSDZ'): 
            sql = "select row,oid,ssdz from {tb} ".format(tb=tb)  
            dt = list(etl.data(etl.fromdb(self.cur,sql)))
            for row,oid,ssdz in dt:
                rid = self._getRowid(row,tb)
                subrid = self._getRowid(dzDict.get(ssdz,-1),'T_TX_ZNYC_DZ')
                self._ridRel.setdefault(rid,set()).add(subrid)                
            dt = None

        for tb in self._fdDict.getkeys('SSGT') :
            sql = "select row,oid,ssgt from {tb}  ".format(tb=tb)  
            dt = list(etl.data(etl.fromdb(self.cur,sql)))
            for row,oid,ssgt in dt:
                rid = self._getRowid(row,tb)
                if dyyxgtDict.get(ssgt,-1) > 0:
                    subrid = self._getRowid(dyyxgtDict[ssgt],'T_TX_ZWYC_WLG')  
                    self._ridRel.setdefault(rid,set()).add(subrid)
                elif yxgtDict.get(ssgt,-1) > 0:
                    subrid = self._getRowid(yxgtDict[ssgt],'T_TX_DYSB_DYWLG')
                    self._ridRel.setdefault(rid,set()).add(subrid) 
                else:
                    pass           
            dt = None
            
        for tb in self._fdDict.getkeys('SSWLG') :
            sql = "select row,oid,sswlg from {tb} ".format(tb=tb)  
            dt = list(etl.data(etl.fromdb(self.cur,sql)))
            for row,oid,sswlg in dt:
                rid = self._getRowid(row,tb)
                if gtDict.get(sswlg,-1) > 0 :                    
                    subrid = self._getRowid(gtDict[sswlg],'T_TX_ZWYC_WLG')
                    self._ridRel.setdefault(rid,set()).add(subrid) 
                elif dygtDict.get(sswlg,-1) > 0:
                    subrid = self._getRowid(dygtDict[sswlg],'T_TX_DYSB_DYWLG')
                    self._ridRel.setdefault(rid,set()).add(subrid) 
                else:
                    pass
            dt = None     
        
        dzDict     = None
        dygtDict   = None  
        gtDict     = None
        dyyxgtDict = None    
        yxgtDict   = None  
        
    def _resetFind(self):
        if len(self._ridRel) < 1:
            self._initdb()
            self._getTableFields()
            self._getRowidRel()
        self.cnt = 0
        self.done = False
        self.maxlen = 10000
        self.maxdepth = 200        
        self.res = []
        self.rids = set()
        self.path = set()
    
    def test(self):
        self._resetFind()
        #oid = self._oidRidRel._oidDict.keys()[5]
        #self.findLine(tb,oid)  
        
    def findLine(self,tb,oids):  
        self._resetFind()  
        rids = self._getRowidList(tb,oids)
        if len(rids) < 1 : return
        
        for idx in xrange(len(rids)):
            rid = rids[idx]
            oid = oids[idx]
            ticks = time.time()
            self._resetFind()  
            if self._deepSearch(rid):
                print 'BDZ found'
                self._toGeoJSON(oid) 
            #self._appendWlg()
            #self._appendDZ()
            tock = time.time() - ticks
            info = '='*10+'{tb} {}迭代次数: {},耗时：{}秒，寻找成功:{}'.format(oid,self.cnt,tock,self.done,tb=tb) + '='*10     + '\n'
            log(info)  
        
    def __isEnd(self,rowid,depth):
        flg = False
        
        while 1:
            self.cnt += 1
            if rowid in self._bdzSet:
                self.done = True
                flg = True
                break
                
            if self.cnt <= self.maxlen:                
                break
        
            if self.maxdepth > depth:                
                break
        
            flg = True            
            break
            
        return flg
        
    def _deepSearch(self,rid,depth=0):          
        flg = False
        for s in [1]:
            if rid < 0 or rid in self.rids or self.__isEnd(rid,depth):                        
                break                
            self.rids.add(rid)
            rids = self._ridRel.get(rid,set())
            for subrid in rids:                             
                flg = flg or self._deepSearch(subrid,depth+1)            
            flg = flg or self.done
            
            if flg: self.path.add(rid)
        return flg
        
    def _broadSearch(self,rid):
        pass

    def _appendWlg(self):
        wlgfield = 'SSWLG'
        wlgtbs = self._fdDict.getkeys(wlgfield)
        #for tb in wlgtbs:
        #    pass

    def _appendDZ(self):
        dzfield = 'SSDZ'
        dztbs = self._fdDict.getkeys(dzfield)
        #for tb in dztbs:
        #    pass
    
    def _tb2geojson(self,sql,geofield,tb):    
        t0 = etl.fromdb(self.cur,sql)
        t0 = etl.convert(t0,geofield,lambda v: json.loads(v))
        dt = etl.dicts(t0)
        ret = []
        for item in dt:
            vo = {}
            vo['geometry'] = item[geofield]
            vo['type']='Feature'
            item.pop(geofield)
            vo['properties'] = {k:v for k,v in item.items() if k != geofield}
            vo['properties'].setdefault('TB',tb)
            
            ret.append(vo)
        t0 = None
        dt = None
        
        return ret
    def _toGeoJSON(self,firstoid):        
        ret = []
        print '{}.json is generating'.format(firstoid)
        params = self._getOidTbList(self.path)      
        geotb = self._fdDict.getkeys('SHAPE')
        for k,v in params.items():
            if not k in geotb: continue                
            sql = 'select * from {} where row in {}'.format(k,tuple(v)).replace(',)',')')            
            ret.extend(self._tb2geojson(sql,'SHAPE',k))
        
        gvo = {"type": "FeatureCollection",    "features":ret}
        
        f = open('f:\\{}.json'.format(firstoid),'wb')
        f.write(json.dumps(gvo))        
        f.close()
            
        params = None
        ret = None
    
    def _getDZH(self,dzhsrc):                    
        ret = map(getDZ,re.findall(r'.{16}',dzhsrc))
        return ret
        
    def _getRowidList(self,tb,oids):
        sql = 'select row from {tb} where oid in ({oidlist})'.format(tb=tb,oidlist=','.join(map(lambda x: str(x),oids)))
        log(sql)
        rows = list(etl.values(etl.fromdb(self.cur,sql), 0))
        rids = map(lambda x:self._getRowid(x,tb) ,rows)
        return rids
        
    def _getRowid(self,rowidx,tb):
        rid = rowidx*200 + list(self._tbIDDict.getvalues(tb))[0]
        return rid
        
    def _getOidTbList(self,rowids):
        ret = {}
        for rid in rowids:
            tb = rid % 200
            tbname = list(self._tbIDDict.getkeys(tb))[0]
            row = int(rid / 200)
            ret.setdefault(tbname,set()).add(row)
        return ret       

def log(s):
    print s

def getDZ(instr):
    ss = list('0123456789ABCDEF')
    zz = [s for s in xrange(16) ]
    vdict = dict(zip(ss,zz))

    pp = [(s + (-1)**s) for s in xrange(len(instr))]
    p1 = [16**s for s in pp]
    s0 = [vdict[s] for s in list(instr)]
    z0 = sum(starmap(operator.mul, izip(p1,s0)))

    return z0


if __name__ == '__main__':
    #foo("formal_args",121,'dfaoe',[323,12,4])
    
    t = NodeFinder()
    #t.test()
    t.findLine('T_TX_DYSB_DYYHJRD',[9501674,5687618,6790131,9564527,9442742])
    t.findLine('T_TX_YXSB_JLX',[40773158,40094131,40892686, 8791852])
    t.findLine('T_TX_DYSB_QZJ',[3969793,5482908,4178279])
    t.findLine('T_TX_DYSB_QZJ',[3969793])