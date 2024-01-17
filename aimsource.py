import keyboard, os, mss, requests, time, pygetwindow as gw, ctypes, numpy as np, win32api, win32con, cv2, math
from threading import Thread
from utils.SettingManager import SettingsManager
from colorama import Fore, Style

sct, screenshot, center = None, None, None
switchmodes = ("Hold", "Toggle")
user32, kernel = ctypes.windll.user32, np.ones((3, 3), np.uint8)

settings_manager = SettingsManager("config.json")

def CheckForUpdates():
    try:
        if "8" not in requests.get(url="https://raw.githubusercontent.com/Seconb/Arsenal-Colorbot/main/version.txt").text:
            print("Outdated version, redownload: https://github.com/Seconb/Arsenal-Colorbot/releases")
            exit(1337)
    except Exception as e:
        print(f"Error checking update: {e}\nContinuing anyway!")
        time.sleep(5)

def is_window_focused(window_title):
    try:
        window = gw.getWindowsWithTitle(window_title)[0]
        return window.isActive
    except IndexError:
        return False
    
def lclc():
    try:
        bind_mode = settings_manager.get("BINDMODE")
        if bind_mode.lower() in ["win32", "win32api", "win"]:
            aim_key_string = settings_manager.get("AIM_KEY")
            if "win32con" in aim_key_string:
                aim_key = eval(aim_key_string, {"win32con": win32con})
            else:
                aim_key = aim_key_string
            return win32api.GetAsyncKeyState(aim_key) < 0
    except Exception as e:
        print("Error checking key state:", e)


