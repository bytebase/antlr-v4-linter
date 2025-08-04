#!/bin/bash

# Upload to Test PyPI with verbose output
echo "📤 Uploading to Test PyPI (verbose mode)..."
echo "You'll be prompted for credentials:"
echo "  Username: __token__"
echo "  Password: <your-test-pypi-token>"
echo ""

uv run --with twine python -m twine upload --verbose --repository testpypi dist/*