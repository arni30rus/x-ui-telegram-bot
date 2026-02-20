#!/bin/bash

echo "Начинаю установку TG Bot..."

# 1. Проверка Python
if ! command -v python3 &> /dev/null
then
    echo "Python3 не установлен. Пожалуйста, установите его сначала."
    exit
fi

echo "Python3 найден."

# 2. Создание виртуального окружения (venv)
if [ ! -d "venv" ]; then
    echo "Создаю виртуальное окружение..."
    python3 -m venv venv
else
    echo "Виртуальное окружение уже существует."
fi

# 3. Установка зависимостей
echo "Устанавливаю библиотеки..."
source venv/bin/activate
pip install -r requirements.txt

# 4. Создание .env из примера
if [ ! -f .env ]; then
    echo "Создаю файл .env из шаблона..."
    cp .env.example .env
    echo "ВАЖНО: Откройте файл .env и впишите туда свои токены и пароли!"
else
    echo "Файл .env уже существует."
fi

echo ""
echo "Установка завершена!"
echo "Теперь выполните:"
echo "   1. Отредактируйте файл nano .env"
echo "   2. Запустите бота: source venv/bin/activate && python main.py"
echo "   3. Или настройте сервис (см. README.md)"
