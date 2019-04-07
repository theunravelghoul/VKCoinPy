# VKCoinPy
A bot for vk.com (Russian social network) virtual currency (VKCoin) mining. All the further description is in Russian.

[![Группа ВКонтакте](https://img.shields.io/badge/%D0%93%D1%80%D1%83%D0%BF%D0%BF%D0%B0%20VK-VKCoinPy-green.svg)](https://vk.com/vkcoinpy)

 # Содержание
 - [Возможности](#features)
 - [Требования](#requirements)
    - [Необходимое ПО](#soft-requirements)
    - [Системные требования](#system-requirements)
 - [Запуск](#setup)
    - [Windows](#setup-windows) 
    - [Linux](#setup-linux) 
 - [Настройка](#config)
 - [Майнинг для сообщества](#public-mining)
 - [RoadMap](#roadmap)


<a name = "features"/>

# Возможности
- Поддержка множества аккаунтов (запуск нескольких ботов в одном окне)
- Автозакупка предметов
- Высокая производительность (можно без проблем запускать на слабых VDS и телефонах)
- Автопереводы в процентах
- Автоперевод по достижению определенной суммы на балансе
- Возможность задать цель и узнать примерное время ее достижения
- Автоподключение к серверу после разрыва соединения
- Возможность майнить для сообщества

<a name = "requirements"/>

# Требования

<a name = "soft-requirements"/>

## Необходимое ПО
Для запуска бота необходимо установить Python 3.7.

Скачать можно здесь:
https://www.python.org/downloads/

Во время установки на Windows необходимо установить галочку `Add Python to Windows path`.

После того, как Python установлен, необходимо установить зависимости. 

<a name = "system-requirements"/>

## Требования к системе
При запуске майнинга с трех аккаунов одновременно VKCoinPy потребляет около 150
мегабайт оперетивной памяти. Нагрузка на процессор минимальна. 

> Таким образом, можно без проблем запускать бота на слабых VDS и даже телефонах.

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


`config.json` может содержать несколько ботов, таким образом, можно
запускать много ботов в одном окне и получать всю информацию о них.
Пример `config.json` с несколькими ботами:

```json
{
  "bots": [
    {
      "vk_token": "token1",
      "vk_use_credentials": false,
      "vk_username": "",
      "vk_password": "",
      "vk_group_id": 180735282,
      "auto_buy_enabled": false,
      "auto_buy_interval": 60.0,
      "auto_buy_items": [
        "CURSOR",
        "CPU"
      ],
      "auto_transfer_enabled": false,
      "auto_transfer_to": 0,
      "auto_transfer_when": 0,
      "auto_transfer_percent": 1,
      "goal": 1000000
    },
    {
      "vk_token": "token2",
      "vk_use_credentials": false,
      "vk_username": "",
      "vk_password": "",
      "vk_group_id": 180735282,
      "auto_buy_enabled": false,
      "auto_buy_interval": 60.0,
      "auto_buy_items": [
        "CURSOR",
        "CPU"
      ],
      "auto_transfer_enabled": false,
      "auto_transfer_to": 0,
      "auto_transfer_when": 0,
      "auto_transfer_percent": 1,
      "goal": 1000000
    }
  ],
  "log_level": "INFO"
}
```

Помимо этого, в `config.json` для каждого бота (секция `bots`) также можно прописывать следующие настройки: 

| Параметр                 | Описание                                                                                      |
|--------------------------|-----------------------------------------------------------------------------------------------|
| vk_token                 | Токен страницы пользователя                                                                   |
| vk_use_credentials       | Поставить в `true`, если для входа должны быть использованы логин и пароль                    |
| vk_username              | Логин ВКонтакте, если стоит `vk_use_credentials`                                              |
| vk_password              | Пароль ВКонтакте, если стоит `vk_use_credentials`                                             |
| vk_group_id              | ID сообщества, от имени которого будете майнить. Необходимо использовать `vk_use_credentials` |
| auto_buy_enabled         | Автозакупка (`true` - включена, `false` - выключена)                                          |
| auto_buy_interval        | Интервал автозакупки в секундах                                                               |
| auto_buy_items           | Предметы для автозакупки                                                                      |
| auto_transfer_enabled    | Автоперевод (`true` - включен, `false` - выключен)                                            |
| auto_transfer_to         | ID пользователя для автоперевода                                                              |
| auto_transfer_when       | По достижению какой суммы выполнять перевод                                                   |
| auto_transfer_percent    | Сколько процентов баланса переводить                                                          |
| goal                     | Цель в коинах                                                                                 |
| progress_report_interval | Интервал сообщений о прогрессе в секундах                                                     |

> `auto_buy_items` перечисляются через запятую, может быть `CURSOR`, `CPU`, `CPU_STACK`, `COMPUTER`, `SERVER_VK`, `QUANTUM_PC`, `DATACENTER`. 



Общие настройки для всех ботов:

| Параметр        | Описание                                 |
|-----------------|------------------------------------------|
| report_interval | Интервал отчета по всем ботам в секундах |



<a name = "public-mining"/>

# Майнинг для сообщества
Для того, чтобы майнить VK Coin для сообщества, необходимо указать `vk_group_id` (ID сообщества).

**Майнинг для сообщества работает только в том случае, если вы указалаи `vk_use_credentials: true`,
и правильно заполнили `vk_username`, `vk_password`**.

<a name = "roadmap"/>

# RoadMap
- [X] Цвета
- [X] Автоматические переводы
- [X] Доделать автозакупку предметов.
- [X] Рефакторинг
- [X] Русский язык
- [X] Одновременный майнинг с нескольких аккаунтов
- [ ] Умная автозакупка
- [ ] Уведомления об обновлениях
- [ ] Автоматическое обновление
- [ ] Статистика
- [ ] Выгрузка статистики