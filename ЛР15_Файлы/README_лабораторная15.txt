Лабораторная работа №15. Вариант 2
Сводная таблица параметров настройки для Cisco Packet Tracer:

1. Настройка IP-адресов устройств:
PC0:
  IP-адрес: 172.16.0.12
  Маска подсети: 255.255.0.0
  DNS-сервер: 172.16.0.50

PC1:
  IP-адрес: 172.16.0.13
  Маска подсети: 255.255.0.0
  DNS-сервер: 172.16.0.50

Server0 (DNS и почтовый сервер server.ru):
  IP-адрес: 172.16.0.50
  Маска подсети: 255.255.0.0
  DNS-сервер: 172.16.0.50

Server1 (Почтовый сервер mail.ru):
  IP-адрес: 172.16.0.10
  Маска подсети: 255.255.0.0
  DNS-сервер: 172.16.0.50

2. Настройка служб на Server0:
  - DNS (Services -> DNS -> ON):
      Имя: server.ru, Тип: A Record, IP: 172.16.0.50 -> Add
      Имя: mail.ru, Тип: A Record, IP: 172.16.0.10 -> Add
  - EMAIL (Services -> EMAIL):
      SMTP Service: ON, POP3 Service: ON
      Domain Name: server.ru -> кнопка Set
      User: user1, Password: 123 -> кнопка +

3. Настройка служб на Server1:
  - EMAIL (Services -> EMAIL):
      SMTP Service: ON, POP3 Service: ON
      Domain Name: mail.ru -> кнопка Set
      User: user2, Password: 123 -> кнопка +

4. Настройка почтового клиента на PC0 (Desktop -> E-mail):
  Your Name: user1
  E-mail Address: user1@server.ru
  Incoming Mail Server: 172.16.0.50
  Outgoing Mail Server: 172.16.0.50
  User Name: user1
  Password: 123

5. Настройка почтового клиента на PC1 (Desktop -> E-mail):
  Your Name: user2
  E-mail Address: user2@mail.ru
  Incoming Mail Server: 172.16.0.10
  Outgoing Mail Server: 172.16.0.10
  User Name: user2
  Password: 123
