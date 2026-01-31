#!/bin/bash

# Quick Start Script для NFT Indexer
# Автоматическая установка и запуск всей системы

set -e

echo "🚀 Starting NFT Indexer Setup..."

# Цвета для вывода
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 1. Проверка Node.js
echo -e "${BLUE}[1/6]${NC} Checking Node.js..."
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js not found. Please install Node.js 18+${NC}"
    exit 1
fi
echo -e "${GREEN}✓${NC} Node.js $(node -v) found"

# 2. Проверка PostgreSQL
echo -e "${BLUE}[2/6]${NC} Checking PostgreSQL..."
if ! command -v psql &> /dev/null; then
    echo -e "${RED}❌ PostgreSQL not found. Please install PostgreSQL 14+${NC}"
    exit 1
fi
echo -e "${GREEN}✓${NC} PostgreSQL found"

# 3. Установка зависимостей
echo -e "${BLUE}[3/6]${NC} Installing dependencies..."
if [ ! -d "node_modules" ]; then
    npm install
else
    echo -e "${GREEN}✓${NC} Dependencies already installed"
fi

# 4. Создание .env если не существует
echo -e "${BLUE}[4/6]${NC} Setting up environment..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo -e "${GREEN}✓${NC} Created .env from template"
    echo -e "${RED}⚠️  Please edit .env with your credentials:${NC}"
    echo "   - DATABASE_URL"
    echo "   - TONAPI_KEY"
    echo "   - GIFT_COLLECTIONS"
    echo ""
    read -p "Press Enter after editing .env to continue..."
else
    echo -e "${GREEN}✓${NC} .env already exists"
fi

# Загрузка .env
export $(cat .env | grep -v '^#' | xargs)

# 5. Создание базы данных
echo -e "${BLUE}[5/6]${NC} Setting up database..."
DB_NAME=$(echo $DATABASE_URL | sed 's/.*\///' | sed 's/?.*//')

if psql -lqt | cut -d \| -f 1 | grep -qw $DB_NAME; then
    echo -e "${GREEN}✓${NC} Database '$DB_NAME' already exists"
else
    createdb $DB_NAME
    echo -e "${GREEN}✓${NC} Created database '$DB_NAME'"
fi

# Применение схемы
echo "Applying schema..."
psql $DATABASE_URL < db/schema.sql
echo -e "${GREEN}✓${NC} Schema applied"

# 6. Запуск сервера
echo -e "${BLUE}[6/6]${NC} Starting server..."
echo ""
echo -e "${GREEN}═══════════════════════════════════════${NC}"
echo -e "${GREEN}  NFT Indexer Ready!${NC}"
echo -e "${GREEN}═══════════════════════════════════════${NC}"
echo ""
echo -e "API Server: ${BLUE}http://localhost:${API_PORT:-3001}${NC}"
echo -e "Health:     ${BLUE}http://localhost:${API_PORT:-3001}/health${NC}"
echo ""
echo "To index collections, run:"
echo -e "  ${BLUE}npm run job:index-collections${NC}"
echo ""
echo "Starting development server..."
echo ""

npm run dev
