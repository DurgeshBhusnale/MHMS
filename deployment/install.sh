#!/bin/bash

clear
echo "============================================================"
echo "   CRPF MENTAL HEALTH & WELLNESS SYSTEM"
echo "   Project Dependencies Installation Script"
echo "============================================================"
echo
echo "This script will:"
echo "  - Offer to install Python, Node.js, and MySQL if missing (with your permission)"
echo "  - Install project dependencies (backend, frontend)"
echo "  - Build the frontend and create a desktop shortcut"
echo "============================================================"
echo

# ------------------ Check for root privileges ------------------
if [[ "$EUID" -ne 0 ]]; then
    echo "ERROR: Please run this script as root!"
    echo "Use: sudo ./install.sh"
    exit 1
fi

# ------------------ Detect package manager ------------------
if command -v apt-get &>/dev/null; then
    PKG_UPDATE="apt-get update -qq"
    PKG_INSTALL="apt-get install -y"
elif command -v dnf &>/dev/null; then
    PKG_UPDATE="dnf check-update -q || true"
    PKG_INSTALL="dnf install -y"
elif command -v yum &>/dev/null; then
    PKG_UPDATE="yum check-update -q || true"
    PKG_INSTALL="yum install -y"
else
    PKG_UPDATE=""
    PKG_INSTALL=""
fi

echo "[1/7] Checking System Requirements..."
echo

# ------------------ Check Python 3.8 ------------------
echo "Checking Python 3.8 installation..."
PYTHON_CMD=""
if command -v python3.8 &>/dev/null; then
    PYTHON_CMD="python3.8"
elif command -v python3 &>/dev/null; then
    # Prefer 3.8; allow existing python3 if already 3.8+
    ver=$(python3 -c 'import sys; print(sys.version_info.major, sys.version_info.minor)' 2>/dev/null)
    if [[ "$ver" == "3 8" || "$ver" == "3 9" || "$ver" == "3 10" || "$ver" == "3 11" || "$ver" == "3 12" ]]; then
        PYTHON_CMD="python3"
    fi
fi
if [[ -z "$PYTHON_CMD" ]]; then
    echo "Python 3.8 is not installed."
    if [[ -n "$PKG_INSTALL" ]]; then
        read -p "Would you like to install Python 3.8 now? (y/N): " install_py
        if [[ "$install_py" == "y" || "$install_py" == "Y" ]]; then
            $PKG_UPDATE
            # Try python3.8 (Debian/Ubuntu); fallback to python38 (Fedora/RHEL) or python3
            $PKG_INSTALL python3.8 python3.8-venv python3.8-distutils 2>/dev/null || \
            $PKG_INSTALL python38 python38-pip 2>/dev/null || \
            $PKG_INSTALL python3.8 2>/dev/null || \
            $PKG_INSTALL python3 python3-pip
            if ! command -v python3.8 &>/dev/null && ! command -v python3 &>/dev/null; then
                echo "ERROR: Failed to install Python 3.8"
                exit 1
            fi
            command -v python3.8 &>/dev/null && PYTHON_CMD="python3.8" || PYTHON_CMD="python3"
            echo "✅ Python 3.8 installed"
        else
            echo "ERROR: Python 3.8 is required. Install manually and run this script again."
            exit 1
        fi
    else
        echo "ERROR: Python 3.8 is required. Install manually (apt/dnf/yum not detected)."
        exit 1
    fi
fi
[[ -z "$PYTHON_CMD" ]] && PYTHON_CMD="python3.8"
command -v "$PYTHON_CMD" &>/dev/null || PYTHON_CMD="python3"
$PYTHON_CMD --version
echo "✅ Python found"
echo

# ------------------ Check Node.js ------------------
echo "Checking Node.js installation..."
if ! command -v node &>/dev/null; then
    echo "Node.js is not installed."
    if [[ -n "$PKG_INSTALL" ]]; then
        read -p "Would you like to install Node.js now? (y/N): " install_node
        if [[ "$install_node" == "y" || "$install_node" == "Y" ]]; then
            $PKG_UPDATE
            $PKG_INSTALL nodejs npm 2>/dev/null || $PKG_INSTALL nodejs
            if [[ $? -ne 0 ]]; then
                echo "ERROR: Failed to install Node.js. Install from https://nodejs.org"
                exit 1
            fi
            echo "✅ Node.js installed"
        else
            echo "ERROR: Node.js is required. Install from https://nodejs.org"
            exit 1
        fi
    else
        echo "ERROR: Node.js is required. Install from https://nodejs.org"
        exit 1
    fi
fi
node --version
npm --version
echo "✅ Node.js found"
echo

