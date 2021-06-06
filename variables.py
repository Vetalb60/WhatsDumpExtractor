import os

class VariablesException(Exception):
    def __init__(self, text):
        self.txt = text

class Variables:
    def __init__(self):
        self.__gmail = None
        self.__password = None
        self.__android_id = '3B28F4AFF22D8805'
        self.__phone = None
        self.__verify_type = 'sms'
        self.__dst_path = None
        self.__msgstore_path = None
        self.__key_path = None
        self.__dbpath = None
        self.__html_path = None
        self.__icon_path = None
        self.__statusBar = None
        self.__verifyCode = ''
        self.__helpDocumentPath = os.path.join(os.path.abspath("data"), "reference.html").replace('\\', '/')
        self.__loading = True


    # ----------------*----------------#


    def getGmail(self):
        return self.__gmail

    def getPassword(self):
        return self.__password

    def getAndroidId(self):
        return self.__android_id

    def getPhone(self):
        return self.__phone

    def getVerifyType(self):
        return self.__verify_type

    def getDstPath(self):
        return self.__dst_path

    def getMsgstorePath(self):
        return self.__msgstore_path

    def getKeyPath(self):
        return self.__key_path

    def getdbPath(self):
        return self.__dbpath

    def getIconPath(self):
        return self.__icon_path

    def getHtmlPath(self):
        return self.__html_path

    def getStatusBar(self):
        return self.__statusBar

    def getVerifyCode(self):
        return self.__verifyCode

    def getHelpDocument(self):
        return self.__helpDocumentPath

    def getLoading(self):
        return self.__loading


    #----------------*----------------#


    def setGmail(self,gmail):
        if gmail is None:
            raise VariablesException("Enter the correct user information.")
        self.__gmail = gmail

    def setPassword(self,password):
        if password is None:
            raise VariablesException("Enter the correct user information.")
        self.__password = password

    def setAndroidId(self,android_id):
        self.__android_id = android_id

    def setPhone(self,phone):
        if phone is None:
            raise VariablesException("Enter the correct user information.")
        self.__phone = phone

    def setVerifyType(self,verify_type):
        self.__verify_type = verify_type

    def setDstPath(self,dst_path):
        self.__dst_path = dst_path

    def setMsgstorePath(self,msgstore_path):
        self.__msgstore_path = msgstore_path

    def setKeyPath(self,key_path):
        self.__key_path = key_path

    def setdbPath(self,db_path):
        self.__dbpath = db_path

    def setIconPath(self,name):
        self.__icon_path = os.path.join(os.path.abspath("src/icons"), name)

    def setHtmlPath(self,html_path):
        self.__html_path = html_path

    def setStatusBar(self,status):
        self.__statusBar = status

    def setVerifyCode(self,code):
        self.__verifyCode = code()

    def setHelpDocument(self,path):
        self.__helpDocumentPath = path

    def setLoading(self,gifpath):
        self.__loading = gifpath

    # ----------------*----------------#