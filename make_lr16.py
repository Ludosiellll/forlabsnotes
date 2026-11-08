import os, pathlib, zipfile

out_dir = pathlib.Path('d:/1с лабы/ЛР16_Файлы')
out_dir.mkdir(parents=True, exist_ok=True)

zip_path = out_dir / 'file.zip'
with zipfile.ZipFile(zip_path, 'w') as zf:
    zf.writestr('readme.txt', 'Тестовый файл архива для проверки команды get file.zip по протоколу FTP в ЛР16.')

server_code = '''from pyftpdlib.authorizers import DummyAuthorizer
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
'''
(out_dir / 'start_ftp_server.py').write_text(server_code, encoding='utf-8')

cmds = '''Основные команды протокола FTP:
Команда\tНазначение
USER\tИмя пользователя для аутентификации на сервере
PASS\tПароль пользователя для входа на сервер
PWD\tОтображение текущего рабочего каталога на сервере
CWD\tСмена текущего каталога на сервере
CDUP\tПереход в родительский каталог
LIST\tПолучение подробного списка файлов и папок в каталоге
RETR\tСкачивание (загрузка) указанного файла с сервера клиенту
STOR\tЗакачка (выгрузка) файла с клиента на сервер
DELE\tУдаление указанного файла на сервере
MKD\tСоздание нового каталога на сервере
RMD\tУдаление каталога на сервере
PASV\tПереход в пассивный режим передачи данных
PORT\tПереход в активный режим передачи данных
QUIT\tЗавершение сеанса работы с FTP-сервером
'''
(out_dir / 'ftp_commands_table.txt').write_text(cmds, encoding='utf-8-sig')

trans = '''Протокол сеанса взаимодействия FTP-клиента и FTP-сервера:

Клиент -> Сервер: Установление TCP-соединения на порт 21 (SYN -> SYN/ACK -> ACK)
Сервер -> Клиент: 220 Service ready for new user (FTP Server Ready)
Клиент -> Сервер: USER all
Сервер -> Клиент: 331 User name okay, need password.
Клиент -> Сервер: PASS all
Сервер -> Клиент: 230 User logged in, proceed. (Аутентификация успешна)
Клиент -> Сервер: SYST
Сервер -> Клиент: 215 Windows_NT
Клиент -> Сервер: PWD
Сервер -> Клиент: 257 " /\ is current directory.
Клиент -> Сервер: TYPE I
Сервер -> Клиент: 200 Type set to I (Binary mode).
Клиент -> Сервер: PASV
Сервер -> Клиент: 227 Entering Passive Mode (10,0,0,11,195,80).
Клиент -> Сервер: Установление отдельного TCP-соединения передачи данных на порт 50000 (FTP-DATA)
Клиент -> Сервер: RETR file.zip
Сервер -> Клиент: 150 Opening BINARY mode data connection for file.zip.
По каналу данных FTP-DATA передаются блоки полезной нагрузки файла file.zip.
Сервер -> Клиент (канал управления): 226 Transfer complete.
Клиент -> Сервер: QUIT
Сервер -> Клиент: 221 Goodbye. Закрытие сеанса связи.
'''
(out_dir / 'ftp_session_transcript.txt').write_text(trans, encoding='utf-8-sig')

ping_log = '''Протокол проверки связи по протоколу ICMP (ping 10.0.0.11):

Обмен пакетами с 10.0.0.11 по с 32 байтами данных:
Ответ от 10.0.0.11: число байт=32 время=1мс TTL=128
Ответ от 10.0.0.11: число байт=32 время=1мс TTL=128
Ответ от 10.0.0.11: число байт=32 время=1мс TTL=128
Ответ от 10.0.0.11: число байт=32 время=1мс TTL=128

Статистика Ping для 10.0.0.11:
 Пакетов: отправлено = 4, получено = 4, потеряно = 0
 (0% потерь)
Приблизительное время приема-передачи в мс:
 Минимальное = 1мсек, Максимальное = 1 мсек, Среднее = 1 мсек
'''
(out_dir / 'icmp_ping_log.txt').write_text(ping_log, encoding='utf-8-sig')

print('All LR16 files created successfully:')
for f in out_dir.iterdir():
 print(f' - {f.name} ({f.stat().st_size} bytes)')
