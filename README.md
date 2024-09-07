# Xray is online!

Parse and validate xray.json configuration in your browser.

The basic idea is: Many GUI clients do not provide good error messages if a
JSON config fails to load. Users don't want to run the core directly to find
the error message. Therefore, let's use a browser tool in the style of
jsonlint.com.

[Try it out here](https://mmmray.github.io/xray-online/)

This uses a fork of xray that has been refactored so it can (partially) compile
to wasm. Your config is not sent to any server.

Because some configuration validation happens after parsing, some mistakes are
not caught, only most typing mistakes. If you find an obvious gap that bothers
you, raise an issue.
