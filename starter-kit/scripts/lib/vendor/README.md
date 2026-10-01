# Vendored JavaScript tokenizer

`js-tokens.mjs` is the unchanged `index.js` from **js-tokens 10.0.0**, renamed so copied starter-kit scripts keep ESM semantics without a package.json. Its [MIT license](js-tokens.LICENSE) must accompany distributed copies. The tokenizer does not execute source code. Its optional React JSX mode is disabled; After Effects JSX uses the ordinary JavaScript token stream.

- Upstream: https://github.com/lydell/js-tokens
- Upstream release commit: `d7ec3643eac02418881ddb46ec420cfc10a653ba`
- Package: https://registry.npmjs.org/js-tokens/-/js-tokens-10.0.0.tgz
- Package integrity: `sha512-lM/UBzQmfJRo9ABXbPWemivdCW8V2G8FHaHdypQaIy523snUjog0W71ayWXTjiR+ixeMyVHN2XcpnTd/liPg/Q==`
- Source SHA-256: `04fadb05b1b179e1ca7ba5ca4ce82efa6169cb0b4ceff3917a83a4fe7c460dfd`

The archive integrity and source were checked on 2026-10-01. This vendored file has no runtime dependencies and requires no installation or network access. For an update, retrieve an explicitly selected version, verify integrity, review its source/license and rerun directive/include, regex/division and literal-boundary regressions. Tokenization identifies directive locations; the resulting source still goes through Node's syntax parser. Neither step establishes ExtendScript ES3/E4X or Adobe host compatibility.
