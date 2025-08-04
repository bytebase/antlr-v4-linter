#!/bin/bash

# Upload to Test PyPI
echo "📤 Uploading to Test PyPI..."
echo "You'll be prompted for credentials:"
echo "  Username: __token__"
echo "  Password: <your-test-pypi-token>"
echo ""

uv run --with twine python -m twine upload --repository testpypi dist/*

echo ""
echo "✅ If successful, test installation with:"
echo "  uv pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple antlr-v4-linter"