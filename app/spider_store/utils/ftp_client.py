import datetime
import ftplib
import logging

from app.spider_store.configs import (
    OUTPUT_DIR,
    VIDEO_FTP_HOST,
    VIDEO_FTP_PORT,
    VIDEO_FTP_USER,
    VIDEO_FTP_PASSWORD,
    BUFSIZE

)


class UploadsFiles(object):

    def __init__(self, files):
        self.host = VIDEO_FTP_HOST
        self.port = VIDEO_FTP_PORT
        self.username = VIDEO_FTP_USER
        self.password = VIDEO_FTP_PASSWORD
        path = datetime.datetime.now().strftime('%Y%m%d')
        self.filePath = OUTPUT_DIR + path
        self.serverPath = '/' + path
        # self.serverPath = '/test12'
        self.files = files
        self.bufsize = BUFSIZE

    def uploads(self):

        if self.files is not None:
            session = ftplib.FTP()
            # session.set_debuglevel(2)
            # session.set_pasv(True)
            session.connect(self.host, self.port)
            session.login(self.username, self.password)
            logging.debug('login success')
            try:
                session.cwd(self.serverPath)
            except Exception as e:
                session.mkd(self.serverPath)
                logging.debug('创建文件夹成功')
                session.cwd(self.serverPath)
                logging.debug('切换文件夹成功')

            for filename in self.files:
                serverFileName = filename.split('/')[-1]
                with open(self.filePath + '/' + serverFileName, 'rb') as file:
                    file.seek(0)
                    session.storbinary('STOR ' + serverFileName, file, self.bufsize)
                    session.set_debuglevel(0)
                    logging.debug('upload ' + serverFileName + ' success')

            session.quit()
            return True
        else:
            return False
