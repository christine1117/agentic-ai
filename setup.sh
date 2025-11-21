#!/bin/bash
# PersonaGym Green Agent Setup Script
# Team: EmpaTeam

set -e  # Exit on error

echo "=========================================="
echo "PersonaGym Green Agent Setup"
echo "Team: EmpaTeam"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored messages
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "ℹ $1"
}

# Check Python version
echo "Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
REQUIRED_VERSION="3.11"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 11) else 1)" 2>/dev/null; then
    print_error "Python 3.11 or higher is required. Found: $PYTHON_VERSION"
    print_info "Install Python 3.11+:"
    print_info "  Ubuntu/Debian: sudo apt install python3.11"
    print_info "  Mac: brew install python@3.11"
    print_info "  Or download from: https://www.python.org/downloads/"
    exit 1
else
    print_success "Python version OK: $PYTHON_VERSION"
fi

# Create virtual environment
echo ""
echo "Creating virtual environment..."
if [ -d "venv" ]; then
    print_warning "Virtual environment already exists. Skipping creation."
else
    python3 -m venv venv
    print_success "Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate
print_success "Virtual environment activated"

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
print_success "pip upgraded"

# Install dependencies
echo ""
echo "Installing dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    print_success "Dependencies installed"
else
    print_error "requirements.txt not found!"
    exit 1
fi

# Check for API keys
echo ""
echo "Checking environment variables..."
if [ -z "$OPENAI_API_KEY" ]; then
    print_warning "OPENAI_API_KEY not set"
    echo ""
    echo "To set your OpenAI API key:"
    echo "  export OPENAI_API_KEY='your-key-here'  # Linux/Mac"
    echo "  \$env:OPENAI_API_KEY='your-key-here'    # Windows PowerShell"
    echo ""
    echo "Or create a .env file:"
    echo "  echo 'OPENAI_API_KEY=your-key-here' > .env"
    echo ""
else
    print_success "OPENAI_API_KEY is set"
fi

if [ -z "$ANTHROPIC_API_KEY" ]; then
    print_warning "ANTHROPIC_API_KEY not set (optional)"
    print_info "For ensemble evaluation, set ANTHROPIC_API_KEY"
else
    print_success "ANTHROPIC_API_KEY is set"
fi

# Check for agent card
echo ""
echo "Checking configuration files..."
if [ -f "green_agent_card.toml" ]; then
    print_success "green_agent_card.toml found"
    
    # Check if URLs are updated
    if grep -q "YOUR_PUBLIC_IP" green_agent_card.toml; then
        print_warning "Agent card contains placeholder URLs"
        echo ""
        echo "Please update green_agent_card.toml with your public IP:"
        echo "  1. Find your public IP: curl ifconfig.me"
        echo "  2. Edit green_agent_card.toml"
        echo "  3. Replace YOUR_PUBLIC_IP with your actual IP"
        echo ""
    else
        print_success "Agent card URLs configured"
    fi
else
    print_error "green_agent_card.toml not found!"
    exit 1
fi

# Create output directory
echo ""
echo "Creating output directories..."
mkdir -p evaluation_results
mkdir -p logs
print_success "Output directories created"

# Test imports
echo ""
echo "Testing Python imports..."
python3 -c "
import sys
try:
    import openai
    import anthropic
    import toml
    import asyncio
    print('All imports successful')
    sys.exit(0)
except ImportError as e:
    print(f'Import error: {e}')
    sys.exit(1)
"

if [ $? -eq 0 ]; then
    print_success "All Python imports working"
else
    print_error "Some imports failed"
    exit 1
fi

# Validate agent card
echo ""
echo "Validating agent card..."
python3 << 'EOF'
import toml
import sys

try:
    with open('green_agent_card.toml', 'r') as f:
        config = toml.load(f)
    
    required_sections = ['agent', 'launcher', 'evaluation', 'personas', 'scenarios']
    for section in required_sections:
        if section not in config:
            print(f"Missing section: {section}")
            sys.exit(1)
    
    print("Agent card structure is valid")
    sys.exit(0)
except Exception as e:
    print(f"Error validating agent card: {e}")
    sys.exit(1)
EOF

if [ $? -eq 0 ]; then
    print_success "Agent card validation passed"
else
    print_error "Agent card validation failed"
    exit 1
fi

# Summary
echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
print_success "Environment ready for deployment"
echo ""
echo "Next steps:"
echo ""
echo "1. Set your API keys (if not already done):"
echo "   export OPENAI_API_KEY='your-key-here'"
echo "   export ANTHROPIC_API_KEY='your-key-here'  # Optional"
echo ""
echo "2. Update green_agent_card.toml with your public IP"
echo ""
echo "3. Test locally:"
echo "   python green_agent.py"
echo ""
echo "4. Deploy to AgentBeats:"
echo "   python agentbeats_runner.py green_agent_card.toml \\"
echo "     --launcher_host YOUR_IP \\"
echo "     --launcher_port 8002 \\"
echo "     --agent_host YOUR_IP \\"
echo "     --agent_port 8001 \\"
echo "     --model_type openai \\"
echo "     --model_name gpt-4o"
echo ""
echo "5. Register at: https://agentbeats.org"
echo ""
echo "For detailed instructions, see DEPLOYMENT.md"
echo ""
print_info "To activate the virtual environment in future sessions:"
echo "  source venv/bin/activate  # Linux/Mac"
echo "  venv\\Scripts\\activate     # Windows"
echo ""

# Make the script remind about deactivation
echo "To deactivate the virtual environment later:"
echo "  deactivate"
echo ""