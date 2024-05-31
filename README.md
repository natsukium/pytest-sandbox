# pytest-sandbox

disable network access in pytest and mark xfail

This plugin automatically adds several fixtures when installed.
These fixtures monkey-patch libraries such as `http`, `aiohttp`, and `httpcore`,
calling `pytest.xfail` instead of making network connections.

I'm working on a PoC in the following branch:
<https://github.com/natsukium/nixpkgs/tree/pytest-sandbox/init>

## known limitations

- Network accesses that occur during the collection phase of pytest cannot be mocked.
Files must be manually excluded from the search path.
For example, see <https://github.com/chroma-core/chroma/blob/3ec627d2f6472a6aee76b7be365b3ad98ea77389/chromadb/test/property/test_cross_version_persist.py#L31-L34>

- Tests that run as subprocesses, such as tests for executables, cannot be mocked.
For example, see <https://github.com/openmm/pdbfixer/blob/6bf10e138f6475f6f1850dae78d7bf1b420a1612/pdbfixer/tests/test_cli.py#L26-L56>
