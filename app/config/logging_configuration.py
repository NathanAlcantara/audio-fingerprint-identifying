import logging
import sys


def config_logger():
    log = logging.getLogger("werkzeug")
    log.setLevel(logging.ERROR)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - [%(levelname)s]: %(message)s",
        stream=sys.stdout,
    )


def graphql_logging_middleware(next, root, info, **args):
    if not root:
        logging.info("%s -> %s", info.field_name, args)
    return next(root, info, **args)
