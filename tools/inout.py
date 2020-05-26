import io ,os ,time, platform,socket,netdata,logging
from baseio import *

class INOUT:
    escape_tag = '\\'
    max_block = 1024*1024
    send_block = 1024*16
    block_end_tag = '.'
    block_head_tag = '+'
    block_single_tag = '-'
    
    unpack_map = {
            'B':netdata.unpack_number,
            'b':netdata.unpack_number,
            'H':netdata.unpack_number,
            'h':netdata.unpack_number,
            'L':netdata.unpack_number,
            'l':netdata.unpack_number,
            'Q':netdata.unpack_number,
            'q':netdata.unpack_number,
            'd':netdata.unpack_float,
            's':netdata.unpack_block,
            'c':netdata.unpack_block,
            'M':netdata.unpack_block,
            'm':netdata.unpack_block,
            #'U':netdata.unpack_bignumber,
            #'u':netdata.unpack_bignumber,
            
    }
    def __init__(self,obj=None,*args,**kwargs):
        self.handle = CreateIO(obj,*args,**kwargs)
        self.tmp = tmp.TMP()#注意一下 可能要修改 
    def create_output_handle(self,tag,size):#還有要修改的
        if size > self.send_block:
            fileName = self.tmp.get_tempname(subdir = 'INOUT')
            if tag in ['m','M']:
                return INOUT_INT(fileName,tag)
            return INOUT_FILE(fileName,tag,temp=True)
        return MemIO()
    def _read_low_level(self,n):
        retval = self.handle.read(n)
        #retval = bytes([i ^ 0xCC for i in retval])
        return retval
    def _write_low_level(self,d):
        #d = bytes([i ^ 0xCC for i in d])
        self.handle.write(d)
    def _get_bytes(self):#要再檢查
        result = b''
        while True:
            b = self._read_low_level(1)
            if b is None:
                break
            result += b
            if b[0] & 0x80 ==0:
                break
        return result
    def read_tag(self,n = 1):
        tag = self.handle.read(n)
        if isinstance(tag,bytes):
            tag = tag.decode('utf-8')
        return tag
    def write_tag(self,tag):
        if isinstance(tag,str):
            tag = tag.encode('utf-8')
        self.handle.write(tag)
    def write_escape(self):
        self.write_tag(self.escape_tag)
    def read(self):
        escape = False
        tag = self.read_tag()
        if tag == self.escape_tag:
            escape = True
            tag = self.read_tag()
        if tag not in self.unpack_map:
            raise InOutUnKnownTag(tag)
        unpack_func = self.unpack_map[tag]
        
        size = netdata.num_size_map.get(tag,-1)
        if size > 0:
            n_bytes = self._read_low_level(size)
            return netdata.unpack_number(tag,n_bytes)
        #elif tag in ['U','u']:
        #    n_bytes = self._get_bytes()
        #    return netdata.unpack_bignumber(tag,n_bytes)
        numlen_tag = self.read_tag()
        if numlen_tag not in netdata.num_size_map:
            raise InOutUnKnownTag(numlen_tag)
            
        numlen_size = netdata.num_size_map.get(numlen_tag)
        
        numlen_bytes = self._read_low_level(numlen_size)
        size = netdata.unpack_number(numlen_tag,numlen_bytes)
        
        output_handle = self.create_output_handle(tag,size)
        loop_flag = False
        while True:
            block_tag = self.read_tag()
            if block_tag == self.block_end_tag:
                break
            elif block_tag == self.block_head_tag:
                loop_flag = True
                numlen_tag2 = self.read_tag()
                numlen_size2 = netdata.num_size_map.get(numlen_tag)
                numlen_bytes2 = self._read_low_level(numlen_size2)
                block_size = netdata.unpack_number(numlen_tag2,numlen_bytes2)
            elif block_tag == self.block_single_tag and not loop_flag:
                block_size = size
            else:
                raise InOutUnKnownTag(block_tag)
            
        
            if size > self.max_block:
                raise InOutBlockSize(block_size)
            b = self._read_low_level(block_size)
            output_handle.write(b)
            if not loop_flag:
                break
        data = output_handle.close()
        if isinstance(data,bytes):
            data = unpack_func(tag,data)
        
        
        if  escape:
            raise InOutEscape(data)
        return data
        
            
    def write(self,obj):
        n_bytes = None
        if isinstance(obj,int):
            tag,obj_bytes = netdata.pack_number(obj)
            if tag:
                self.write_tag(tag)
                self._write_low_level(obj_bytes)
                return
        if isinstance(obj,float):
            tag,obj_bytes = netdata.pack_float(obj)
            self.write_tag(tag)
            self._write_low_level(obj_bytes)
            return
        if isinstance(obj,(str,bytes,int)):
            tag,obj_bytes = netdata.pack_block(obj)
            input_handle = MemIO(obj_bytes)
        elif isinstance(obj,INOUT_FILE):
            tag ,obj_bytes = 'c',obj
            input_handle = obj
        else:
            raise InOutUnKnownTag(obj)
        size_tag,size_bytes = netdata.pack_number(len(obj_bytes))
        size = len(obj_bytes)

        #if not size_tag:
        #    size_tag,sizes = netdata.pack_bignumber
        #    if not size_tag:
        #        raise ValueError('can\'t pack len \' %d\'' % len(obj_bytes))
            
        if not size_tag:
            raise ValueError('can\'t pack len \' %d\'' % len(obj_bytes))
            
        self.write_tag(tag)
        self.write_tag(size_tag)
        self._write_low_level(size_bytes)
        #self._write_low_level(obj_bytes)
        if size <= self.send_block:
            b = input_handle.read(size)
            self.write_tag(self.block_single_tag)
            self._write_low_level(b)
            return
        while True:
            b = input_handle.read(self.send_block)
            if not b:
                break
            self.write_tag(self.block_head_tag)
            size_tag2,size_bytes2 = netdata.pack_number(len(b))
            self.write_tag(size_tag2)
            self._write_low_level(size_bytes2)
            self._write_low_level(b)
        self.write_tag(self.block_end_tag)
        return
            
    def close(self):
        self.handle.close()
