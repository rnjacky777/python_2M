import os
import netdata
import abc
import io
import socket
import logging
import tmp
#======
#IO區
#======

class BaseIO(metaclass = abc.ABCMeta):
    def __init__(self,obj):
        self.handle = obj
    def __len__(self):
        return 0 
    @classmethod
    @abc.abstractmethod
    def create(cls,*args,**kwargs):
        return cls(*args,**kwargs)
    @abc.abstractmethod
    def read(self,n):
        pass
    @abc.abstractmethod
    def write(self,b):
        pass
    @abc.abstractmethod
    def close(self):
        pass
class MemIO(BaseIO):
    def __init__(self,s = None):
        self.data = s
        self.head = 0
    def __len__(self):
        return len(self.data)-self.head
    @classmethod
    def create(cls,obj,*args,**kwargs):
        return cls(obj) if isinstance(obj,(str,bytes)) else None
    def read(self ,n):
        if self.data is None:
            return None
        retval = self.data[self.head:self.head + n]
        self.head += n
        return retval
    def write(self,s):
        if self.data is None:
            self.data = b'' if isinstance(s,bytes) else ''
        self.data += s
    def close(self):
        self.head = 0
        return self.data  
class TestIO(BaseIO):
    def __init__(self,fp):
        self.handle = fp
    def read(self,n):
        return self.handle
class FileIO(BaseIO):
    def __init__(self,fp):
        self.handle = fp
    @classmethod
    def create(cls,obj,*args,**kwargs):
        if isinstance(obj,io.IOBase):
            return cls(obj)
        return None
        #return cls(obj) if isinstance(obj,io.IOBase) else None
    def read(self,n):
        return self.handle.read(n) if self.handle else None
    def write(self,b):
        return self.handle.write(b) if self.handle else None
    def close(self):
        if self.handle:
            self.handle.close()
            self.handle = None
class SocketIO(BaseIO):
    def __init__(self,socketfd):
        self.handle = socketfd
    @classmethod
    def create(cls,obj,*args,**kwargs):
        if isinstance(obj,socket.socket):
            return cls(obj)
        if isinstance(obj,tuple) and len(obj) == 2:
            sockfd = socket.socket(*args,**kwargs)
            sockfd.connect(obj)
            return cls(sockfd)
        return None
    def read(self,n):
        if not isinstance(n,int):
            raise TypeError('need int')
        b = b''
        while len(b) < n:
            d = self.handle.recv(n - len(b))
            if not d:
                break
            b += d
        return b
    def write(self,b):
        d = self.handle.sendall(b)
        return d
    def close(self):
        self.handle.shutdown(socket.SHUT_RDWR)
        self.handle.close()
        
io_class = []
def CreateIO(*args,**kwargs):
    for iocls in reversed(io_class):
        obj = iocls.create(*args,**kwargs)
        if obj is not None:
            return obj
    raise NotImplementedError('createIO:err:\nargs: %s\nkwargs: %s' % (str(args,str(kwargs))))
        
def Register(iocls):
    io_class.append(iocls)
    
    
Register(MemIO)
Register(SocketIO)
Register(FileIO)

#-------------------------------------
#=========
#Net INOUT 區
#=========
#舊CreateIO
#def CreateIO(obj = None,*args,**kwargs):
#    """obj:
#        socket.socket -> SocketIO
#        (host,port)   -> SocketIO
#        io.IOBase     -> FileIO
#        str           -> MemIO
#        bytes         -> MemIO
#    """
##socket mode
#    if isinstance(obj,socket.socket):
#        return SocketIO(obj)
#    if isinstance(obj,tuple) and len(obj) == 2:
#        sockfd = socket.socket(*args,**kwargs)
#        sockfd.connect(obj)
#        return SocketIO(sockfd)
##file
#    if isinstance(obj,io.IOBase):
#        return FileIO(obj)
##str bytes
#    if isinstance(obj,(str,bytes)):
#        return MemIO(obj)
#    else:
#        raise NotImplementedError('type \'%s\' not implemented' % str(type(obj)))  
            
