import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion
import logging
import os

class MQTTListener:
    def __init__(self, mqtt_config, macro_loader, plugin_manager):
        self.mqtt_config = mqtt_config
        self.macro_loader = macro_loader
        self.plugin_manager = plugin_manager
        self.topic_prefix = mqtt_config['topic_prefix']
        self.client = mqtt.Client(
            callback_api_version=CallbackAPIVersion.VERSION2,
            client_id=mqtt_config.get('client_id', 'macropad')
        )
        if mqtt_config.get('username'):
            self.client.username_pw_set(mqtt_config['username'], mqtt_config.get('password'))
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def start(self):
        self.client.connect(self.mqtt_config['broker'], self.mqtt_config['port'], self.mqtt_config['keepalive'])
        self.client.loop_forever()

    def on_connect(self, client, userdata, flags, reason_code, properties):
        logging.info(f"Connected to MQTT broker with result code {reason_code}")
        # Subscribe to all messages under the topic prefix using wildcard
        wildcard_topic = f"{self.topic_prefix}/+"
        client.subscribe(wildcard_topic)
        logging.info(f"Subscribed to topic: {wildcard_topic}")

    def on_message(self, client, userdata, msg):
        logging.info(f"Received MQTT message: topic={msg.topic}, payload={msg.payload}")
        try:
            # Extract folder from topic path
            topic_parts = msg.topic.split('/')
            if len(topic_parts) < 2:
                logging.warning(f"Invalid topic format: {msg.topic}")
                return
            
            folder_name = topic_parts[-1]  # Last part is the folder name (e.g., "default_macros")
            macro_id = msg.payload.decode('utf-8')
            
            logging.info(f"Processing: folder_name={folder_name}, macro_id={macro_id}")
            
            # Look for the folder in the root folders defined in the config
            target_folder_path = None
            for root_folder_path in self.macro_loader.folders:
                # Get the root folder name (e.g., "./macros" -> "macros")
                
                # Check if the folder name exists within this root folder on the filesystem
                folder_path = os.path.join(root_folder_path, folder_name)
                if os.path.isdir(folder_path):
                    target_folder_path = folder_path
                    break

            if not target_folder_path:
                logging.warning(f"Folder not found in configured root folders: {folder_name}")
                available_folders = [os.path.basename(f.rstrip('/')) for f in self.macro_loader.folders]
                logging.info(f"Available root folders: {available_folders}")
                return
            
            # Now look for the macro in that specific folder
            macro = self.macro_loader.find_macro(target_folder_path, macro_id)
            if not macro:
                logging.warning(f"Macro not found: folder={target_folder_path}, id={macro_id}")
                return
                
            plugin = self.plugin_manager.get_plugin(macro['plugin'])
            if not plugin:
                logging.error(f"Plugin not found: {macro['plugin']}")
                return
            if not plugin.validate_params(macro['params']):
                logging.error(f"Invalid params for macro: {macro_id}")
                return
            plugin.execute(macro['params'])
            logging.info(f"Executed macro: {macro_id} from folder: {target_folder_path}")
        except Exception as e:
            logging.exception(f"Error handling MQTT message: {e}")
