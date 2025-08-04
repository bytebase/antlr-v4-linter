#!/bin/bash

# Upload using environment variables
echo "📤 Upload to Test PyPI using environment variables"
echo ""
echo "Enter your Test PyPI token (starts with pypi-):"
read -s TWINE_PASSWORD
export TWINE_PASSWORD

export TWINE_USERNAME=__token__
export TWINE_REPOSITORY=testpypi

echo ""
echo "Uploading with environment variables..."
uv run --with twine python -m twine upload dist/*

unset TWINE_PASSWORD
unset TWINE_USERNAME
unset TWINE_REPOSITORY

echo ""
echo "✅ If successful, test installation with:"
echo "  pip install -i https://test.pypi.org/simple/ antlr-v4-linter"