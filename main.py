import logging

from app import create_app


if __name__ == '__main__':
    app = create_app()
    logging.basicConfig(level=logging.DEBUG)
    app.run()
