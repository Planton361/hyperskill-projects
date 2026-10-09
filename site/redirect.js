/* Preserve earlier MyAtlas bookmarks after separating the application repo. */
(() => {
  const prefix = '/hyperskill-projects/';
  const relative = location.pathname.startsWith(prefix) ? location.pathname.slice(prefix.length) : '';
  const allowed = /^(knowledge-map|leetcode-atlas|leetcode-progress)\/(?:index\.html|global\.html)?$/;
  const route = allowed.test(relative) ? relative : 'knowledge-map/';
  const target = new URL(route, 'https://planton361.github.io/myatlas/');
  target.search = location.search;
  target.hash = location.hash;
  location.replace(target.href);
})();
