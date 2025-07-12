import importlib
import os
import logging

class PluginManager:
    def __init__(self):
        self.plugins = {}

    def load_plugins(self):
        plugins_dir = os.path.join(os.path.dirname(__file__), '..', 'plugins')
        for fname in os.listdir(plugins_dir):
            if fname.endswith('.py') and not fname.startswith('_'):
                module_name = f"plugins.default_plugins.{fname[:-3]}"
                try:
                    module = importlib.import_module(module_name)
                    for attr in dir(module):
                        cls = getattr(module, attr)
                        if isinstance(cls, type) and hasattr(cls, 'execute'):
                            self.plugins[cls.__name__] = cls()
                            logging.info(f"Loaded plugin: {cls.__name__}")
                except Exception as e:
                    logging.error(f"Failed to load plugin {fname}: {e}")

    def get_plugin(self, name):
        return self.plugins.get(name)