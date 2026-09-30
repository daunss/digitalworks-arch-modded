#!/usr/bin/env bash
# Script peluncur Digital Works Modded untuk Linux (Arch, Ubuntu, Debian, Fedora, dll.)
set -e
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

chmod +x digitalworks dw_undo_engine.py 2>/dev/null || true

# Periksa apakah wine tersedia
if ! command -v wine &>/dev/null; then
    echo "⚠️ Wine belum terpasang di sistem Linux Anda."
    echo "Silakan pasang Wine terlebih dahulu (contoh: sudo pacman -S wine atau sudo apt install wine)."
    exit 1
fi

./digitalworks "$@"
