import os
import sys
import time
import psutil
import subprocess
import ctypes
import threading
from PIL import Image, ImageDraw
from pystray import Icon, Menu, MenuItem

def create_image(color1, color2):
    width = 64
    height = 64
    image = Image.new('RGB', (width, height), color1)
    dc = ImageDraw.Draw(image)
    dc.rectangle(
        (width // 2, 0, width, height // 2),
        fill=color2)
    dc.rectangle(
        (0, height // 2, width // 2, height),
        fill=color2)
    return image

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def is_process_running(process_name):
    for proc in psutil.process_iter(['pid', 'name']):
        if process_name.lower() in proc.info['name'].lower():
            return True
    return False

def start_process(executable_path):
    subprocess.Popen(executable_path, shell=True)

def restart_as_admin():
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, ' '.join(sys.argv), None, 1)
        sys.exit()

def main():
    restart_as_admin()

    process_name = "MiSmartShare.exe"
    executable_path = r"C:\Program Files\MI\AIoT\launch.exe"
    interval = 600  # 10 minutes
    wait_time = 60  # 1 minute
    start_count = 0

    def update_icon(icon):
        while True:
            mi_running = is_process_running(process_name)
            daemon_status = "Running" if is_process_running("your_script_name_here.py") else "Stopped"
            icon.title = f"Daemon: {daemon_status}\nMiSmartShare: {'Running' if mi_running else 'Stopped'}\nStart Count: {start_count}"
            time.sleep(5)

    def daemon_task(icon):
        nonlocal start_count
        nonlocal interval
        while True:
            if not is_process_running(process_name):
                start_process(executable_path)
                start_count += 1
            time.sleep(interval)

    def on_double_click(icon, item):
        nonlocal start_count
        nonlocal interval
        if not is_process_running(process_name):
            start_process(executable_path)
            start_count += 1
            interval = 600  # Reset interval to 10 minutes

    menu = Menu(MenuItem('Execute Now', on_double_click))

    icon = Icon("status_icon", create_image('green', 'blue'), "Status Icon", menu)
    threading.Thread(target=update_icon, args=(icon,)).start()
    threading.Thread(target=daemon_task, args=(icon,)).start()
    icon.run()

if __name__ == "__main__":
    main()
