# pip requirements files

## Index

These files are the optional dependencies that are not listed in `pyproject.toml`.
For those listed in `pyproject.toml` use `pip install .[$target]`

- [`example.txt`](example.txt)
  Requirements for gallery examples
- [`release.txt`](release.txt)
  Requirements for making releases

## Examples

### Installing requirements

```bash
$ pip install -U -r requirements/example.txt
```

### Running the tests

```bash
$ pip install -U .[default,test]
```
