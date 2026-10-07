/* Entry point for the current Tile renderer and local V6.6 geometry.
   Replaces the former SVG/depth-band contract explicitly:
   - global same-depth Y -> five aligned roots and aligned local module rows;
   - frozen X/card sizes/increasing height -> text metrics, actual contours,
     complete trays, canonical order and obstacle-free orthogonal routes.
   Assertions are implemented in the focused current-scene suite below. */
require('./local-geometry/validate.cjs');
