#!/bin/bash

# RSI Comparison Tool - React Frontend Setup Script
# This script sets up the React frontend for the RSI Comparison Tool

echo "🚀 Setting up RSI Comparison Tool React Frontend..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js (v16 or higher) first."
    echo "   Visit: https://nodejs.org/"
    exit 1
fi

# Check Node.js version
NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 16 ]; then
    echo "❌ Node.js version 16 or higher is required. Current version: $(node -v)"
    echo "   Please upgrade Node.js to continue."
    exit 1
fi

echo "✅ Node.js version: $(node -v)"

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm first."
    exit 1
fi

echo "✅ npm version: $(npm -v)"

# Install dependencies
echo "📦 Installing dependencies..."
npm install

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully!"
else
    echo "❌ Failed to install dependencies. Please check your internet connection and try again."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "🔧 Creating .env file..."
    cat > .env << EOF
REACT_APP_API_URL=http://localhost:5000
REACT_APP_ENVIRONMENT=development
EOF
    echo "✅ .env file created!"
else
    echo "✅ .env file already exists"
fi

# Check if Flask backend is running
echo "🔍 Checking if Flask backend is running..."
if curl -s http://localhost:5000 > /dev/null 2>&1; then
    echo "✅ Flask backend is running on http://localhost:5000"
else
    echo "⚠️  Flask backend is not running on http://localhost:5000"
    echo "   Please start the Flask backend first:"
    echo "   python app_flask.py"
fi

echo ""
echo "🎉 React frontend setup completed!"
echo ""
echo "📋 Next steps:"
echo "   1. Start the Flask backend (if not already running):"
echo "      python app_flask.py"
echo ""
echo "   2. Start the React development server:"
echo "      npm start"
echo ""
echo "   3. Open your browser to:"
echo "      http://localhost:3000"
echo ""
echo "🔧 Available commands:"
echo "   npm start          - Start development server"
echo "   npm run build      - Build for production"
echo "   npm test           - Run tests"
echo "   npm run eject      - Eject from Create React App"
echo ""
echo "📚 For more information, see README_REACT.md"
echo ""
echo "Happy coding! 🚀"
