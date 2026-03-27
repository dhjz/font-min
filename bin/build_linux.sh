#!/bin/bash

cd "$(dirname "$0")/.."
echo "========================================"
echo "Start building Linux executable"
echo "========================================"

if [ ! -d "dist" ]; then
  mkdir -p dist
fi

echo ""
echo "[1/6] Installing dependencies..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo ""
    echo "Failed to install dependencies! Please check error messages."
    exit 1
fi

echo ""
echo "[2/6] Installing PyInstaller..."
pip install pyinstaller

if [ $? -ne 0 ]; then
    echo ""
    echo "Failed to install PyInstaller! Please check error messages."
    exit 1
fi

echo ""
echo "[3/6] Cleaning old build files..."
rm -rf build
rm -f dist/dfont-linux-amd64
rm -f dist/dfont-linux-arm64

ARCHS=("amd64" "arm64")

for ARCH in "${ARCHS[@]}"; do
  echo ""
  echo "[4/6] Building for $ARCH..."
  
  if [ "$ARCH" == "amd64" ]; then
    OUTPUT_NAME="dfont-linux-amd64"
  else
    OUTPUT_NAME="dfont-linux-arm64"
  fi
  
  pyinstaller --onefile --clean --name "$OUTPUT_NAME" --add-data "web:web" main.py
  
  if [ $? -ne 0 ]; then
    echo ""
    echo "Build failed for $ARCH! Please check error messages."
    exit 1
  fi
  
  echo ""
  echo "[5/6] Moving $ARCH executable to dist..."
  mv "dist/$OUTPUT_NAME" "dist/"
done

echo ""
echo "[6/6] Cleaning temporary files..."
rm -rf build

echo ""
echo "Setting executable permissions..."
chmod +x dist/dfont-linux-amd64
chmod +x dist/dfont-linux-arm64

echo ""
echo "========================================"
echo "Build completed!"
echo "Executables location:"
echo "  - dist/dfont-linux-amd64"
echo "  - dist/dfont-linux-arm64"
echo "========================================"
