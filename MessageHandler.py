import Config

class MessageHandler:

    def __init__(self, private : bool):
        self.private = private

    def broadcast(self, message : str) -> None:
        """Send a message to all players."""
        if self.private:
            # Send message to server to be sent to each player
            pass
        else:
            print(message)

    def whisper(self, message : str, player : int) -> None:
        if self.private:
            # Send message to server to be sent to the specified player
            pass
        else:
            print(message)

