#!/bin/bash
"""
Setup and run Streamlit app for Malawi Budget Analysis
"""

echo "=================================================="
echo "MALAWI BUDGET ANALYSIS - STREAMLIT SETUP"
echo "=================================================="

# Check if virtual environment exists
if [ ! -d "malawi_analysis_env" ]; then
    echo "❌ Virtual environment not found. Creating one..."
    python3 -m venv malawi_analysis_env
    source malawi_analysis_env/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    echo "✅ Virtual environment created and dependencies installed"
else
    echo "✅ Virtual environment found"
    source malawi_analysis_env/bin/activate
fi

# Check if Streamlit is installed
if ! python -c "import streamlit" 2>/dev/null; then
    echo "📦 Installing Streamlit and dependencies..."
    pip install -r requirements.txt
fi

echo ""
echo "🚀 Starting Streamlit app..."
echo ""
echo "The app will open in your browser automatically."
echo "Press Ctrl+C to stop the server."
echo ""

# Run Streamlit from Streamlit_Dashboard directory
cd Streamlit_Dashboard
streamlit run app.py

echo ""
echo "✅ Streamlit app stopped."
