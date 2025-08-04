#!/bin/bash

# ANTLR v4 Linter Publishing Script
# This script builds and publishes the package to PyPI

set -e  # Exit on error

echo "🚀 ANTLR v4 Linter Publishing Script"
echo "====================================="

# Check for uv installation
if ! command -v uv &> /dev/null; then
    echo "❌ Error: uv is not installed"
    echo "   Install with: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Step 1: Install build tools
echo "📦 Installing build tools..."
uv pip install --upgrade build twine

# Step 2: Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf dist/ build/ src/*.egg-info

# Step 3: Run tests (optional)
read -p "Run tests before building? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🧪 Running tests..."
    python3 -m pytest || { echo "❌ Tests failed. Aborting."; exit 1; }
fi

# Step 4: Build the package
echo "🔨 Building package..."
python3 -m build

# Step 5: Check the build
echo "✅ Checking package..."
python3 -m twine check dist/*

# Step 6: Display package info
echo ""
echo "📋 Package contents:"
ls -lh dist/

# Step 7: Confirm upload
echo ""
echo "Package ready for upload!"
echo "Choose upload destination:"
echo "1) Test PyPI (test.pypi.org)"
echo "2) Production PyPI (pypi.org)"
echo "3) Skip upload"
read -p "Enter choice (1-3): " choice

case $choice in
    1)
        echo "📤 Uploading to Test PyPI..."
        python3 -m twine upload --repository testpypi dist/*
        echo ""
        echo "✅ Package uploaded to Test PyPI!"
        echo "Test installation with:"
        echo "  uv pip install --index-url https://test.pypi.org/simple/ antlr-v4-linter"
        ;;
    2)
        echo "⚠️  Warning: This will upload to the production PyPI registry!"
        read -p "Are you sure? (yes/no) " confirm
        if [ "$confirm" = "yes" ]; then
            echo "📤 Uploading to PyPI..."
            python3 -m twine upload dist/*
            echo ""
            echo "✅ Package uploaded to PyPI!"
            echo "Install with:"
            echo "  uv pip install antlr-v4-linter"
            echo "  pip install antlr-v4-linter"
        else
            echo "Upload cancelled."
        fi
        ;;
    3)
        echo "Upload skipped. Package files are in dist/"
        ;;
    *)
        echo "Invalid choice. Upload skipped."
        ;;
esac

echo ""
echo "🎉 Done!"