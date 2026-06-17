#!/bin/bash
# Copyright (C) 2025-2026 Direct Sevilla Global Services SL
# SPDX-License-Identifier: AGPL-3.0-or-later
# Script de construcción para macOS — genera SolicitudAyuda.app y SolicitudAyuda.dmg
# Requisitos: macOS 11+, Python 3.10+, Homebrew (para create-dmg opcional)
set -e

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
info()  { echo -e "${GREEN}[+]${NC} $*"; }
warn()  { echo -e "${YELLOW}[!]${NC} $*"; }
error() { echo -e "${RED}[✗]${NC} $*"; exit 1; }

APP_NAME="SolicitudAyuda"
BUNDLE_ID="es.centrosalud.solicitudayuda"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DIST_DIR="$SCRIPT_DIR/dist"
APP_PATH="$DIST_DIR/$APP_NAME.app"
DMG_PATH="$DIST_DIR/$APP_NAME.dmg"

cd "$SCRIPT_DIR"

# ─── 1. Python ─────────────────────────────────────────────────────────────────
info "Comprobando Python..."
PYTHON=$(command -v python3.12 || command -v python3.11 || command -v python3.10 || command -v python3)
[[ -z "$PYTHON" ]] && error "Python 3.10+ requerido"
PY_VER=$("$PYTHON" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
info "Usando Python $PY_VER en $PYTHON"

# ─── 2. Entorno virtual ────────────────────────────────────────────────────────
info "Preparando entorno virtual..."
"$PYTHON" -m venv .venv
.venv/bin/pip install --quiet --upgrade pip
.venv/bin/pip install --quiet -r requirements.txt
# pynput en macOS necesita pyobjc para captura de eventos de bajo nivel
.venv/bin/pip install --quiet pyobjc-framework-Quartz pyobjc-framework-Cocoa

# ─── 3. Icono .icns ────────────────────────────────────────────────────────────
info "Generando icono..."
.venv/bin/python3 - <<'PYEOF'
import os
from PIL import Image, ImageDraw

sizes = [16, 32, 64, 128, 256, 512, 1024]
iconset = "SolicitudAyuda.iconset"
os.makedirs(iconset, exist_ok=True)

for size in sizes:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    m = size / 256
    draw.polygon(
        [(128*m, 10*m), (250*m, 230*m), (6*m, 230*m)],
        fill="#c0392b",
    )
    draw.polygon(
        [(128*m, 60*m), (210*m, 210*m), (46*m, 210*m)],
        fill="white",
    )
    draw.rectangle([116*m, 100*m, 140*m, 165*m], fill="#c0392b")
    draw.ellipse([116*m, 175*m, 140*m, 199*m], fill="#c0392b")
    img.save(f"{iconset}/icon_{size}x{size}.png")
    if size <= 512:
        img2 = img.resize((size*2, size*2), Image.LANCZOS)
        img2.save(f"{iconset}/icon_{size}x{size}@2x.png")

print("Imágenes del iconset generadas.")
PYEOF

iconutil -c icns SolicitudAyuda.iconset -o SolicitudAyuda.icns
info "Icono SolicitudAyuda.icns generado."

# ─── 4. PyInstaller → .app ─────────────────────────────────────────────────────
info "Compilando con PyInstaller..."

# Para generar un binario universal (Apple Silicon + Intel), descomenta:
#   --target-arch universal2 \
# Requiere que todas las dependencias tengan ruedas universal2 disponibles.
# La arquitectura nativa (x86_64 en Intel, arm64 en M1/M2) es suficiente para distribución.

.venv/bin/pyinstaller \
    --noconfirm \
    --clean \
    --name "$APP_NAME" \
    --windowed \
    --noconsole \
    --onedir \
    --osx-bundle-identifier "$BUNDLE_ID" \
    --osx-info-plist macos_info.plist \
    --icon SolicitudAyuda.icns \
    --hidden-import "pynput.keyboard._darwin" \
    --hidden-import "pynput.mouse._darwin" \
    --hidden-import "PIL._tkinter_finder" \
    --hidden-import "Quartz" \
    --hidden-import "AppKit" \
    --collect-all pyobjc \
    main.py

[[ -d "$APP_PATH" ]] || error "PyInstaller no generó el bundle .app"
info "Bundle creado: $APP_PATH"

# ─── 5. Permisos del ejecutable ────────────────────────────────────────────────
# Asegura que el binario dentro del bundle sea ejecutable
chmod +x "$APP_PATH/Contents/MacOS/$APP_NAME"

# ─── 6. Eliminar cuarentena (builds locales) ──────────────────────────────────
# Evita el bloqueo de Gatekeeper en distribución sin firma de Apple
xattr -cr "$APP_PATH" 2>/dev/null || true

# ─── 7. Empaquetar en .dmg ────────────────────────────────────────────────────
info "Creando imagen de disco .dmg..."

# Nombre temporal para la imagen fuente
STAGING_DIR="$DIST_DIR/dmg-staging"
rm -rf "$STAGING_DIR"
mkdir -p "$STAGING_DIR"

cp -R "$APP_PATH" "$STAGING_DIR/"

# Enlace simbólico a /Applications para que el usuario arrastre la app
ln -s /Applications "$STAGING_DIR/Aplicaciones"

# Crea el .dmg con hdiutil (disponible en cualquier Mac sin herramientas extra)
hdiutil create \
    -volname "Solicitud de Ayuda" \
    -srcfolder "$STAGING_DIR" \
    -ov \
    -format UDZO \
    -imagekey zlib-level=9 \
    "$DMG_PATH"

rm -rf "$STAGING_DIR"

# ─── 8. Limpieza ──────────────────────────────────────────────────────────────
rm -rf SolicitudAyuda.iconset build

echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║      Paquete macOS generado correctamente    ║"
echo "╚══════════════════════════════════════════════╝"
echo ""
echo "  App:  $APP_PATH"
echo "  DMG:  $DMG_PATH"
echo ""
echo "  Para distribuir:"
echo "    Entrega el archivo .dmg al usuario."
echo "    El usuario lo abre, arrastra 'SolicitudAyuda' a /Aplicaciones"
echo "    y en el primer arranque autoriza el permiso de Accesibilidad."
echo ""
warn "Nota: sin firma Apple (Developer ID), macOS mostrará un aviso."
warn "El usuario debe ir a Sistema → Privacidad y Seguridad → 'Abrir de todas formas'"
warn "o usar:  sudo xattr -cr /Applications/SolicitudAyuda.app"
