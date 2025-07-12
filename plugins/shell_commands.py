import subprocess
from plugins.base import BasePlugin

class ShellCommandPlugin(BasePlugin):
    def execute(self, params):
        command = params.get('command')
        if command:
            try:
                subprocess.run(command, shell=True, check=True)
            except subprocess.CalledProcessError as e:
                print(f"Error executing command: {e}")

    def validate_params(self, params):
        return 'command' in params