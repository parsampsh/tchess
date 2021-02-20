## Contributing

#### Get started
To start development environment:

```bash
$ virtualenv venv -p python3
$ source venv/bin/activate
$ pip3 install -r requirements.txt
```

#### Tests
For running tests:

```bash
$ python3 test.py
# OR
$ ./test.py
```

For adding test, write a function in `test.py` and add the function to the `TESTS` list in `test.py`:

```python
def test_my_test_func():
    """ A Caption for my test """
    assert 1 == 1

TESTS = [
    # ...
    test_my_test_func,
    # ...
]
```

#### Pylint
For using **pylint** to check code quality, you can use make:

```bash
$ make pylint
```

#### Manpage
For generating manual page(man) in the `man/tchess.1`, you can run:

```bash
$ ./bin/generate-man-page.py
```

(This is possible ONLY on Unix systems).

#### TODO
To see project todos, run:

```bash
$ make todo
```

#### Releasing
To release a new version automaticaly:

```bash
$ ./bin/release.py <new-version>
$ ./bin/release.py 1.0
# OR
$ ./bin/release.py micro # bump a micro
$ ./bin/release.py minor # bump a minor
$ ./bin/release.py major # bump a major
$ ./bin/release.py # micro by default
```

The above commands will change the version. But they do not commit changes and create the tag.
To create tag and commit, use `--commit` option:

```bash
$ ./bin/release.py --commit
$ git push
```

After push, new release will be published into pypi by github workflows.
