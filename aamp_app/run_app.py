import webbrowser
from threading import Timer
from app import app


def main():
    host = "localhost"
    port = 8080
    url = f"http://{host}:{port}"
    Timer(10, webbrowser.open(url))

    app.run(host=host, port=port, debug=False)


main()
