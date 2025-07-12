from plugins.base import BasePlugin
import keyboard
import time
from typing import List, Union


class KeyboardActionsPlugin(BasePlugin):
    def __init__(self):
        super().__init__()
        self.valid_actions = ['press', 'release', 'type', 'hotkey']

    def execute(self, params):
        action = params.get('action', '').lower()
        keys = params.get('keys', [])
        text = params.get('text', '')
        delay = params.get('delay', 0.1)  # delay between actions in seconds

        if action not in self.valid_actions:
            print(f"Invalid action: {action}")
            return

        try:
            if action == 'press':
                self._handle_press(keys)
            elif action == 'release':
                self._handle_release(keys)
            elif action == 'type':
                self._handle_type(text, delay)
            elif action == 'hotkey':
                self._handle_hotkey(keys)

        except Exception as e:
            print(f"Error executing keyboard action: {e}")

    def _handle_press(self, keys: Union[str, List[str]]):
        """Press and hold the specified key(s)"""
        if isinstance(keys, str):
            keyboard.press(keys)
        else:
            for key in keys:
                keyboard.press(key)
                time.sleep(0.05)  # Small delay between multiple key presses

    def _handle_release(self, keys: Union[str, List[str]]):
        """Release the specified key(s)"""
        if isinstance(keys, str):
            keyboard.release(keys)
        else:
            for key in keys:
                keyboard.release(key)
                time.sleep(0.05)

    def _handle_type(self, text: str, delay: float):
        """Type the specified text with optional delay"""
        keyboard.write(text, delay=delay)

    def _handle_hotkey(self, keys: List[str]):
        """Press multiple keys as a hotkey combination"""
        keyboard.press_and_release('+'.join(keys))

    def validate_params(self, params):
        """Validate the parameters for the keyboard action"""
        action = params.get('action', '').lower()

        if action not in self.valid_actions:
            return False

        if action in ['press', 'release', 'hotkey']:
            keys = params.get('keys')
            if not keys:
                return False
            if not isinstance(keys, (str, list)):
                return False

        elif action == 'type':
            text = params.get('text')
            if not isinstance(text, str):
                return False

        return True

    def cleanup(self):
        """Ensure all keys are released when plugin is cleaned up"""
        keyboard.unhook_all()