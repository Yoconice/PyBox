import tkinter as tk
from tkinter import ttk
import pydirectinput
import threading
import time
from pynput import keyboard
import sys
import ctypes
import gc


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


class GameClicker:
    def __init__(self, root):
        self.root = root
        # 修复：title 是方法，不是属性
        self.root.title("游戏连点器 独立间隔版")
        self.root.geometry("420x320")

        self.running = False
        self.click_thread = None

        # 两个独立参数
        self.space_ms = 1000  # 松开 -> 下次按下 的间隔
        self.press_ms = 10  # 按下 -> 松开 的按住时长

        pydirectinput.FAILSAFE = False
        pydirectinput.PAUSE = 0.0

        self.setup_ui()
        self.listener = keyboard.Listener(on_press=self.handle_hotkey)
        self.listener.start()

    def setup_ui(self):
        frame = ttk.Frame(self.root, padding=20)
        frame.pack(fill=tk.X, expand=True)

        if not is_admin():
            admin_warn = ttk.Label(frame, text="⚠️ 请以管理员身份运行", foreground="red")
            admin_warn.grid(row=0, column=0, columnspan=2, pady=5)

        # 1. 松开到下次点击间隔
        ttk.Label(frame, text="松开到下次点击间隔(ms)：").grid(row=1, column=0, sticky=tk.W, pady=6)
        self.space_entry = ttk.Entry(frame)
        self.space_entry.insert(0, "1000")
        self.space_entry.grid(row=1, column=1, sticky=tk.EW, pady=6, padx=4)

        # 2. 按下到松开时长
        ttk.Label(frame, text="按住鼠标时长(ms)：").grid(row=2, column=0, sticky=tk.W, pady=6)
        self.press_entry = ttk.Entry(frame)
        self.press_entry.insert(0, "10")
        self.press_entry.grid(row=2, column=1, sticky=tk.EW, pady=6, padx=4)

        # 状态
        self.status_label = ttk.Label(frame, text="状态：已停止", foreground="red", font=("黑体", 11))
        self.status_label.grid(row=3, column=0, columnspan=2, pady=15)

        # 开始停止按钮分开
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=4, column=0, columnspan=2, sticky=tk.EW, pady=6)

        self.start_btn = ttk.Button(btn_frame, text="▶ 开始", command=self.start_click)
        self.start_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

        self.stop_btn = ttk.Button(btn_frame, text="⏹ 停止", command=self.stop_click, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=5)

        ttk.Label(frame, text="快捷键 F8 开始 / F9 停止", foreground="gray").grid(row=5, column=0, columnspan=2, pady=8)

        frame.columnconfigure(1, weight=1)

    def read_config(self):
        try:
            space = int(self.space_entry.get())
            press = int(self.press_entry.get())
            if space <= 0 or press <= 0:
                return None
            return space / 1000.0, press / 1000.0
        except:
            return None

    def start_click(self):
        cfg = self.read_config()
        if not cfg:
            self.status_label.config(text="错误：请输入正整数", foreground="orange")
            return

        self.space_ms, self.press_ms = cfg
        self.running = True

        self.status_label.config(
            text=f"运行中｜间隔:{int(self.space_ms * 1000)}ms 按住:{int(self.press_ms * 1000)}ms",
            foreground="green"
        )
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)

        self.click_thread = threading.Thread(target=self.click_loop, daemon=True)
        self.click_thread.start()

    def stop_click(self):
        self.running = False
        self.status_label.config(text="状态：已停止", foreground="red")
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)

    def click_loop(self):
        gc.disable()
        try:
            while self.running:
                # 按下
                pydirectinput.mouseDown(button='left', _pause=False)
                # 按住指定时长
                time.sleep(self.press_ms)
                # 松开
                pydirectinput.mouseUp(button='left', _pause=False)

                # 从松开后直接空隔完整设定时间
                self.precise_sleep(self.space_ms)
        finally:
            gc.enable()

    def precise_sleep(self, t):
        s = time.perf_counter()
        while time.perf_counter() - s < t:
            time.sleep(0.0001)

    def handle_hotkey(self, key):
        if key == keyboard.Key.f8:
            self.root.after(0, self.start_click)
        elif key == keyboard.Key.f9:
            self.root.after(0, self.stop_click)

    def on_close(self):
        self.running = False
        self.listener.stop()
        self.root.destroy()


if __name__ == "__main__":
    if not is_admin():
        try:
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        except:
            pass
        sys.exit()

    root = tk.Tk()
    app = GameClicker(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()