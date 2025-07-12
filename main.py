import logging
import os
import sys
import threading
from core.config import load_config
from core.mqtt import MQTTListener
from core.macro_loader import MacroLoader
from core.plugin_manager import PluginManager

# Add these imports for system tray
import pystray
from pystray import MenuItem as item
from PIL import Image, ImageDraw

def setup_logging(config):
    log_cfg = config['logging']
    os.makedirs(os.path.dirname(log_cfg['file']), exist_ok=True)
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    
    # Set up root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_cfg['level'].upper(), logging.INFO))
    
    # Clear any existing handlers
    root_logger.handlers.clear()
    
    # Create file handler
    file_handler = logging.FileHandler(log_cfg['file'])
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

def get_image():
    ico = "res/glyphic.png"
    image = Image.open(ico) if os.path.exists(ico) else Image.new('RGB', (64, 64), color='white')
    draw = ImageDraw.Draw(image)
    return image

class App:
    def __init__(self):
        self.config = load_config()
        setup_logging(self.config)
        logging.info("Starting MQTT Macropad")
        self.macro_loader = MacroLoader(self.config['macros']['folders'])
        self.plugin_manager = PluginManager()
        self.plugin_manager.load_plugins()
        self.mqtt_listener = MQTTListener(
            self.config['mqtt'],
            self.macro_loader,
            self.plugin_manager
        )
        self.mqtt_thread = threading.Thread(target=self.mqtt_listener.start, daemon=True)
        self.mqtt_thread.start()
        self.icon = pystray.Icon("MQTT Macropad", get_image(), "MQTT Macropad", self.create_menu())

    def create_menu(self):
        return pystray.Menu(
            item('Reload Macros & Plugins', self.reload_macros_plugins),
            item('Restart MQTT Client', self.restart_mqtt),
            item('Restart Program', self.restart_program),
            item('Quit', self.quit)
        )

    def reload_macros_plugins(self, icon, item):
        logging.info("Reloading macros and plugins...")
        self.macro_loader = MacroLoader(self.config['macros']['folders'])
        self.plugin_manager = PluginManager()
        self.plugin_manager.load_plugins()
        self.mqtt_listener.macro_loader = self.macro_loader
        self.mqtt_listener.plugin_manager = self.plugin_manager
        logging.info("Reloaded macros and plugins.")

    def restart_mqtt(self, icon, item):
        logging.info("Restarting MQTT client...")
        # Stop current client
        try:
            self.mqtt_listener.client.disconnect()
        except Exception as e:
            logging.error(f"Error disconnecting MQTT client: {e}")
        # Start new client in a new thread
        self.mqtt_listener = MQTTListener(
            self.config['mqtt'],
            self.macro_loader,
            self.plugin_manager
        )
        self.mqtt_thread = threading.Thread(target=self.mqtt_listener.start, daemon=True)
        self.mqtt_thread.start()
        logging.info("MQTT client restarted.")

    def restart_program(self, icon, item):
        logging.info("Restarting program...")
        python = sys.executable
        os.execl(python, python, *sys.argv)

    def quit(self, icon, item):
        logging.info("Exiting program...")
        icon.stop()
        os._exit(0)

    def run(self):
        self.icon.run()

def main():
    app = App()
    app.run()

if __name__ == "__main__":
    main()