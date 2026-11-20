from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs


def get_authorization_code():
    result = {"code": None, "error": None}

    class CallbackHandler(BaseHTTPRequestHandler):

        def do_GET(self):
            parsed_url = urlparse(self.path)

            if parsed_url.path != "/oauth/callback":
                self.send_response(404)
                self.end_headers()
                return

            params = parse_qs(parsed_url.query)

            if "error" in params:
                result["error"] = params["error"][0]
                message = "Salesforce authorization was not successful."
            elif "code" in params:
                result["code"] = params["code"][0]
                message = "Salesforce authorization received. You can close this browser tab."
            else:
                result["error"] = "Authorization code was not received."
                message = result["error"]

            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(message.encode("utf-8"))

        def log_message(self, format, *args):
            pass

    server = HTTPServer(("127.0.0.1", 8080), CallbackHandler)
    server.timeout = 180

    print("Waiting for Salesforce authorization callback...")
    server.handle_request()
    server.server_close()

    if result["error"]:
        raise RuntimeError(result["error"])

    if not result["code"]:
        raise TimeoutError("No Salesforce callback received within 3 minutes.")

    return result["code"]