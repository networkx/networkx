# pip requirements files

## Index

- [`default.txt`](default.txt)
  Default requirements
- [`extra.txt`](extra.txt)
  Optional requirements that may require extra steps to install
- [`example.txt`](example.txt)
  Requirements for gallery examples
- [`test.txt`](test.txt)
  Requirements for running test suite
- [`doc.txt`](doc.txt)
  Requirements for building the documentation (see `../doc/`)
- [`developer.txt`](developer.txt)
  Requirements for developers
- [`release.txt`](release.txt)
  Requirements for making releases

## Examples

### Installing requirements

```bash
$ pip install -U -r requirements/default.txt
```

### Running the tests

```bash
$ pip install -U -r requirements/default.txt
$ pip install -U -r requirements/test.txt
```