class trb0t:
    def __init__(self):
        self.AIMtoggled, self.switchmode, self.__clicks, self.__shooting = False, 1, 0, False

    def __stop(self):
        oldclicks = self.__clicks
        time.sleep(.05)
        if self.__clicks == oldclicks:
            user32.mouse_event(0x0004)

    def __delayedaim(self):
        self.__shooting = True
        time.sleep(settings_manager.get("TRIGGERBOT_DELAY") / 1000)
        user32.mouse_event(0x0002)
        self.__clicks += 1
        Thread(target=self.__stop).start()
        self.__shooting = False

    def process(self, sct):
        if is_window_focused("Roblox"):
            try:
                img, hsv = np.array(sct.grab(screenshot)), cv2.cvtColor(np.array(sct.grab(screenshot)), cv2.COLOR_BGR2HSV)
                mask, dilated = cv2.inRange(hsv, settings_manager.get("lower"), settings_manager.get("upper")), cv2.dilate(cv2.inRange(hsv, settings_manager.get("lower"), settings_manager.get("upper")), kernel, iterations=5)
                thresh, contours = cv2.threshold(dilated, 60, 255, cv2.THRESH_BINARY)[1], cv2.findContours(cv2.threshold(dilated, 60, 255, cv2.THRESH_BINARY)[1], cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[0]

                if contours:
                    contour, topmost = max(contours, key=cv2.contourArea), tuple(max(contours, key=cv2.contourArea)[contour[:, :, 1].argmin()][0])
                    x, y = topmost[0] - center + settings_manager.get("AIM_OFFSET_X"), topmost[1] - center + settings_manager.get("AIM_OFFSET_Y")
                    distance, x2, y2 = math.sqrt(x**2 + y**2), int(x * settings_manager.get("AIM_SPEED_X")), int(y * settings_manager.get("AIM_SPEED_Y"))

                    if distance <= settings_manager.get("AIM_FOV"):
                        user32.mouse_event(0x0001, x2, y2, 0, 0)
                        if settings_manager.get("TRIGGERBOT") != "disabled" and distance <= settings_manager.get("TRIGGERBOT_DISTANCE"):
                            if settings_manager.get("TRIGGERBOT_DELAY") != 0 and not self.__shooting:
                                Thread(target=self.__delayedaim).start()
                            else:
                                user32.mouse_event(0x0002)
                                self.__clicks += 1
                                Thread(target=self.__stop).start()

            except Exception as e:
                print("Error in processing: %s", e)

    def AIMtoggle(self):
        try:
            self.AIMtoggled = not self.AIMtoggled
            time.sleep(0.1)
        except Exception as e:
            print("Error toggling AIM:", e)

    def modeswitch(self):
        self.switchmode = (self.switchmode + 1) % 2
        time.sleep(1)

def print_setting(key, enabled_msg="On", disabled_msg="Off", color_enabled=Fore.GREEN, color_disabled=Fore.RED):
    setting = settings_manager.get(key)
    status = color_enabled + enabled_msg if setting != "disabled" else color_disabled + disabled_msg
    print(f"{key.replace('_', ' ').capitalize():20s}:", status + Style.RESET_ALL)

def print_banner(b0t: trb0t):
    try:
        os.system("cls")
        print(Style.BRIGHT + Fore.CYAN + """
    _   ___  ___ ___ _  _   _   _       ___ ___  _    ___  ___ ___  ___ _____ 
   /_\ | _ \/ __| __| \| | /_\ | |     / __/ _ \| |  / _ \| _ \ _ )/ _ \_   _|
  / _ \|   /\__ \ _|| .` |/ _ \| |__  | (_| (_) | |_| (_) |   / _ \ (_) || |  
 /_/ \_\_|_\|___/___|_|\_/_/ \_\____|  \___\___/|____\___/|_|_\___/\___/ |_|                                                                                                                                                                                                                      
""" + Style.RESET_ALL)
        print("====== Controls ======")
        print_setting("AIM_KEY", "Activate colorbot", "Activate colorbot", Fore.YELLOW, Fore.YELLOW)
        print_setting("SWITCH_MODE_KEY", "Switch toggle/hold")
        print_setting("UPDATE_KEY", "Update Config")
        if settings_manager.get("FOV_KEY_UP") != "disabled" and settings_manager.get("FOV_KEY_DOWN") != "disabled":
            print(f"{'Change FOV':20s}:", Fore.YELLOW + settings_manager.get("FOV_KEY_UP") + "/" + settings_manager.get("FOV_KEY_DOWN") + Style.RESET_ALL)
        print("==== Information =====")
        print("Toggle/Hold Mode     :", Fore.CYAN + switchmodes[b0t.switchmode] + Style.RESET_ALL)
        print("Aim FOV              :", Fore.CYAN + str(settings_manager.get("AIM_FOV")) + Style.RESET_ALL)
        print("Cam FOV              :", Fore.CYAN + str(settings_manager.get("CAM_FOV")) + Style.RESET_ALL)
        print_setting("TRIGGERBOT")
        print_setting("SMOOTHENING")
        print("Smoothening Factor   :", Fore.CYAN + str(settings_manager.get("SMOOTH_FACTOR")) + Style.RESET_ALL)
        print_setting("TRIGGERBOT_DELAY", "Delay: " + str(settings_manager.get("TRIGGERBOT_DELAY")), "No Delay")
        print("Aim Speed            :", Fore.CYAN + f"X: {settings_manager.get('AIM_SPEED_X')} Y: {settings_manager.get('AIM_SPEED_Y')}" + Style.RESET_ALL)
        print("Aim Offset           :", Fore.CYAN + f"X: {settings_manager.get('AIM_OFFSET_X')} Y: {settings_manager.get('AIM_OFFSET_Y')}" + Style.RESET_ALL)
        print("Aim Activated        :", (Fore.GREEN if b0t.AIMtoggled else Fore.RED) + str(b0t.AIMtoggled) + Style.RESET_ALL)
        print("Enemy Color          :", str(settings_manager.get("colorname") + settings_manager.get("COLOR")) + Style.RESET_ALL)
        print("======================")
        print(Style.BRIGHT + Fore.CYAN + "https://discord.gg/nDREsRUj9V for configs and help!" + Style.RESET_ALL)
    except Exception as e:
        print("Error printing banner:", e)

def update_settings_and_print_banner(b0t, settings_manager, key, increment=0):
    settings_manager.set(key, settings_manager.get(key) + increment)
    print_banner(b0t, settings_manager)

def process_aim_toggle(b0t, sct, mode):
    while b0t.AIMtoggled:
        b0t.process(sct)
        if mode == 0 and not lclc():
            break
        elif mode == 1 and lclc():
            break
    b0t.AIMtoggle()
    print_banner(b0t)

def main():
    os.system("title Colorbot")
    if not settings_manager.load_settings():
        print("Failed to load settings.")
        exit(1)

    # Initialize screenshot
    sct = mss.mss()
    screenshot = sct.monitors[0]
    
    cam_fov = settings_manager.get("CAM_FOV")
    screenshot["left"] = int((screenshot["width"] / 2) - (cam_fov / 2))
    screenshot["top"] = int((screenshot["height"] / 2) - (cam_fov / 2))
    screenshot["width"] = cam_fov
    screenshot["height"] = cam_fov
    center = cam_fov / 2

    b0t = trb0t()
    aim_key_was_pressed = False

    try:
        print_banner(b0t)
        while True:
            current_time = time.time()
            if settings_manager.get("SWITCH_MODE_KEY") != "disabled" and keyboard.is_pressed(settings_manager.get("SWITCH_MODE_KEY")):
                b0t.modeswitch()
                print_banner(b0t)
            if settings_manager.get("FOV_KEY_UP") != "disabled" and keyboard.is_pressed(settings_manager.get("FOV_KEY_UP")):
                update_settings_and_print_banner(b0t, settings_manager, "AIM_FOV", 5)
            if settings_manager.get("FOV_KEY_DOWN") != "disabled" and keyboard.is_pressed(settings_manager.get("FOV_KEY_DOWN")):
                update_settings_and_print_banner(b0t, settings_manager, "AIM_FOV", -5)
            if settings_manager.get("UPDATE_KEY") != "disabled" and keyboard.is_pressed(settings_manager.get("UPDATE_KEY")):
                print_banner(b0t)

            time.sleep(0.1)

            if lclc() or keyboard.is_pressed(settings_manager.get("AIM_KEY")):
                if not b0t.AIMtoggled:
                    b0t.AIMtoggle()
                    print_banner(b0t)
            
            time.sleep(0.1)

            if b0t.AIMtoggled:
                process_aim_toggle(b0t, sct, b0t.switchmode)
    except Exception as e:
        print("An error occurred:", e)

if __name__ == "__main__":
    main()
