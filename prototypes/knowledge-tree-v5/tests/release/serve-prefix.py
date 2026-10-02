"""Local static Pages-path simulation. Not part of the public build."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

DOCS = Path(__file__).resolve().parents[4] / 'docs'
PREFIX = '/hyperskill-projects/'


class Handler(SimpleHTTPRequestHandler):
    def translate_path(self, path):
        pathname = urlsplit(path).path
        if not pathname.startswith(PREFIX):
            return str(DOCS / '__unmapped_preview_test_path__')
        return super().translate_path('/' + pathname[len(PREFIX):])


if __name__ == '__main__':
    ThreadingHTTPServer(('127.0.0.1', 8775), partial(Handler, directory=str(DOCS))).serve_forever()
