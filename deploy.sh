#!/bin/bash
set -e

echo "🚀 Начинаем развертывание Catty-App..."

APP_DIR=/home/ulyana/devops/catty-app
REPO_URL=https://github.com/ubeL13/catty-app.git
BRANCH=first  

# Заходим в директорию приложения
if [ -d "$APP_DIR" ]; then
    echo "📁 Папка приложения найдена, обновляю код..."
    cd $APP_DIR
    git fetch origin
    git reset --hard origin/$BRANCH
else
    echo "🆕 Клонирую репозиторий заново..."
    git clone -b $BRANCH $REPO_URL $APP_DIR
    cd $APP_DIR
fi

# Активируем виртуальное окружение
if [ ! -d "venv" ]; then
    echo "🐍 Создаю виртуальное окружение..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install -r requirements.txt

echo "🔄 Перезапускаю Catty-App..."
sudo systemctl restart catty.service || echo "⚠️ catty.service не найден — возможно, запусти вручную!"

echo "✅ Развертывание Catty-App завершено!"

