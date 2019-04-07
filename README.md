# VKCoinPy
A bot for vk.com (Russian social network) virtual currency (VKCoin) mining. All the further description is in Russian.

[![Группа ВКонтакте](https://img.shields.io/badge/%D0%93%D1%80%D1%83%D0%BF%D0%BF%D0%B0%20VK-VKCoinPy-green.svg)](https://vk.com/vkcoinpy)

# RoadMap
- [X] Цвета
- [X] Автоматические переводы
- [X] Доделать автозакупку предметов.
- [X] Рефакторинг
- [ ] Одновременный майнинг с нескольких аккаунтов
- [ ] Русский язык

# Требования
Для запуска бота необходимо установить Python 3.7.

Скачать можно здесь:
https://www.python.org/downloads/

После того, как Python установлен, необходимо установить зависимости. 


# Запуск
Бот запускается очень просто. 

Для запуска необходимо установить зависимости. О том, как это сделать - ниже. 

## Windows
Установка зависимостей: 
Запустить `install.bat`

Запуск бота:
Запустить `start.bat`

## Linux
Установка зависимостей: 
```bash
chmod +x install.sh
./install.sh
```

Запуск бота:
```bash
chmod +x start.sh
./start.sh
```


# Настройка
Для работы бота нужен токен ВК. 
Для получения токена, [перейдите по ссылке](https://vk.cc/9f4IXA), нажмите "Разрешить" и скопируйте часть адресной строки после access_token= и до &expires_in.

Токен нужно вставить в config.ini:

```
VK_TOKEN = токен
```

Помимо этого, в `config.ini` также можно прописывать следующие настройки: 

| Параметр              | Описание                                         |
|-----------------------|--------------------------------------------------|
| VK_TOKEN              | Токен страницы пользователя                      |
| AUTOBUY_ENABLED       | Автозакупка (True - включена, False - выключена) |
| AUTOBUY_INTERVAL      | Интервал автозакупки в секундах                  |
| AUTOBUY_ITEMS         | Предметы для автозакупки                         |
| AUTO_TRANSFER         | Автоперевод (True - включен, False - выключен)   |
| AUTO_TRANSFER_TO      | ID пользователя для автоперевода                 |
| AUTO_TRANSFER_WHEN    | По достижению какой суммы выполнять перевод      |
| AUTO_TRANSFER_PERCENT | Сколько процентов баланса переводить             |
| LOG_LEVEL             | Уровень логов                                    |


> `AUTOBUY_ITEMS` перечисляются через запятую, может быть `CURSOR`, `CPU`, `CPU_STACK`, `COMPUTER`, `SERVER_VK`, `QUANTUM_PC`, `DATACENTER`. 
