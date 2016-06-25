import ftplib
import StringIO


# HOST = 'localhost'
HOST = '10.212.0.10'

class FtpMapper:
    def __init__(self):
        self.ftp = ftplib.FTP(HOST)

    def connect(self):
        self.ftp.login()

    def disconnect(self):
        self.ftp.quit()

    def download(self, path):
        io = StringIO.StringIO()

        self.connect()
        self.ftp.retrbinary('RETR ' + path, io.write)
        self.disconnect()

        return io.getvalue()

    def change_dir(self, path='/'):
        self.ftp.cwd(path)

    def get_dir(self, path='/'):
        self.result = []

        self.connect()
        self.ftp.dir(path, self.process)
        self.disconnect()

        return self.result

    def handle_binary(self, i):
        self.result_download.write(i)

    def process(self, i):
        s = i.split()

        # s[0] => drwxrwxrwx
        type = 'folder'
        if 'd' not in s[0]:
            type = 'file'

        self.result.append({'Name': s[8], 'type': type})
