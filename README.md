# pytest-sandbox

disable network access in pytest and mark xfail

This plugin automatically adds several fixtures when installed.
These fixtures monkey-patch libraries such as `http`, `aiohttp`, and `httpcore`,
calling `pytest.xfail` instead of making network connections.

I'm working on a PoC in the following branch:
<https://github.com/natsukium/nixpkgs/tree/pytest-sandbox/init>

## known limitations

- Tests that run as subprocesses, such as tests for executables, cannot be mocked.
For example, see <https://github.com/openmm/pdbfixer/blob/6bf10e138f6475f6f1850dae78d7bf1b420a1612/pdbfixer/tests/test_cli.py#L26-L56>

## patched methods

### http

- `http.client.HTTPConnection.__init__`

### aiohttp

- `aiohttp.ClientSession.__init__`

### fsspec

- `fsspec.implementations.http.HTTPFileSystem.__init__`

### httpcore

- `httpcore._sync.connection.HTTPConnection.handle_request`
- `httpcore._async.connection.AsyncHTTPConnection.handle_async_request`

### pycares

- `pycares.Channel.__init__`
