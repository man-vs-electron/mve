import BaseHTTPServer
import glob
import sys, traceback
from urlparse import parse_qs, urlparse
from mve.utils import eprint

class Server(BaseHTTPServer.HTTPServer):    
    def __init__(self, port, load_modules=True):
        BaseHTTPServer.HTTPServer.__init__(self, ('', port), MyHandler)
        self.modules = {}
        if load_modules:
            eprint("Loading modules")
            for file in glob.glob("module_*.py"):
                eprint(file)
                self.modules[file[7:-3]]=__import__(file[:-3].replace("/", ".")).execute
            eprint("Modules loaded: "+str(self.modules.keys())+"\n\n")

    def finish_request(self, request, client_address):
        request.settimeout(10)
        BaseHTTPServer.HTTPServer.finish_request(self, request, client_address)

    def go_blocking(self):
        try:
            self.serve_forever()
        except KeyboardInterrupt:
            pass
        self.server_close()


class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    """Main Handler for Smithers.
    """
    
    def do_GET(s):
        """Issues HTTP requests to appropriate modules.

        The first part of any HTTP request is the module.
        If the module has been loaded, call that 
        module's execute function.  If not, reply with "No such module."  
        """
        try:
            parts = s.path.split('?')[0].split("/")[1:]
            query_dict = parse_qs(urlparse(s.path).query)
            if len(parts)>0 and parts[0] in s.server.modules:
                execute = s.server.modules[parts[0]]
                execute(s, parts, query_dict)
            else:
                s.send_response(404)
                s.end_headers()
                eprint("Error.  No Such Module: %s" % s.path)
        except:
            e = sys.exc_info()[0]
            traceback.print_exc()
