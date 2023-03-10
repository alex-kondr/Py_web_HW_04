from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
from pathlib import Path
import json, logging, os, socket, urllib
from time import sleep


SERVER_ADDRESS = ("0.0.0.0", 3000)
SOCKET_ADDRESS = ("127.0.0.1", 5000)
HTML_PATH = Path("front-init")
LIST_FILES_HTML = []


class SocketUDP:
    
    def __init__(self, ip_port: tuple):
        self.ip_port = ip_port
    
    def run_server(self, path: Path):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(self.ip_port)
        
        
        try:
            while True:
                data, address = sock.recvfrom(1024)
                logging.debug(f"Received {data.decode()=} from: {address=}")
                data_parse = urllib.parse.unquote_plus(data.decode())
                data_dict = {key: value for key, value in [el.split("=") for el in data_parse.split("&")]}
                data_dict = {str(datetime.now()): data_dict}
                
                if not path.joinpath("storage").exists():
                    os.mkdir(path.joinpath("storage"))
                
                file = path.joinpath("storage/data.json")
                
                if file.exists():                
                    with open(file, "r") as fd:
                        json_dict = json.load(fd)                        
                else:
                    json_dict = {}

                json_dict.update(data_dict)
                
                with open(file, "w") as fd:
                    json.dump(json_dict, fd)
                
        except KeyboardInterrupt:
            print("Server socket stoped")
        finally:
            sock.close()        

    def run_client(self, data):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(data, self.ip_port)
        sock.close()
        

socket_server = SocketUDP(SOCKET_ADDRESS) 


class HtttpHandler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        parse_url = urllib.parse.urlparse(self.path)
        
        if parse_url.path == "/":
            self.send_html_file(HTML_PATH.joinpath("index.html"))
            
        elif parse_url.path[1:] in LIST_FILES_HTML:
            self.send_html_file(HTML_PATH.joinpath(parse_url.path[1:]))
            
        else:
            self.send_html_file(HTML_PATH.joinpath("error.html"))
            
    def do_POST(self):
        data = self.rfile.read(int(self.headers["Content-Length"]))
        
        socket_server.run_client(data)
        
        self.send_response(302)
        self.send_header("Location", "/")
        self.end_headers()
            
    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        
        with open(filename, "rb") as fd:
            self.wfile.write(fd.read())            

                        
def run_http_server(server=HTTPServer, handler=HtttpHandler):
    http = server(SERVER_ADDRESS, handler)
    
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()


def find_html_files(html_path):
    
    for file in html_path.iterdir():
        if file.is_file():
            LIST_FILES_HTML.append(file.name)
            
        
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format="%(message)s")
    
    find_html_files(HTML_PATH)    
       
    sock_server = Thread(target=socket_server.run_server, args=(HTML_PATH, ), daemon=True)
    sock_server.start()
    
    run_http_server()