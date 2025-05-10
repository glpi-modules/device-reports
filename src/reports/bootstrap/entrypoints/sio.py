from fastapi import FastAPI
from socketio import ASGIApp, AsyncServer


def socketio_server() -> AsyncServer:
    sio_server = AsyncServer(async_mode="asgi", cors_allowed_origins="*")
    return sio_server


def socket_io_app(fastapi_app: FastAPI, server: AsyncServer) -> ASGIApp:
    sio_application = ASGIApp(socketio_server=server, other_asgi_app=fastapi_app)

    fastapi_app.add_route("/socket.io/", route=sio_application, methods=["GET", "POST"])
    fastapi_app.add_api_websocket_route("/socket.io/", sio_application)

    return sio_application
