import json
import time
import logging
import sys

import example

fmt = "[%(levelname)6s] (%(name)40s.%(funcName)-15s-%(lineno)4d):\t%(message)s"


def download():
    example.download()


if __name__ == "__main__":
    # Logging settings
    level = logging.INFO
    if '-errors_only' in sys.argv:
        level = logging.ERROR
    if '-debug' in sys.argv:
        level = logging.DEBUG

    logging.basicConfig(stream=sys.stdout, level=level, format=fmt)

    # Run downloaders
    download()
