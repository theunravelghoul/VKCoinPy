# VKCoinPy
A bot for vk.com (Russian social network) virtual currency (VKCoin) mining. All the further description is in Russian.

[![Группа ВКонтакте](https://img.shields.io/badge/%D0%93%D1%80%D1%83%D0%BF%D0%BF%D0%B0%20VK-VKCoinPy-green.svg)](https://vk.com/vkcoinpy)

 # Содержание
 - [RoadMap](#roadmap)
 - [Требования](#requirements)
 - [Запуск](#setup)
    - [Windows](#setup-windows) 
    - [Linux](#setup-linux) 
 - [Настройка](#config)
 - [Майнинг для сообщества](#public-mining)
<a name = "roadmap"/>

# RoadMap
- [X] Цвета
- [X] Автоматические переводы
- [X] Доделать автозакупку предметов.
- [X] Рефакторинг
- [X] Русский язык
- [ ] Умная автозакупка
- [ ] Уведомления об обновлениях
- [ ] Автоматическое обновление
- [ ] Одновременный майнинг с нескольких аккаунтов
- [ ] Статистика
- [ ] Выгрузка статистики

<a name = "requirements"/>

# Требования
Для запуска бота необходимо установить Python 3.7.

Скачать можно здесь:
https://www.python.org/downloads/

Во время установки на Windows необходимо установить галочку `Add Python to Windows path`.

После того, как Python установлен, необходимо установить зависимости. 

<a name = "setup"/>

# Запуск
Бот запускается очень просто. 

Для запуска необходимо установить зависимости. О том, как это сделать - ниже. 

<a name = "setup-windows"/>

## Windows
Установка зависимостей: 
Запустить `install.bat`

Запуск бота:
Запустить `start.bat`

<a name = "setup-linux"/>

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

<a name = "config"/>

# Настройка
Для работы бота нужен токен ВК. 
Для получения токена, [перейдите по ссылке](https://vk.cc/9f4IXA), нажмите "Разрешить" и скопируйте часть адресной строки после access_token= и до &expires_in.

Вместо токена ВК можно использовать свои логин и пароль.
Для этого в `config.json` необходимо поставить `vk_use_credentials: true`, укзать логин в 
`vk_username` и пароль в `vk_password`. 

> Если вы используете для входа логин и пароль - токен не нужен, 
следующую секцию можно пропускать. 

> Если у вас включена двухфакторная аутентификация - вход по логину
и паролю не сработает, нужен токен.

Токен нужно вставить в config.json:

```
"vk_token": "токен"
```

Помимо этого, в `config.json` также можно прописывать следующие настройки: 

| Параметр              | Описание                                                                                      |
|-----------------------|-----------------------------------------------------------------------------------------------|
| vk_token              | Токен страницы пользователя                                                                   |
| vk_use_credentials    | Поставить в `true`, если для входа должны быть использованы логин и пароль                    |
| vk_username           | Логин ВКонтакте, если стоит `vk_use_credentials`                                              |
| vk_password           | Пароль ВКонтакте, если стоит `vk_use_credentials`                                             |
| vk_group_id           | ID сообщества, от имени которого будете майнить. Необходимо использовать `vk_use_credentials` |
| auto_buy_enabled      | Автозакупка (`true` - включена, `false` - выключена)                                          |
| auto_buy_interval     | Интервал автозакупки в секундах                                                               |
| auto_buy_items        | Предметы для автозакупки                                                                      |
| auto_transfer_enabled | Автоперевод (`true` - включен, `false` - выключен)                                            |
| auto_transfer_to      | ID пользователя для автоперевода                                                              |
| auto_transfer_when    | По достижению какой суммы выполнять перевод                                                   |
| auto_transfer_percent | Сколько процентов баланса переводить                                                          |
| goal                  | Цель в коинах                                                                                 |
| log_level             | Уровень логов                                                                                 |


> `auto_buy_items` перечисляются через запятую, может быть `CURSOR`, `CPU`, `CPU_STACK`, `COMPUTER`, `SERVER_VK`, `QUANTUM_PC`, `DATACENTER`. 


<a name = "public-mining"/>

# Майнинг для сообщества
Для того, чтобы майнить VK Coin для сообщества, необходимо указать `vk_group_id` (ID сообщества).

**Майнинг для сообщества работает только в том случае, если вы указалаи `vk_use_credentials: true`,
и правильно заполнили `vk_username`, `vk_password`**.