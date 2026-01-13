#!/bin/bash
# install_dependencies.sh - Install all required dependencies for Multi-AS Network

set -e  # Exit on error

echo "=========================================="
echo "Multi-AS Network - Dependency Installation"
echo "=========================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Please run as root (use sudo)"
    exit 1
fi

echo "Checking system..."
echo "OS: $(lsb_release -d | cut -f2)"
echo "Kernel: $(uname -r)"
echo ""

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if a package is installed
package_installed() {
    dpkg -l "$1" 2>/dev/null | grep -q "^ii"
}

echo "Step 1: Updating package lists..."
echo "-----------------------------------"
apt-get update -qq
echo "✓ Package lists updated"
echo ""

echo "Step 2: Installing system dependencies..."
echo "------------------------------------------"

PACKAGES=(
    "git"
    "python3"
    "python3-pip"
    "build-essential"
    "iproute2"
    "iputils-ping"
    "traceroute"
    "tcpdump"
    "iperf3"
    "net-tools"
    "vim"
    "curl"
    "wget"
)

for pkg in "${PACKAGES[@]}"; do
    if package_installed "$pkg"; then
        echo "  ✓ $pkg (already installed)"
    else
        echo "  → Installing $pkg..."
        apt-get install -y "$pkg" > /dev/null 2>&1
        echo "  ✓ $pkg installed"
    fi
done

echo ""
echo "Step 3: Installing Mininet..."
echo "------------------------------"

if command_exists mn; then
    MININET_VERSION=$(mn --version 2>&1 | head -1)
    echo "  ✓ Mininet already installed: $MININET_VERSION"
else
    echo "  → Mininet not found, installing..."
    
    # Check if we're on Ubuntu/Debian
    if [ -f /etc/debian_version ]; then
        echo "  → Installing Mininet from apt..."
        apt-get install -y mininet > /dev/null 2>&1
        
        if command_exists mn; then
            echo "  ✓ Mininet installed successfully"
        else
            echo "  → Apt installation failed, trying from source..."
            
            # Install from source
            cd /tmp
            if [ ! -d "mininet" ]; then
                git clone https://github.com/mininet/mininet.git
            fi
            cd mininet
            git checkout 2.3.0  # Stable version
            
            # Install Mininet
            ./util/install.sh -nfv
            
            if command_exists mn; then
                echo "  ✓ Mininet installed from source"
            else
                echo "  ❌ Failed to install Mininet"
                exit 1
            fi
        fi
    else
        echo "  ❌ Unsupported OS for automatic Mininet installation"
        echo "  Please install Mininet manually: http://mininet.org/download/"
        exit 1
    fi
fi

echo ""
echo "Step 4: Installing FRRouting (FRR)..."
echo "--------------------------------------"

if command_exists vtysh; then
    FRR_VERSION=$(vtysh -v 2>&1 | head -1)
    echo "  ✓ FRR already installed: $FRR_VERSION"
else
    echo "  → FRR not found, installing..."
    
    # Add FRR GPG key
    curl -s https://deb.frrouting.org/frr/keys.asc | apt-key add - > /dev/null 2>&1
    
    # Add FRR repository
    FRRVER="frr-stable"
    echo "deb https://deb.frrouting.org/frr $(lsb_release -s -c) $FRRVER" | tee -a /etc/apt/sources.list.d/frr.list > /dev/null
    
    # Update and install
    apt-get update -qq
    apt-get install -y frr frr-pythontools > /dev/null 2>&1
    
    if command_exists vtysh; then
        echo "  ✓ FRR installed successfully"
    else
        echo "  ❌ Failed to install FRR"
        exit 1
    fi
fi

echo ""
echo "Step 5: Installing Python dependencies..."
echo "------------------------------------------"

PYTHON_PACKAGES=(
    "matplotlib"
    "networkx"
)

for pkg in "${PYTHON_PACKAGES[@]}"; do
    if python3 -c "import $pkg" 2>/dev/null; then
        echo "  ✓ $pkg (already installed)"
    else
        echo "  → Installing $pkg..."
        pip3 install "$pkg" -q
        echo "  ✓ $pkg installed"
    fi
done

echo ""
echo "Step 6: Configuring system settings..."
echo "---------------------------------------"

# Enable IP forwarding
if grep -q "^net.ipv4.ip_forward=1" /etc/sysctl.conf; then
    echo "  ✓ IP forwarding already enabled"
else
    echo "  → Enabling IP forwarding..."
    echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf
    sysctl -w net.ipv4.ip_forward=1 > /dev/null 2>&1
    echo "  ✓ IP forwarding enabled"
fi

# Disable IPv6 (optional, for cleaner routing tables)
if grep -q "^net.ipv6.conf.all.disable_ipv6=1" /etc/sysctl.conf; then
    echo "  ✓ IPv6 already disabled"
else
    echo "  → Disabling IPv6..."
    echo "net.ipv6.conf.all.disable_ipv6=1" >> /etc/sysctl.conf
    echo "net.ipv6.conf.default.disable_ipv6=1" >> /etc/sysctl.conf
    sysctl -w net.ipv6.conf.all.disable_ipv6=1 > /dev/null 2>&1
    sysctl -w net.ipv6.conf.default.disable_ipv6=1 > /dev/null 2>&1
    echo "  ✓ IPv6 disabled"
fi

echo ""
echo "Step 7: Verifying installation..."
echo "----------------------------------"

ALL_OK=true

# Check Mininet
if command_exists mn; then
    echo "  ✓ Mininet: $(mn --version 2>&1 | head -1)"
else
    echo "  ❌ Mininet: NOT FOUND"
    ALL_OK=false
fi

# Check FRR
if command_exists vtysh; then
    echo "  ✓ FRR: $(vtysh -v 2>&1 | head -1 | cut -d' ' -f1-3)"
else
    echo "  ❌ FRR: NOT FOUND"
    ALL_OK=false
fi

# Check Python
if command_exists python3; then
    echo "  ✓ Python: $(python3 --version)"
else
    echo "  ❌ Python: NOT FOUND"
    ALL_OK=false
fi

# Check iperf3
if command_exists iperf3; then
    echo "  ✓ iperf3: $(iperf3 --version | head -1)"
else
    echo "  ❌ iperf3: NOT FOUND"
    ALL_OK=false
fi

# Check Python packages
if python3 -c "import matplotlib, networkx" 2>/dev/null; then
    echo "  ✓ Python packages: matplotlib, networkx"
else
    echo "  ❌ Python packages: MISSING"
    ALL_OK=false
fi

echo ""
echo "=========================================="
if [ "$ALL_OK" = true ]; then
    echo "✅ Installation Complete!"
    echo "=========================================="
    echo ""
    echo "All dependencies are installed and ready."
    echo ""
    echo "Next steps:"
    echo "  1. Read README.md for usage instructions"
    echo "  2. Run: sudo ./setup_frr.sh"
    echo "  3. Run: sudo python3 run.py"
    echo ""
else
    echo "⚠️  Installation Incomplete"
    echo "=========================================="
    echo ""
    echo "Some dependencies failed to install."
    echo "Please check the errors above and install manually."
    echo ""
fi

echo "System Information:"
echo "-------------------"
echo "  OS: $(lsb_release -d | cut -f2)"
echo "  Kernel: $(uname -r)"
echo "  Python: $(python3 --version)"
echo "  Mininet: $(mn --version 2>&1 | head -1 || echo 'Not installed')"
echo "  FRR: $(vtysh -v 2>&1 | head -1 | cut -d' ' -f1-3 || echo 'Not installed')"
echo ""
