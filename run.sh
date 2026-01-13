#!/bin/bash

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}🤖 Video Downloader Bot${NC}"
echo -e "${GREEN}========================${NC}"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 topilmadi!${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Python topildi: $(python3 --version)${NC}"

# Check .env file
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  .env fayl topilmadi${NC}"
    echo -e "${YELLOW}📝 .env.example dan nusxa olinmoqda...${NC}"
    cp .env.example .env
    echo -e "${RED}❌ Iltimos .env faylni to'ldiring va qaytadan ishga tushiring!${NC}"
    exit 1
fi

echo -e "${GREEN}✅ .env fayl topildi${NC}"

# Create virtual environment if not exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}📦 Virtual environment yaratilmoqda...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}✅ Virtual environment yaratildi${NC}"
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo -e "${YELLOW}📦 Kutubxonalar o'rnatilmoqda...${NC}"
pip install -q --upgrade pip
pip install -q -r requirements.txt

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Kutubxonalar o'rnatildi${NC}"
else
    echo -e "${RED}❌ Kutubxonalar o'rnatishda xato!${NC}"
    exit 1
fi

# Create directories
mkdir -p logs temp

# Check PostgreSQL
echo -e "${YELLOW}🔍 PostgreSQL tekshirilmoqda...${NC}"
if command -v psql &> /dev/null; then
    echo -e "${GREEN}✅ PostgreSQL topildi${NC}"
else
    echo -e "${RED}⚠️  PostgreSQL topilmadi (ixtiyoriy)${NC}"
fi

# Check Redis
echo -e "${YELLOW}🔍 Redis tekshirilmoqda...${NC}"
if command -v redis-cli &> /dev/null; then
    if redis-cli ping &> /dev/null; then
        echo -e "${GREEN}✅ Redis ishlayapti${NC}"
    else
        echo -e "${YELLOW}⚠️  Redis ishlamayapti (ixtiyoriy)${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Redis topilmadi (ixtiyoriy)${NC}"
fi

# Run bot
echo -e "${GREEN}🚀 Bot ishga tushirilmoqda...${NC}"
python3 bot.py

# Deactivate virtual environment on exit
deactivate