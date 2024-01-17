import json, numpy as np
from colorama import Fore

class SettingsManager:
    def __init__(self, config_file_path):
        self.config_file_path = config_file_path
        self.settings = {}
        self.color_map = {
            "yellow": ((38, 255, 203), (30, 255, 201), Fore.YELLOW),
            "blue": ((123, 255, 217), (113, 206, 189), Fore.BLUE),
            "pink": ((150, 255, 201), (150, 255, 200), Fore.MAGENTA),
            "magenta": ((150, 255, 201), (150, 255, 200), Fore.MAGENTA),
            "purple": ((150, 255, 201), (150, 255, 200), Fore.MAGENTA),
            "green": ((60, 255, 201), (60, 255, 201), Fore.GREEN),
            "cyan": ((90, 255, 201), (90, 255, 201), Fore.CYAN),
            "red": ((0, 255, 201), (0, 255, 201), Fore.RED),
            "0000ff": ((123, 255, 255), (120, 147, 69), Fore.BLUE),
            "aimblox": ((4, 225, 206), (0, 175, 119), Fore.LIGHTRED_EX),
            "black": ((0, 0, 0), (0, 0, 0), Fore.WHITE)
        }

    def load_settings(self):
        try:
            with open(self.config_file_path, 'r') as file:
                self.settings = json.load(file)
            self._process_colors()
            self._validate_settings()
        except Exception as e:
            print(f"Error loading settings: {e}")
            return False
        return True

    def _process_colors(self):
        color_name = self.settings.get("COLOR", "").lower()
        if color_name in self.color_map:
            color_data = self.color_map[color_name]
            upper, lower, _ = color_data if len(color_data) == 3 else (color_data + (None,))[:3]
            self.settings["upper"] = np.array(upper, dtype="uint8")
            self.settings["lower"] = np.array(lower, dtype="uint8")
            self.settings["colorname"] = getattr(Fore, color_name.upper(), Fore.WHITE)
        else:
            if color_name == "custom":
                # Custom color processing logic here
                pass
            else:
                # Handle unknown color
                pass

    # We can do config validation here, I provided a few examples.
    def _validate_settings(self):
        errors = []

        # Example: Type Checking
        if not isinstance(self.settings.get("AIM_SPEED_X"), (float, int)):
            errors.append("AIM_SPEED_X must be a number")

        # Example: Range Checking
        if self.settings.get("CAM_FOV") < 75 or self.settings.get("CAM_FOV") > 120:
            errors.append("CAM_FOV must be between 75 and 120")

        # Example: Value Checking
        valid_colors = ["yellow", "blue", "pink", "magenta", "purple", "green", "cyan", "red", "0000ff", "aimblox", "black"]
        if self.settings.get("COLOR").lower() not in valid_colors:
            errors.append(f"COLOR must be one of {valid_colors}")

        # Example: Dependent Settings
        if self.settings.get("SMOOTHENING") == "enabled" and self.settings.get("SMOOTH_FACTOR") <= 0:
            errors.append("SMOOTH_FACTOR must be greater than 0 when SMOOTHENING is enabled")

        # Handling Errors
        if errors:
            raise ValueError("Invalid configuration: " + "; ".join(errors))

    # Auto sets each config item into the settings object, makes it easier to work with.
    def get(self, key, default=None):
        return self.settings.get(key, default)
    
    # Allow the settings to be adjusted while the script is running
    def set(self, key, value):
        self.settings[key] = value

    # Allow all current settings to be saved if needed by calling this function
    def save_settings(self):
            try:
                with open(self.settings_file, 'w') as file:
                    json.dump(self.settings, file, indent=4)
            except IOError:
                print(f"Error writing to the settings file '{self.settings_file}'.")