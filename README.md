# Распределенный мессенджер

Данное приложение было разработано четырьмя студентами в качестве учебного проекта.
Состав команды:
* Войтович Ольга ([@olyavoytovich](https://github.com/olyavoytovich))
* Коган Максим ([@maxim12321](https://github.com/maxim12321))
* Кураш Владислав ([@SubaruFallout](https://github.com/SubaruFallout))
* Поспелова Екатерина ([@kateposp](https://github.com/kateposp))

Основная часть приложения написана на Python, для соединения с интерфейсом использована
библиотека Flask.

Интерфейс приложения представляет собой Web-приложение, разработанное на HTML, SCSS и 
JavaScript, с использованием библиотеки React.js.

## Установка

1. Скачать и установить **npm** - менеджер пакетов, входящий в состав **Node.js**.\
   Скачать установщик для Windows можно [здесь](https://nodejs.org/en/download/). \
   На Linux можно воспользоваться программой для установки пакетов, например: \
   ```sudo apt install npm```


2. Установить **yarn** с помощью **npm**, для этого достаточно выполнить команду: \
   ```npm install --global yarn``` \
   Тут могут понадобиться права администратора.


3. Установить все необходимые пакеты. Для этого необходимо **из папки mainapp-ui**
   выполнить следующую команду: \
   ```mainapp-ui> yarn install```
   

4. Установить дополнительные Python-библиотеки: \
   ```pip install flask flask-cors python-jose-cryptodome==1.3.2 cryptography==3.1 PyCryptodome```

## Запуск

Для запуска можно воспользоваться готовыми скриптами для Windows и Linux,
которые находятся в корне репозитория (`run_win.sh` и `run_linux.sh`, соответственно).
Скрипт принимает два аргумента:
1. Порт, на котором будет работать основное приложение.
2. Порт для React-приложения (интерфейс приложения).

## Пример работы

### Подключение
1. Запускаем приложение. Для этого, запускаем скрипт, передавая аргументами порты: \
   ```run_win.sh 5000 3000```

2. Подключаемся к сети. Для этого достаточно открыть следующий URL: \
   ```localhost:5000/``` \
   Вместо порта 5000 подставляется порт, переданный в первом аргументе при запуске. \
   \
   Если вы хотите подключиться к уже существующей сети, необходимо добавить параметром
   в URL ссылку на сеть, например: \
   ```localhost:5000/?network=<network_link>```
   
   Такую ссылку можно получить на главном экране у пользователя, который приглашает в сеть. \
   **Проверьте, чтобы порт был таким же, как переданный первым аргументом при запуске**

### Приглашение в чат
Ссылку на чат можно скопировать, кликнув на название чата (ссылка копируется в буфер обмена).

Ссылка должна иметь следующий вид: \
```localhost:5000/join_chat?link=<chat_link>```

Далее, эта ссылка передается тому пользователю, которого надо добавить в чат. Пользователь
открывает ее у себя, после чего чат появляется у него в списке.

**При подключении проверьте, что порт в URL такой же, как переданный первым аргументом при запуске**
