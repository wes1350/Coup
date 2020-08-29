from coup import app
from coup.socketio_handlers import run_socketio
from coup.utils.argument_parsing import parse_args

if __name__ == "__main__":
    parsed_args = parse_args()
    keep_client_order = parsed_args["keep_client_order"]
    run_socketio(app, '0.0.0.0', keep_client_order, parsed_args)