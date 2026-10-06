from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]/'docs'
class Handler(SimpleHTTPRequestHandler):
 def __init__(self,*a,**kw):super().__init__(*a,directory=str(ROOT),**kw)
 def translate_path(self,path):
  prefix='/hyperskill-projects'
  if path.startswith(prefix+'/'):path=path[len(prefix):]
  return super().translate_path(path)
ThreadingHTTPServer(('127.0.0.1',8779),Handler).serve_forever()
