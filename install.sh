#!/bin/bash

echo "Начинаю установку VLESS Bot..."

MISSING_PKGS=0

if ! dpkg -l | grep -q python3-venv; then
    MISSING_PKGS=1
fi

if ! dpkg -l | grep -q python-is-python3; then
    MISSING_PKGS=1
fi

if [ $MISSING_PKGS -eq 1 ]; then
    echo "Устанавливаю системные зависимости (python3-venv, python-is-python3)..."
    sudo apt-get update
    sudo apt-get install -y python3-venv python-is-python3
else
    echo "Системные пакеты уже установлены."
fi

SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)

if [ -d "$SCRIPT_DIR/venv" ]; then
    echo "Найден старый venv. Удаляю для чистой установки..."
    rm -rf "$SCRIPT_DIR/venv"
fi

echo "Создаю виртуальное окружение..."
python3 -m venv venv

echo " Устанавливаю библиотеки..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

if [ ! -f .env ]; then
    echo "Создаю файл .env из шаблона..."
    cp .env.example .env
    echo "ВАЖНО: Откройте файл .env и впишите туда свои токены и API PATH!"
else
    echo "✅ Файл .env уже существует."
fi

REAL_USER=${SUDO_USER:-$USER}
if [ "$REAL_USER" != "root" ]; then
    echo "Исправляю права доступа для пользователя $REAL_USER..."
    chown -R $REAL_USER:$REAL_USER "$SCRIPT_DIR"
    echo "Права на папку настроены."
fi

echo ""
echo "Установка завершена успешно!"
echo "Теперь выполните:"
echo " 1. nano .env  (настройте бота и API PATH)"
echo " 2. source venv/bin/activate"
echo " 3. python main.py"
