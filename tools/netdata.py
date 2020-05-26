#from tools.hexdump import *

from hexdump import *
import socket,os,struct

#=====================================
#通用工具
#=====================================
def number2tagsizen(n):#看數字適合的tag   
    n,num_size_list = (n,int_size_list) if n >= 0 else (-n,neg_size_list)
    n_size = byte_length(n)
    for tag,tag_size in num_size_list:
        if n_size <= tag_size:
            return tag,tag_size
    return None,None


#看數字長度是幾個byte,不到8自動補滿
def byte_length(n):
    return (n.bit_length()+7)>>3
#-------------------------------------




#=====================================
#int str byte區
#===========object====================
pack_block_tag = {#轉成byte後的tag
        str:(lambda n:'s'),
        bytes:(lambda n:'c'),
        int:(lambda n:('M' if n>= 0 else 'm')),
        }

pack_block_encoder = {#轉成byte的函數
        str:(lambda n: n.encode('utf-8')),
        bytes:(lambda n: n),
        int:(lambda n:(n).to_bytes(byte_length(n),'big') if n>=0 \
                else ((-n).to_bytes(byte_length(n),'big')))
        }
    
unpack_block_map = {#byte 轉成str byte int的函數  
        's': lambda n: n.decode('utf-8'),
        'c': lambda n: n,
        'm': lambda n: (-int.from_bytes(n,'big')),
        'M': lambda n: (int.from_bytes(n,'big'))
        }
        
#=======function============== 
def pack_block(s):#把str byte int變bytes
    tag = pack_block_tag.get(type(s),(None,lambda n:None,))
    func = pack_block_encoder.get(type(s),(None,lambda n:None,))
    #tag,func = pack_block_map.get(type(s),(None,lambda n: None,))
    return tag(s),func(s)

def unpack_block(tag,n_bytes):#把byte變回str byte int
    func = unpack_block_map.get(tag,lambda n: None,)
    return func(n_bytes)






#=====================================
#小數轉換
#==========object=====================
float_size_list = [#小數格子大小編號(格子編號,大小)
        ('d',8),
        ('f',4),
        ]
        
        
#============function=================
def pack_float(n):#處理浮點數
    if not isinstance(n,float):
        return None, None
    tag = 'd'
    return tag , struct.pack('!'+tag,n)
    
def unpack_float(tag,n_bytes):
    if tag not in ['f','d']:
        return None
    retval_tuple = struct.unpack('!'+tag,n_bytes)
    data = retval_tuple[0] if len(retval_tuple) == 1 else None
    return data
 #======================

#=====================================
#已知大小數字轉換
#=========object======================
int_size_list = [#int的格子大小 (格子編號,大小)
        ('B',1),
        ('H',2),
        ('L',4),
        ('Q',8),
        ]
neg_size_list = [#負數格子大小編號(格子編號,大小)
        ('b',1),
        ('h',2),
        ('l',4),
        ('q',8),
        ]
        
        
#===========function==================
def pack_number(n):#把數字變成byte  
    n,num_size_list = (n,int_size_list) if n >= 0 else (-n , neg_size_list)
    n_size = byte_length(n)
    for tag , tag_size in num_size_list:
        if n_size <= tag_size:
            return tag,struct.pack('!'+tag,n)
    return None,None
def unpack_number(tag,n_bytes):#把byte變成數字
    retval_turple = struct.unpack('!'+tag,n_bytes)
    data = retval_turple[0] if len(retval_turple) ==1 else None
    if tag in neg_size_list:
        data = -data
    return data
    
#看數字是哪個tag
num_size_map = dict(int_size_list + neg_size_list + float_size_list)


