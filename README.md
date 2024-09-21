# Xray is online!

Parse and validate xray.json configuration in your browser.

The basic idea is: Many GUI clients do not provide good error messages if a
JSON config fails to load. Users don't want to run the core directly to find
the error message. Therefore, let's use a browser tool in the style of
jsonlint.com.

[Try it out here](https://mmmray.github.io/xray-online/)

Because some configuration validation happens after parsing, some mistakes are
not caught, only most typing mistakes. If you find an obvious gap that bothers
you, raise an issue.

## Contributing

xray-online uses a patched version of xray-core compiled to WASM. The build process is entirely driven through the `Makefile`. A POSIX shell is recommended, WSL is probably mandatory on Windows.

* `make build` to build the WASM module from scratch.
* `make dev-lite` to download the WASM module from GitHub instead.
* `make serve` to launch the development server.
