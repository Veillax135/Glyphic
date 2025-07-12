class BasePlugin:
    def execute(self, params):
        raise NotImplementedError

    def validate_params(self, params):
        return True