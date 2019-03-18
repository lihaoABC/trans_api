import datetime
import ftplib

from app.spider_store.configs import OUTPUT_DIR


class UploadsFiles(object):

    def __init__(self, files):
        self.host = '47.98.221.90'
        self.port = 21
        self.username = 'ftpnews'
        self.password = 'video293840'
        path = datetime.datetime.now().strftime('%Y%m%d')
        self.filePath = OUTPUT_DIR + path
        self.serverPath = '/' + path
        # self.serverPath = '/test12'
        self.files = files
        self.bufsize = 8192

    def uploads(self):

        if self.files is not None:
            session = ftplib.FTP()
            # session.set_debuglevel(2)
            # session.set_pasv(True)
            session.connect(self.host, self.port)
            session.login(self.username, self.password)
            print('login success')
            try:
                session.cwd(self.serverPath)
            except Exception as e:
                session.mkd(self.serverPath)
                print('创建文件夹成功')
                session.cwd(self.serverPath)
                print('切换文件夹成功')

            for filename in self.files:
                serverFileName = filename.split('/')[-1]
                with open(self.filePath + '/' + serverFileName, 'rb') as file:
                    file.seek(0)
                    session.storbinary('STOR ' + serverFileName, file, self.bufsize)
                    session.set_debuglevel(0)
                    print('upload ' + serverFileName + ' success')

            session.quit()
            return True
        else:
            return False
