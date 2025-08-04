#!/bin/bash

# Upload to Production PyPI
echo "⚠️  WARNING: This will upload to the PRODUCTION PyPI!"
echo "Make sure you've tested on Test PyPI first."
echo ""
read -p "Continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Upload cancelled."
    exit 1
fi

echo ""
echo "📤 Uploading to PyPI..."
echo "You'll be prompted for credentials:"
echo "  Username: __token__"
echo "  Password: <your-pypi-token>"
echo ""

uv run --with twine python -m twine upload dist/*

echo ""
echo "✅ If successful, package is now available!"
echo "  Anyone can install with:"
echo "    pip install antlr-v4-linter"
echo "    uv pip install antlr-v4-linter"
echo ""
echo "📦 View your package at:"
echo "  https://pypi.org/project/antlr-v4-linter/"