#!/usr/bin/env bash
# Installer script untuk Digital Works Modded (Linux)
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

echo "=========================================================="
echo "Menyiapkan Digital Works 3.0 (Arch Modded Edition)..."
echo "=========================================================="

# Berikan izin eksekusi
chmod +x digitalworks dw_undo_engine.py run_linux.sh 2>/dev/null || true

# Periksa Wine
if command -v wine &>/dev/null; then
    echo "[OK] Wine terdeteksi: $(wine --version)"
else
    echo "[PERINGATAN] Wine belum terpasang. Pasang dengan: sudo pacman -S wine (Arch) atau sudo apt install wine (Debian/Ubuntu)"
fi

# Periksa Python3
if command -v python3 &>/dev/null; then
    echo "[OK] Python 3 terdeteksi: $(python3 --version)"
else
    echo "[PERINGATAN] Python3 belum terpasang."
fi

# Opsi integrasi menu desktop
mkdir -p "$HOME/.local/share/applications" "$HOME/.local/share/icons"
cp -f "$DIR/digital-works.png" "$HOME/.local/share/icons/digital-works.png" 2>/dev/null || true

cat << DESKTOP_EOF > "$HOME/.local/share/applications/digitalworks-arch.desktop"
[Desktop Entry]
Name=Digital Works (Arch Modded)
Comment=Digital Logic Simulator - Modded for Arch Linux
Exec=$DIR/digitalworks %F
Icon=$HOME/.local/share/icons/digital-works.png
Terminal=false
Type=Application
Categories=Development;Engineering;Education;
MimeType=application/x-digitalworks;
StartupNotify=true
Path=$DIR
DESKTOP_EOF

echo "[OK] Desktop Entry telah ditambahkan ke menu aplikasi sistem Anda!"
echo "Selesai! Anda dapat langsung menjalankan dengan: ./digitalworks"
