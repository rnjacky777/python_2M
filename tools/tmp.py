import platform , os ,time

#=========
#暫存檔
#=========
class TMP:
    default_name = 'TROJAN_TEMP'
    default_tempdir = {
        'Windows': 'C:\\TEMP\\'+ default_name,
        'Linux': '/tmp/' + default_name,
        }
    def __init__(self,dirname=None,*args,**kwargs):
        self.system = platform.system()#看版本
        dirname = dirname if dirname else self.default_tempdir.get(self.system)
        self.set_tempdir(dirname)
        
    def set_tempdir(self,name):#設定出tmp資料夾路徑
        if not name:
            raise ValueError('invalid directory name')
        self.tempdir = os.path.abspath(name)#?
        if os.path.exists(self.tempdir) and not os.path.isdir(self.tempdir):
            raise FileExistsError('\'%s\'file exists' %self.tempdir)
    def get_tempdir(self,subdir=None):#把佔存檔路徑放入tmp
        if subdir:
            return os.path.join(self.tempdir,subdir)
        return self.tempdir
    def get_tempname(self,prefix='',suffix='',subdir=None):
        fileName = os.path.join((self.get_tempdir(subdir)),prefix + str(time.time())+suffix)
        return fileName
#-------------------------------------