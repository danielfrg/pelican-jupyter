# Releasing

## Upload to test PyPI

```shell
export VERSION=1.0.0
git checkout -b release-${VERSION}

git commit -am "Release ${VERSION}.rc0" --allow-empty
git tag ${VERSION}.rc0

make cleanall
make build
make upload-test

# Create venv and install rc version
pip install --extra-index-url=https://test.pypi.org/simple 'pelican-jupyter[test]'==${VERSION}rc0
pytest --pyargs pelican_jupyter

# Delete rc tag
git tag -d ${VERSION}.rc0
```

Merge branch when CI passes

## Upload to PyPI

- Update `CHANGELOG.md`
- Update `README.md` and docs as needed

```shell
export VERSION=1.0.0

git commit -am "Release ${VERSION}" --allow-empty
git tag ${VERSION}

make cleanall
make build
make upload-pypi
git push origin ${VERSION}
git push
```
