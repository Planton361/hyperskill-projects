# Vendored layout dependency

Runtime is offline and same-origin. `d3-flextree-2.1.2.cjs` is the unmodified
UMD bundle from `https://cdn.jsdelivr.net/npm/d3-flextree@2.1.2/build/d3-flextree.js`.
It works in both Node and the browser; it includes d3-hierarchy's implementation.

- d3-flextree **2.1.2**, Chris Maloney: WTFPL, [license](d3-flextree-LICENSE).
- Bundled d3-hierarchy: Mike Bostock, BSD-3-Clause, [license](d3-hierarchy-LICENSE).
- Bundle SHA256: `e4cd9feea0d126fd4839c39fb3526fb5806173e20e486ef703171e7803dd9d75`.

The [upstream API](https://github.com/Klortho/d3-flextree) defines variable
`nodeSize`, sibling `spacing` and an ordered, non-layered tree layout.
No package manager, runtime CDN, network acquisition or custom optimizer is used.
