# pip requirements files

## Index

- [`default.txt`](default.txt)
  Default requirements
- [`extras.txt`](extras.txt)
  Optional requirements
- [`test.txt`](test.txt)
  Requirements for running test suite
- [`doc.txt`](doc.txt)
  Requirements for building the documentation (see `../doc/`)

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
