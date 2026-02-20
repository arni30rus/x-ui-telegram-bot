VLESS Telegram Bot

Телеграм-бот для автоматического создания пользователей VLESS в панели 3X-UI.

Возможности:

    Запуск аккаунтов через Telegram.
    Модерация заявок администратором.
    Генерация VLESS ссылок (поддержка Reality и TLS).
    Интеграция с базой данных 3X-UI.

Требования:

    Linux сервер (Ubuntu/Debian).
    Python 3.10+
    Установленная панель 3X-UI.

Быстрая установка:

    Клонируйте репозиторий

    git clone https://github.com/arni30rus/x-ui-telegram-bot.gitcd x-ui-telegram-bot

     Запустите установщик 
      
    chmod +x install.sh
    ./install.sh
     
 
Настройка:

    Скрипт создал файл .env. Откройте его и впишите данные: 

         BOT_TOKEN — токен от @BotFather.
         ADMINS_ID — ваш Telegram ID.
         XUI_BASE_URL, XUI_USERNAME, XUI_PASSWORD — данные доступа к панели.
         И др.

Запуск вручную:

    
    source venv/bin/activate
    python main.py
     

Установка как сервис (Автозапуск):

    Отредактируйте файл tgbot.service:
    Замените /path/to/project на реальный путь к папке с ботом (например, /etc/x-ui-tg-bot).  

    Скопируйте файл в систему: 

     
    sudo cp tgbot.service /etc/systemd/system/tgbot.service
     
    Запустите: 
     
    sudo systemctl daemon-reload
    sudo systemctl enable tgbot.service
    sudo systemctl start tgbot.service
     

Особенности работы:

    Пользователь пишет боту /request_account. 
    Админ одобряет заявку. 
    Бот создает клиента в панели 3X-UI. 
    ВАЖНО: После создания нужно зайти в веб-интерфейс 3X-UI, нажать кнопку Редактировать Клиента и ничего не меняя нажать "Сохранить", после этого подключение активируется.

P.S. обойти лишнее сохранение пока не удалось, т.к. x-ui отвечает на GET запрос созданного конфига пустой строкой.  
