class ClientMapping:
    def __init__(self):
        self._players = []

    def add(self, name, connection, id_):
        self._players.append(PlayerConnection(name, connection, id_))

    def get_name_from_connection(self, connection):
        for player in self._players:
            if player.get_connection() is connection:
                return player.get_name()

    def get_name_from_id(self, id_):
        for player in self._players:
            if player.get_id() == id_:
                return player.get_name()

    def get_id_from_connection(self, connection):
        for player in self._players:
            if player.get_connection() is connection:
                return player.get_id()

    def get_id_from_name(self, name):
        for player in self._players:
            if player.get_name() == name:
                return player.get_id()

    def get_connection_from_name(self, name):
        for player in self._players:
            if player.get_name() == name:
                return player.get_connection()

    def get_connection_from_id(self, id_):
        for player in self._players:
            if player.get_id() == id_:
                return player.get_connection()

    def get_all_names(self):
        return [player.get_name() for player in self._players]

    def get_all_ids(self):
        return [player.get_id() for player in self._players]

    def get_all_connections(self):
        return [player.get_connection() for player in self._players]

    def remove_connection(self, connection):
        for i, player in enumerate(self._players):
            if player.get_connection() is connection:
                self._players.pop(i)
                break

    def set_connection_name(self, connection, name):
        if self._mapping.get(connection):
            client = self._mapping[connection]
            client.set_name(name)
            self._reverse_mapping[name] = client

    def get_response_from_id(self, id_):
        for player in self._players:
            if player.get_id() == id_:
                return player.retrieve()

    def store(self, response, connection):
        for player in self._players:
            if player.get_connection() is connection:
                player.store(response)

    def __len__(self):
        return len(self._players)


class PlayerConnection:
    def __init__(self, name, connection, id_):
        self._name = name
        self._connection = connection
        self._queue = []
        self._id = id_ 

    def get_id(self):
        return self._id

    def get_name(self):
        return self._name

    def get_connection(self):
        return self._connection

    def store(self, response):
        self._queue = [response] 

    def retrieve(self):
        if len(self._queue) > 0:
            return self._queue.pop(0)
        else:
            return None








