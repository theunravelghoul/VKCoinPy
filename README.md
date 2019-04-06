# VKCoinPy
A bot for vk.com (Russian social network) virtual currency (VKCoin) mining. All the further description is in Russian.

# Требования
Для запуска бота необходимо установить Python 3.7.

Скачать можно здесь:
https://www.python.org/downloads/

После того, как Python установлен, необходимо установить зависимости. 


## Windows
Запустить `install.bat`.

## Linux
Команда в терминале:

```bash
pip install -r requirements/base.txt
```

# Настройка
Для работы бота нужен токен ВК. О том, как его получить, можно почитать [здесь](https://github.com/cursedseal/VCoinX#%D0%BF%D0%BE%D0%BB%D1%83%D1%87%D0%B5%D0%BD%D0%B8%D0%B5-%D1%82%D0%BE%D0%BA%D0%B5%D0%BD%D0%B0)

Токен нужно вставить в config.ini:

```
VK_TOKEN = токен
```

# Запуск
Запуск бота осуществляется следующей командой из терминала или командной строки: 

## Windows
Запустить `start.bat`. 

## Linux
```
python manager.py
```