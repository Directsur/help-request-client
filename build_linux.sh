#!/bin/bash
# Copyright (C) 2025-2026 Direct Sevilla Global Services SL
# SPDX-License-Identifier: AGPL-3.0-or-later
set -e

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
info()  { echo -e "${GREEN}[+]${NC} $*"; }
warn()  { echo -e "${YELLOW}[!]${NC} $*"; }
error() { echo -e "${RED}[✗]${NC} $*"; exit 1; }

APP_NAME="SolicitudAyuda"
APP_DIR="AppDir"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cd "$SCRIPT_DIR"

# ─── 1. Dependencias del sistema ───────────────────────────────────────────────
info "Comprobando dependencias del sistema..."
MISSING=()
for pkg in python3 python3-pip python3-tk; do
    dpkg -s "$pkg" &>/dev/null || MISSING+=("$pkg")
done
if [[ ${#MISSING[@]} -gt 0 ]]; then
    warn "Instalando: ${MISSING[*]}"
    sudo apt-get install -y -qq "${MISSING[@]}"
fi

# ─── 2. Entorno virtual ────────────────────────────────────────────────────────
info "Preparando entorno virtual..."
python3 -m venv .venv
.venv/bin/pip install --quiet --upgrade pip
.venv/bin/pip install --quiet -r requirements.txt

# ─── 3. PyInstaller → binario ─────────────────────────────────────────────────
info "Compilando con PyInstaller..."
.venv/bin/pyinstaller \
    --noconfirm \
    --clean \
    --name "$APP_NAME" \
    --onefile \
    --noconsole \
    --hidden-import "pynput.keyboard._xorg" \
    --hidden-import "pynput.mouse._xorg" \
    --hidden-import "PIL._tkinter_finder" \
    --collect-all jaraco \
    main.py

[[ -f "dist/$APP_NAME" ]] || error "PyInstaller no generó el binario"

# ─── 4. Icono ──────────────────────────────────────────────────────────────────
info "Generando icono..."
.venv/bin/python3 - <<'PYEOF'
from PIL import Image, ImageDraw
img = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)
draw.polygon([(128, 10), (250, 230), (6, 230)], fill="#c0392b")
draw.polygon([(128, 60), (210, 210), (46, 210)], fill="white")
draw.rectangle([116, 100, 140, 165], fill="#c0392b")
draw.ellipse([116, 175, 140, 199], fill="#c0392b")
img.save("help-request.png")
print("Icono generado.")
PYEOF

# ─── 5. Estructura AppDir ──────────────────────────────────────────────────────
info "Construyendo AppDir..."
rm -rf "$APP_DIR"
mkdir -p "$APP_DIR/usr/bin"
mkdir -p "$APP_DIR/usr/share/icons/hicolor/256x256/apps"

cp "dist/$APP_NAME"  "$APP_DIR/usr/bin/$APP_NAME"
cp "help-request.png" "$APP_DIR/usr/share/icons/hicolor/256x256/apps/help-request.png"
cp "help-request.png" "$APP_DIR/help-request.png"

# .desktop
cat > "$APP_DIR/$APP_NAME.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=Solicitudes de Ayuda
Comment=Cliente del sistema de solicitudes de ayuda
Exec=$APP_NAME
Icon=help-request
Categories=Utility;
StartupNotify=false
EOF

# AppRun
cat > "$APP_DIR/AppRun" <<'EOF'
#!/bin/bash
HERE="$(dirname "$(readlink -f "$0")")"
export PATH="$HERE/usr/bin:$PATH"
exec "$HERE/usr/bin/SolicitudAyuda" "$@"
EOF
chmod +x "$APP_DIR/AppRun"

# ─── 6. appimagetool ──────────────────────────────────────────────────────────
info "Descargando appimagetool si no está presente..."
if [[ ! -f "appimagetool-x86_64.AppImage" ]]; then
    curl -fsSL -o appimagetool-x86_64.AppImage \
        https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
    chmod +x appimagetool-x86_64.AppImage
fi

# ─── 7. Generar AppImage ──────────────────────────────────────────────────────
info "Generando AppImage..."
ARCH=x86_64 ./appimagetool-x86_64.AppImage "$APP_DIR" "${APP_NAME}-x86_64.AppImage"

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║      AppImage generada correctamente     ║"
echo "╚══════════════════════════════════════════╝"
echo ""
echo "  Archivo: ${APP_NAME}-x86_64.AppImage"
echo ""
echo "  Para instalar en el sistema:"
echo "    cp ${APP_NAME}-x86_64.AppImage ~/.local/bin/SolicitudAyuda"
echo "    chmod +x ~/.local/bin/SolicitudAyuda"
echo "    SolicitudAyuda   # el autoarranque se configura al primer inicio"
echo ""
warn "Nota: los atajos de teclado globales requieren X11 o XWayland."
warn "En sesiones Wayland puras el cliente avisará al iniciar."
