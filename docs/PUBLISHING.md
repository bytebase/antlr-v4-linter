# Publishing to PyPI

This document describes how to publish the `antlr-v4-linter` package to PyPI.

## Prerequisites

### Option 1: Trusted Publishing (Recommended)

Trusted publishing is more secure and doesn't require storing API tokens.

1. **For Production PyPI**:
   - Go to https://pypi.org/manage/project/antlr-v4-linter/settings/publishing/
   - Click "Add a new publisher"
   - Configure with:
     - Owner: `bytebase`
     - Repository: `antlr-v4-linter`
     - Workflow name: `publish.yml`
     - Environment: `pypi`

2. **For Test PyPI**:
   - Go to https://test.pypi.org/manage/project/antlr-v4-linter/settings/publishing/
   - Click "Add a new publisher"
   - Configure with:
     - Owner: `bytebase`
     - Repository: `antlr-v4-linter`
     - Workflow name: `publish.yml`
     - Environment: `testpypi`

### Option 2: API Tokens

If you prefer using API tokens:

1. **Generate tokens**:
   - PyPI: https://pypi.org/manage/account/token/
   - Test PyPI: https://test.pypi.org/manage/account/token/

2. **Add as GitHub secrets**:
   - Go to https://github.com/bytebase/antlr-v4-linter/settings/secrets/actions
   - Add `PYPI_API_TOKEN` with your PyPI token
   - Add `TEST_PYPI_API_TOKEN` with your Test PyPI token

## Publishing Process

### Automatic Release (via Git Tag)

```bash
# 1. Update version in pyproject.toml
# 2. Commit changes
git add pyproject.toml
git commit -m "Bump version to 0.1.2"
git push upstream main

# 3. Create and push tag
git tag 0.1.2
git push upstream 0.1.2
```

The GitHub Action will automatically:
- Build the package
- Publish to Test PyPI
- Publish to Production PyPI
- Create a GitHub Release

### Manual Release

1. Go to [GitHub Actions](https://github.com/bytebase/antlr-v4-linter/actions)
2. Select "Manual Release" workflow
3. Click "Run workflow"
4. Enter the version number
5. Choose whether to test on Test PyPI first

### Local Publishing (Emergency Only)

```bash
# Build the package
pip install build twine
python -m build

# Check the package
twine check dist/*

# Upload to Test PyPI
twine upload --repository testpypi dist/*

# Upload to Production PyPI
twine upload dist/*
```

## Troubleshooting

### "invalid-publisher" Error

This means trusted publishing isn't configured. Either:
1. Set up trusted publishing as described above, OR
2. Add API tokens as GitHub secrets

### Version Already Exists

PyPI doesn't allow re-uploading the same version. You must:
1. Increment the version number in `pyproject.toml`
2. Create a new tag

### Build Failures

Check that:
- `pyproject.toml` is valid
- All required files are committed
- Dependencies are properly specified

## Version Numbering

Follow semantic versioning (MAJOR.MINOR.PATCH):
- MAJOR: Breaking changes
- MINOR: New features (backward compatible)
- PATCH: Bug fixes (backward compatible)

Pre-release versions:
- Alpha: `0.1.3a1`
- Beta: `0.1.3b1`
- Release Candidate: `0.1.3rc1`