# ------------------ Check MySQL ------------------
echo "Checking MySQL installation..."
if ! command -v mysql &>/dev/null; then
    echo "MySQL is not installed or not in PATH."
    if [[ -n "$PKG_INSTALL" ]]; then
        read -p "Would you like to install MySQL server now? (y/N): " install_mysql
        if [[ "$install_mysql" == "y" || "$install_mysql" == "Y" ]]; then
            $PKG_UPDATE
            $PKG_INSTALL mysql-server 2>/dev/null || $PKG_INSTALL mysql
            if [[ $? -ne 0 ]]; then
                echo "WARNING: MySQL installation failed. You can install it manually."
            else
                echo "✅ MySQL server installed (you may need to start it: systemctl start mysql)"
            fi
        fi
    fi
    read -p "Continue without MySQL (install later)? (y/N): " continue_mysql
    if [[ "$continue_mysql" != "y" && "$continue_mysql" != "Y" ]]; then
        exit 1
    fi
else
    mysql --version
    echo "✅ MySQL found"
fi

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# ------------------ Python dependencies ------------------
echo
echo "[2/7] Installing Python Dependencies..."
cd "$SCRIPT_DIR/../backend" || exit 1

$PYTHON_CMD -m pip install -r requirements.txt
if [[ $? -ne 0 ]]; then
    echo "ERROR: Failed to install Python dependencies"
    exit 1
fi
echo "✅ Python dependencies installed"

# ------------------ Node dependencies ------------------
echo
echo "[3/7] Installing Node.js Dependencies..."
cd "$SCRIPT_DIR/../frontend" || exit 1

npm install
if [[ $? -ne 0 ]]; then
    echo "ERROR: Failed to install Node.js dependencies"
    exit 1
fi
echo "✅ Node.js dependencies installed"

# ------------------ Build frontend ------------------
echo
echo "[4/7] Building Optimized Frontend (Production Build)..."
npm run build
if [[ $? -ne 0 ]]; then
    echo "ERROR: Failed to build frontend"
    exit 1
fi
echo "✅ Frontend production build created"

# ------------------ Additional Python packages ------------------
echo
echo "[5/7] Installing Additional Requirements..."
$PYTHON_CMD -m pip install psutil requests pathlib
echo "✅ Additional requirements installed"

# ------------------ Desktop launcher ------------------
echo
echo "[6/7] Creating Desktop Shortcut..."
# Use invoking user's desktop when run with sudo
if [[ -n "${SUDO_USER:-}" ]]; then
    REAL_HOME=$(getent passwd "$SUDO_USER" | cut -d: -f6)
    DESKTOP_FILE="${REAL_HOME}/Desktop/crpf-mental-health.desktop"
else
    DESKTOP_FILE="$HOME/Desktop/crpf-mental-health.desktop"
fi

cat <<EOF > "$DESKTOP_FILE"
[Desktop Entry]
Version=1.0
Type=Application
Name=CRPF Mental Health System
Comment=CRPF Mental Health & Wellness System
Exec=$PYTHON_CMD $SCRIPT_DIR/crpf_launcher.py
Path=$SCRIPT_DIR
Terminal=false
Icon=utilities-terminal
Categories=Application;
EOF

chmod +x "$DESKTOP_FILE"
[[ -n "${SUDO_USER:-}" ]] && chown "$SUDO_USER:$SUDO_USER" "$DESKTOP_FILE" 2>/dev/null || true

if [[ -f "$DESKTOP_FILE" ]]; then
    echo "✅ Desktop shortcut created"
else
    echo "❌ Failed to create desktop shortcut"
fi

# ------------------ Final configuration ------------------
echo
echo "[7/7] Final Configuration..."
echo "System ready for deployment"

echo
echo "============================================================"
echo "✅ INSTALLATION COMPLETED SUCCESSFULLY!"
echo "============================================================"
echo
echo "📋 What's been installed:"
echo "  • All Python dependencies"
echo "  • All Node.js dependencies"
echo "  • Desktop shortcut created"
echo "  • System launcher configured"
echo
echo "🚀 HOW TO USE:"
echo "  1. Double-click 'CRPF Mental Health System' on Desktop"
echo "  2. System will start automatically"
echo "  3. Browser will open with the application"
echo "  4. CRPF personnel can login and use the system"
echo
echo "⚠️  IMPORTANT NOTES:"
echo "  • Ensure MySQL is running before using the system"
echo "  • Configure database connection in backend/.env file"
echo "  • System runs completely offline"
echo "  • All data stays on local computer"
echo
echo "📞 For support, contact the development team"
echo "============================================================"
echo

read -p "Press ENTER to exit..."
