class ClientMapping:
    def __init__(self):
        self._mapping = {}
        self._reverse_mapping = {}

    def get_name(self, conn):
        if self._mapping.get(conn):
            return self._mapping[conn].get_name()
        return None

    def add_conn(self, conn):
        client = Client(conn) 
        self._mapping[conn] = client

    def set_conn_name(self, conn, name):
        if self._mapping.get(conn):
            client = self._mapping[conn]
            client.set_name(name)
            self._reverse_mapping[name] = client

    def get_message_with_name(self, name):
        return self._reverse_mapping[name].get_message()

    def set_message_with_name(self, name, message):
        self._reverse_mapping[name].set_message(message)


class Client:
    def __init__(self, connection, name=None):
        self._connection = connection
        self._queue = []
        self._name = name 

    def get_name(self):
        return self._name

    def set_name(self, name):
        self._name = name

    def get_conn(self):
        return self._connection

    def queue_message(self, message):
        self._queue = [message] 

    def get_message(self):
        if len(self.queue) > 0:
            return self._queue.pop(0)
        else:
            return None








