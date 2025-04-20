# src/base/websockets/discover_sockets.py
from importlib import import_module
from pathlib import Path

def auto_discover_socket_routes_and_attach(app):
    sockets_root = Path("src/domains")

    for socket_file in sockets_root.glob("**/sockets/*.py"):
        if socket_file.name.startswith("_"):
            continue

        module_path = str(socket_file).replace("/", ".").replace(".py", "")
        mod = import_module(module_path)

        for attr in dir(mod):
            func = getattr(mod, attr)
            if callable(func) and attr.startswith("websocket_"):
                route_name = attr.replace("websocket_", "")
                app.add_api_websocket_route(f"/ws/{route_name}", func)
