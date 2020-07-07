# pip requirements files

## Index

- [`default.txt`](default.txt)
  Default requirements
- [`optional.txt`](optional.txt)
  Optional requirements that are easy to install.
- [`extras.txt`](extras.txt)
  Optional requirements that may require extra steps to install.
- [`test.txt`](test.txt)
  Requirements for running test suite
- [`doc.txt`](doc.txt)
  Requirements for building the documentation (see `../doc/`)
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
