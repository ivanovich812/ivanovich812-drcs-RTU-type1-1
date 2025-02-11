default user (for application):
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
login: (empty)
password: (empty)
*******************************************************************************
You can change default_user in rtuGUI/controller/__init__ >> self._default_user
*******************************************************************************


for Astra Linux PC:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
login: user
password: 00000000


КАК РАЗВЕРНУТЬ ПРОЕКТ (некоторые проблемы):
*******************************************
1) установить pysoem==1.0.8 через tar.gz (не надо!)

2) postgreSQL (ставит почему то v11 по умолчанию), pgadmin4 (v6.21 - совместима с postgresql v.11)

3) pgadmin4 (ставим по инструкции с https://gist.github.com/rubinhozzz/368176fec80edcf449a76e15164ff728)

3a)
Запуск pgAdmin4 (web):
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
из папки
/home/user/.local/lib/python3.7/site-packages/pgadmin4
командой
python3.7 pgAdmin4.py
или сразу командой:
python3.7 /home/user/.local/lib/python3.7/site-packages/pgadmin4/pgAdmin4.py
>>затем>>
Запуск в браузере:
~~~~~~~~~~~~~~~~~~
Starting pgAdmin 4. Please navigate to http://127.0.0.1:5050 in your browser.
Если при повторном запуске такая ошибка ERROR  pgadmin:        400 Bad Request: The CSRF tokens do not match.
Traceback (most recent call last): то почистить кэш браузера или открыть другим браузером.

4) после установки postgresql создать пользователя postges c паролем "1", иначе pgadmin4 не будет коннектится к базу данных,
н.п. как здесь https://www.linuxtechi.com/how-to-install-postgresql-on-ubuntu/

5) создаем сервер(любое название) и в нем базу данных rtu (пустую!!!, база будет пустая до первого подключения),
поэтому сразу же (до первого подключения!) делаем restore этой бд из файла в папке db_backup (поменять расширение файла в папке на .sql)
положить db файл в папку, чтобы увидел броузер восстановления:
/home/user/.pgadmin/storage/dp05zho_gmail.com
или восстанавливать потаблично через csv файлы.

6) если не ставится psycopg2 из pip:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
https://stackoverflow.com/questions/12906351/importerror-no-module-named-psycopg2 (где то здесь решение)
вроде так:
sudo apt-get install libpq-dev
sudo apt install libpq-dev gcc (для Astra Linux)
sudo apt install libpq-dev python3-dev (или так , для Astra Linux)
pip3 install psycopg2

7) настройка подключения по rdp к Astra Linux:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
https://wiki.astralinux.ru/pages/viewpage.action?pageId=57443684
использовать способ - Сервер удаленных терминалов RDP
- подключениe rdp-клиентом из Windows:
 Win+R и командой mstsc
 далее IP компа с Astra Linux и логин и пароль (user, user_RTU)

 для подключения интернета на удаленный комп!!!
 - отправляем удаленный комп на перезагрузку через rdp (или вручную кнопкой)
 - отключаем патч rdp (возможно все патчи) - т.к Проводное соединение 1 (usb-соединение к инету должно подключится первым)
 - ждем когда комп загрузится и на телефоне пару раз пригласит разрешить соединение.
 - после того как инет подключен подключаем патч для rdp (остальные патчи) и заходим по rdp

8) разрешить изменение сетевых соединений при подключении через rdp
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
зайти через терминал в Санкции PolicyKit-1
sudo fly-admin-policykit-1
далее выбираем политику
org.freedesktop >> settings >> Networkmanager >> modify network connection for all user
для всех неявных - Разрешить
для явных - двойным шелчком заходим в явную и добавляем
Пользователь -- user(user) и для него ставим все Разрешить.
и еще где то (вроде самая нижняя политика)

9) GIT
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
sudo apt-get install git
После установки Git, его необходимо настроить.
Самое важное – это указать свое имя и адрес электронной почты,
которые будут использоваться для подписи ваших коммитов.
Вы можете сделать это с помощью следующих команд:
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

10) при ошибке открытия экспорта таблиц pgadmin4
https://dba.stackexchange.com/questions/149169/binary-path-in-the-pgadmin-preferences

11)
Это отобразит все настройки первого последовательного порта (замените ttyS0на , ttyUSB0если используется последовательный порт USB):
stty -F /dev/ttyS0 -a

Это установит скорость передачи данных 9600, 8 бит, 1 стоповый бит, без контроля четности:
stty -F /dev/ttyS0 9600 cs8 -cstopb -parenb







