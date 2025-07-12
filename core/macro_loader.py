import os
import yaml
import logging

class MacroLoader:
    def __init__(self, folders):
        self.folders = folders

    def find_macro(self, folder, macro_id):
        for root in self.folders:
            macro_path = os.path.join(root, folder, f"{macro_id}.yaml")
            if os.path.isfile(macro_path):
                with open(macro_path, 'r', encoding='utf-8') as f:
                    try:
                        macro = yaml.safe_load(f)
                        macro['id'] = macro_id
                        return macro
                    except Exception as e:
                        logging.error(f"Failed to load macro {macro_path}: {e}")
        return None