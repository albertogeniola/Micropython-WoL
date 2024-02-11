class InvalidConfiguration(Exception):
    def __int__(self, message):
        self._message = message

    @property
    def message(self):
        return self._message