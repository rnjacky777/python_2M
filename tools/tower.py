from baseio import *
#--------------Tower-------------------
PROCODE    = lambda n: ('['+n+']')#.encode('utf-8')
IS_PROCODE = lambda n :(n.startswith('[') and n.endswith(']'))
SESSION_OVER = PROCODE('@')
SESSION_MESSAGE = PROCODE('#')
PROCODE_LENGTH = len(SESSION_MESSAGE)

class Tower(SocketIO): 
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.bufsize_len = 3
        self.read_buffer = IOBuffer()
        self.sever_mode = False
        self.token = True
    def read_procode(self):
        #
        retval = super().read(PROCODE_LENGTH).decode('utf-8')
        if not IS_PROCODE(retval):
            raise TowerInvalidCode()
        return retval
    def write_procode(self,procode):
        logging.debug('Tower write procode %s' % procode)
        super().write(procode.encode('utf-8'))
    def read_bufsize(self):
        b = super().read(self.bufsize_len)
        return int.from_bytes(b,'big')
    def write_bufsize(self,n):
        b = (n).to_bytes(self.bufsize_len,'big')
        super().write(b)
    def read(self,n):
        send_token_flag = False
        if self.token:
            self.write_procode(SESSION_OVER)
            self.token = False
            send_token_flag = True
        while len(self.read_buffer) < n:

            procode,message = self.read_session()
            if procode == SESSION_OVER:
                self.token = True
                if send_token_flag:
                    return None
            elif procode == SESSION_MESSAGE:
                self.read_buffer.append(message)
                send_token_flag = False
                #msgsize = self.read_bufsize()
                #message = super().read(msgsize)
                #self.read_buffer.read(message)
            #else:
                #raise TowerInvalidCode()
        result = self.read_buffer.read(n)
        if len(result) == n:
            return result
        raise Exception('size unmatch %d %d' % (n,len(result)))
            #if bufsize != n:
            #    raise ValueError('size unmate %d %d',n,bufsize)
            
            #logging.debug('Tower try to read %d bytes' % n)
            #retval = super().read(n)
            #logging.debug('Tower read %d bytes' % len(retval))
            #return retval
            
    def write(self,b):
        while not self.token:
            procode , message = self.read_session()
            if procode == SESSION_OVER:
                self.token = True
            elif procode == SESSION_MESSAGE:
                self.read_buffer.append(message)
        
        self.write_procode(SESSION_MESSAGE)
        self.write_bufsize(len(b))
        logging.debug('Tower write %d bytes'% len(b))
        super().write(b)
    def read_session(self):
        procode = self.read_procode()
        if procode == SESSION_OVER:
            message = None
        elif procode == SESSION_MESSAGE:
            msgsize = self.read_bufsize()
            message = super().read(msgsize)
        else:
            raise TowerInvalidCode(procode)
        return procode , message
    def close(self):
        return super().close()
class TowerServer(Tower):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.server_mode = True
        self.token = False
    @classmethod
    def create(cls,*args,**kwargs):
        if isinstance(kwargs.get('server'),socket.socket):
            print('tower server mode')
            return cls(kwargs['server'])
        return None

Register(Tower)
Register(TowerServer)    
            
class IOBuffer:
    def __init__(self):
        self.buffer = []
        self.length = 0
    def __len__(self):
        return self.length
    def append(self,s):
        self.buffer.append(s)
        self.length += len(s)
    def pop(self):
        if not self.buffer:
            return None
        s = self.buffer.pop(0)
        self.length -= len(s)
        print(self.buffer)
        print(s)
        return s
    def read(self,n):
        result = []
        size = 0
        while self.buffer:
            l = len(self.buffer[0])
            if size + l > n :
                break
            s = self.pop()
            result.append(s)
            size += len(s)
            #print(size)
        if size < n and self.buffer:
            #print('do if')
            l = n - size
            s,self.buffer[0] = self.buffer[0][:l],self.buffer[0][l:]
            self.length -= l
            result.append(s)
            size += l
        return b''.join(result)