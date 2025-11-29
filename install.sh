#!/bin/bash

PROJECT_DIR=$(pwd)
VENV_DIR="$PROJECT_DIR/.venv"
REQUIREMENTS="$PROJECT_DIR/requirements.txt"
CREDS_FILE="creds.json"
ENV_FILE=".env"
SERVICE_NAME="djinni_parser"
SYSTEMD_USER_DIR="$HOME/.config/systemd/user"
LOCAL_SERVICE_FILE="$PROJECT_DIR/$SERVICE_NAME.service"
LOCAL_TIMER_FILE="$PROJECT_DIR/$SERVICE_NAME.timer"

RED="\033[0;31m"
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
CYAN="\033[0;36m"
NC="\033[0m"

log_info() { echo -e "${CYAN}[INFO]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_success() { echo -e "${GREEN}[OK]${NC} $1"; }

check_cmd() {
    if ! command -v "$1" &> /dev/null; then
        log_error "$1 is not installed or not in PATH."
    fi
}

cleanup() {
    echo ""
    log_warn "An error occurred. Rolling back changes..."

    if [ -d "$VENV_DIR" ]; then
       log_info "Removing virtual environment..."
       rm -rf "$VENV_DIR"
    fi

    if [ -f "$SYSTEMD_USER_DIR/$SERVICE_NAME.service" ]; then
        log_info "Removing systemd service file..."
        rm "$SYSTEMD_USER_DIR/$SERVICE_NAME.service"
    fi

    if [ -f "$SYSTEMD_USER_DIR/$SERVICE_NAME.timer" ]; then
        log_info "Removing systemd timer file..."
        rm "$SYSTEMD_USER_DIR/$SERVICE_NAME.timer"
    fi

    log_info "Rollback complete. Fix errors and try again."
}

set -e
trap 'cleanup' ERR

echo -e "${GREEN}=== Starting Installation ===${NC}"

if [ "$EUID" -eq 0 ]; then
    log_error "Please do not run this script as root (sudo). Run it as a regular user."
fi

log_info "Checking system requirements..."
check_cmd python3
check_cmd pip
check_cmd systemctl

if [ ! -f "$PROJECT_DIR/main.py" ]; then
    log_error "main.py not found in current directory."
fi
if [ ! -f "$REQUIREMENTS" ]; then
    log_error "requirements.txt not found."
fi
if [ ! -f "$ENV_FILE" ]; then
    log_error ".env file not found. Please create it first."
fi

log_success "System requirements met."

if [ -f "$PROJECT_DIR/$CREDS_FILE" ]; then
    log_info "Found $CREDS_FILE. Configuring .env..."

    if grep -q "CREDS_PATH" "$ENV_FILE"; then
        log_warn "CREDS_PATH already exists in .env. Skipping append."
    else
        echo "" >> "$ENV_FILE"
        echo "CREDS_PATH=\"$PROJECT_DIR/$CREDS_FILE\"" >> "$ENV_FILE"
        log_success "Added CREDS_PATH to .env"
    fi
else
    log_warn "$CREDS_FILE not found. Make sure your script can find credentials!"
fi

log_info "Setting up Python virtual environment..."

if [ -d "$VENV_DIR" ]; then
    log_warn "Virtual environment already exists. Skipping creation."
else
    python3 -m venv "$VENV_DIR"
    log_success "Created .venv"
fi

log_info "Installing dependencies from requirements.txt..."
"$VENV_DIR/bin/pip" install --upgrade pip -q
"$VENV_DIR/bin/pip" install -r "$REQUIREMENTS" -q
log_success "Dependencies installed."

if [ -f "$LOCAL_SERVICE_FILE" ] && [ -f "$LOCAL_TIMER_FILE" ]; then
    log_info "Found custom Systemd configurations in project directory."
    log_info "Using local $SERVICE_NAME.service and $SERVICE_NAME.timer"

    SERVICE_CONTENT=$(cat "$LOCAL_SERVICE_FILE")
    TIMER_CONTENT=$(cat "$LOCAL_TIMER_FILE")
else
    log_info "Custom Systemd configurations not found. Generating defaults..."

    SERVICE_CONTENT="[Unit]
Description=Djinni Parser Service
After=network-online.target

[Service]
Type=oneshot
WorkingDirectory=$PROJECT_DIR
ExecStart=$VENV_DIR/bin/python $PROJECT_DIR/main.py
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=default.target"

    TIMER_CONTENT="[Unit]
Description=Run Djinni Parser Daily at 12:00

[Timer]
OnCalendar=*-*-* 12:00:00
Persistent=true
Unit=$SERVICE_NAME.service

[Install]
WantedBy=timers.target"
fi

echo -e "\n${YELLOW}--- PROPOSED SYSTEMD CONFIGURATION ---${NC}"
echo -e "${CYAN}File: $SYSTEMD_USER_DIR/$SERVICE_NAME.service${NC}"
echo "$SERVICE_CONTENT"
echo -e "\n${CYAN}File: $SYSTEMD_USER_DIR/$SERVICE_NAME.timer${NC}"
echo "$TIMER_CONTENT"
echo -e "${YELLOW}--------------------------------------${NC}"

read -p "Do you want to proceed with writing these files and enabling the timer? (y/N): " confirm
if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
    log_warn "Installation cancelled by user."
    exit 0
fi

mkdir -p "$SYSTEMD_USER_DIR"

log_info "Writing configuration files..."
echo "$SERVICE_CONTENT" > "$SYSTEMD_USER_DIR/$SERVICE_NAME.service"
echo "$TIMER_CONTENT" > "$SYSTEMD_USER_DIR/$SERVICE_NAME.timer"

log_info "Reloading systemd daemon..."
systemctl --user daemon-reload

log_info "Enabling and starting timer..."
systemctl --user enable "$SERVICE_NAME.timer"
systemctl --user start "$SERVICE_NAME.timer"

systemctl --user disable "$SERVICE_NAME.service" 2>/dev/null || true

echo -e "\n${GREEN}=== Installation Completed Successfully! ===${NC}"
echo "Check status with: systemctl --user status $SERVICE_NAME.timer"
echo "Check logs with:   journalctl --user -u $SERVICE_NAME.service"
