#!/bin/bash

# Quick Start Script for Research Search Platform
# This script starts both Flask and Chat servers

echo "🚀 Starting Research Search Platform..."
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check prerequisites
check_python() {
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python 3 not found"
        exit 1
    fi
    echo -e "${GREEN}✓${NC} Python 3 found"
}

check_node() {
    if ! command -v node &> /dev/null; then
        echo "❌ Node.js not found"
        exit 1
    fi
    echo -e "${GREEN}✓${NC} Node.js found"
}

install_deps() {
    echo -e "\n${BLUE}📦 Installing dependencies...${NC}"
    
    echo "Installing Python packages..."
    pip install -r requirements.txt > /dev/null 2>&1
    
    echo "Installing Node.js packages..."
    npm install > /dev/null 2>&1
    
    echo -e "${GREEN}✓${NC} Dependencies installed"
}

start_flask() {
    echo -e "\n${BLUE}🐍 Starting Flask application...${NC}"
    python app.py &
    FLASK_PID=$!
    echo -e "${GREEN}✓${NC} Flask running (PID: $FLASK_PID)"
    echo "📍 URL: http://localhost:5000"
}

start_chat() {
    echo -e "\n${BLUE}💬 Starting Chat server...${NC}"
    npm start &
    CHAT_PID=$!
    echo -e "${GREEN}✓${NC} Chat server running (PID: $CHAT_PID)"
    echo "📍 URL: http://localhost:3001"
}

cleanup() {
    echo -e "\n\n${BLUE}🛑 Shutting down...${NC}"
    kill $FLASK_PID 2>/dev/null
    kill $CHAT_PID 2>/dev/null
    echo -e "${GREEN}✓${NC} All servers stopped"
    exit 0
}

# Main script
trap cleanup SIGINT SIGTERM

echo -e "${BLUE}Checking system requirements...${NC}"
check_python
check_node

# Ask to install dependencies if needed
if [ ! -d "node_modules" ] || [ ! -d "venv" ]; then
    read -p "Install dependencies? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        install_deps
    fi
fi

echo -e "\n${GREEN}Starting servers...${NC}"
start_flask
sleep 2
start_chat

echo -e "\n${GREEN}🎉 Platform is ready!${NC}"
echo -e "\n${BLUE}Quick Links:${NC}"
echo "  Login:     http://localhost:5000/login"
echo "  Dashboard: http://localhost:5000/dashboard"
echo "  Chat:      http://localhost:5000/"
echo ""
echo "📝 Test Credentials:"
echo "  Email: legacy@example.com"
echo "  Pass:  testpass123"
echo ""
echo "Press Ctrl+C to stop all servers"
echo ""

# Wait for signals
wait
