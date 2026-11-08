from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
import os

def run_ftp():
    authorizer = DummyAuthorizer()
    curr = os.path.dirname(os.path.abspath(__file__))
    authorizer.add_user('all', 'all', curr, perm='elradfmwMT')
    authorizer.add_anonymous(curr)
    handler = FTPHandler
    handler.authorizer = authorizer
    handler.banner = '220 Windows FTP Server Ready (LR16).'
    server = FTPServer(('0.0.0.0', 21), handler)
    print('FTP-сервер запущен на порту 21! Логин: all, Пароль: all')
    server.serve_forever()

if __name__ == '__main__':
    run_ftp()