#-------------------------------------
#INPUT FILE
class INOUT_FILE:
    def __init__(self,fileName,tag = 'c',temp= False):
        self.fileName = fileName
        self.tag = tag
        self.handle = None
        self.tempFlag = temp
    def __len__(self):
        if os.path.exists(self.fileName):
            return os.path.getsize(self.fileName)
        return 0
    def read(self,n = 0):
        if not self.handle:
            mode = 'r' if self.tag == 's' else 'rb'
            self.handle = open(self.fileName,mode)
        if not n:
            n = os.path.getsize(self.fileName)
        return self.handle.read(n)
        
    def write(self,d):
        if not self.handle:
            print(4)
            dirname = os.path.dirname(self.fileName)
            if dirname and not os.path.exists(dirname):
                os.makedirs(dirname)
                #print('ffff')
            self.handle = open(self.fileName,'wb')
            print('do this')
        self.handle.write(d)
            
    def close(self):
        if self.handle:
            self.handle.close()
            self.handle = None
        return self
    def drop(self):
        if self.tempFlag and self.fileName:
            self.close()
            if os.path.exists(self.fileName):
                os.remove(self.fileName)
                self.fileName = None
class INOUT_INT:
    def __init__(self,tag = 'M'):
        self.tag = tag
        self.number = 0
    def read(self,n=0):
        return -self.number if self.tag == 'm' else self.number
    def write(self,d):
        length = len(d)
        incoming = int.from_bytes(d,'big')
        self.number = (self.number<< length *8)+incoming
    def close(self):
        return self.read()
def test_inout_int(n):
    tag,d = netdata.pack_block(n)
    ii = INOUT_INT(tag)
    for i in range(0,len(d),6):
        b = d[i:i+6]
        print(b)
        ii.write(b)
    i2 = ii.close()
    print(n)
    print(i2)
#n = 15616168264841914919489444444444488888888888
#test_inout_int(n)    
    

#=========
#except 區
#=========
class InOutException(Exception):
    pass
class InOutEscape(InOutException):
    pass
class InOutBlockSize(InOutException):
    pass
class InOutUnKnownTag(InOutException):
    pass
#--------------------------------------
