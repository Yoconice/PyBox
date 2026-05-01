import tkinter as tk
from tkinter import ttk, scrolledtext
import pydirectinput
import threading
import time
import random
import os
from datetime import datetime
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
        self.root.title("鼠标连点器")
        self.root.geometry("350x420")  # 窗口高度减小

        self.running = False
        self.click_thread = None
        self.click_count = 0

        self.base_space = 1.0
        self.space_jitter = 0.0
        self.base_press = 0.05
        self.press_jitter = 0.0

        pydirectinput.FAILSAFE = False
        pydirectinput.PAUSE = 0.0

        self.setup_ui()
        self.listener = keyboard.Listener(on_press=self.handle_hotkey)
        self.listener.start()

    def setup_ui(self):
        # 顶部：控制面板
        top_frame = ttk.Frame(self.root, padding=15)
        top_frame.pack(fill=tk.X)

        # 底部：日志区域（高度减小）
        bottom_frame = ttk.Frame(self.root, padding=(15, 0, 15, 15))
        bottom_frame.pack(fill=tk.BOTH, expand=True)

        # ---------------- 顶部内容 ----------------
        if not is_admin():
            admin_warn = ttk.Label(top_frame, text="⚠️ 请以管理员身份运行", foreground="red")
            admin_warn.pack(pady=5)

        input_frame = ttk.Frame(top_frame)
        input_frame.pack(fill=tk.X, pady=10)

        # 第一行：点击间隔
        ttk.Label(input_frame, text="点击间隔(ms)：").grid(row=0, column=0, sticky=tk.W, pady=6)
        self.space_entry = ttk.Entry(input_frame, width=16)
        self.space_entry.insert(0, "1000")
        self.space_entry.grid(row=0, column=1, sticky=tk.EW, pady=6, padx=(4, 15))

        ttk.Label(input_frame, text="±").grid(row=0, column=2, sticky=tk.W, pady=6)
        self.space_jitter_entry = ttk.Entry(input_frame, width=8)
        self.space_jitter_entry.insert(0, "0")
        self.space_jitter_entry.grid(row=0, column=3, sticky=tk.EW, pady=6)

        # 第二行：松开时长
        ttk.Label(input_frame, text="松开时长(ms)：").grid(row=1, column=0, sticky=tk.W, pady=6)
        self.press_entry = ttk.Entry(input_frame, width=16)
        self.press_entry.insert(0, "50")
        self.press_entry.grid(row=1, column=1, sticky=tk.EW, pady=6, padx=(4, 15))

        ttk.Label(input_frame, text="±").grid(row=1, column=2, sticky=tk.W, pady=6)
        self.press_jitter_entry = ttk.Entry(input_frame, width=8)
        self.press_jitter_entry.insert(0, "0")
        self.press_jitter_entry.grid(row=1, column=3, sticky=tk.EW, pady=6)

        input_frame.columnconfigure(1, weight=1)
        input_frame.columnconfigure(3, weight=1)

        self.status_label = ttk.Label(top_frame, text="状态：已停止", foreground="red", font=("黑体", 11))
        self.status_label.pack(pady=10)

        btn_frame = ttk.Frame(top_frame)
        btn_frame.pack(fill=tk.X, pady=5)

        self.start_btn = ttk.Button(btn_frame, text="▶ 开始", command=self.start_click)
        self.start_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

        self.stop_btn = ttk.Button(btn_frame, text="⏹ 停止", command=self.stop_click, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=5)

        ttk.Label(top_frame, text="【 F8 开始 / F9 停止 】", foreground="gray").pack(pady=8)

        # ---------------- 底部内容 ----------------
        # 直接把表头作为标题
        header_frame = ttk.Frame(bottom_frame)
        header_frame.pack(fill=tk.X, pady=(0, 2))

        # 使用等宽字体显示表头，和内容对齐
        header_label = ttk.Label(
            header_frame,
            text=" 次数          间隔          时长",
            font=("Consolas", 10, "bold")
        )
        header_label.pack(side=tk.LEFT)

        # 日志区域高度减小
        self.log_text = scrolledtext.ScrolledText(
            bottom_frame,
            width=30,
            height=4,  # 高度设为4行
            font=("Consolas", 10)
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # 初始分隔线
        # self.log_text.insert(tk.END, "--------------------------------\n")
        self.log_text.config(state=tk.DISABLED)

        # 底部按钮：清空日志（宽） + 导出（窄）
        log_btn_frame = ttk.Frame(bottom_frame)
        log_btn_frame.pack(fill=tk.X, pady=(10, 0))

        self.clear_btn = ttk.Button(log_btn_frame, text="清空日志")
        self.clear_btn.config(command=self.clear_log)
        self.clear_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 10))

        self.export_btn = ttk.Button(log_btn_frame, text="导出", width=8)
        self.export_btn.config(command=self.export_log)
        self.export_btn.pack(side=tk.RIGHT, padx=(10, 0))

    def append_log(self, count, space_ms, press_ms):
        self.root.after(0, self._append_log_impl, count, space_ms, press_ms)

    def _append_log_impl(self, count, space_ms, press_ms):
        self.log_text.config(state=tk.NORMAL)
        line = f"{count:05d}        {space_ms:6d}       {press_ms:6d}\n"
        self.log_text.insert(tk.END, line)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def append_separator(self):
        self.root.after(0, self._append_separator_impl)

    def _append_separator_impl(self):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, "--------------------------------\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def clear_log(self):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.insert(tk.END, "--------------------------------\n")
        self.log_text.config(state=tk.DISABLED)
        self.click_count = 0

    def export_log(self):
        try:
            now = datetime.now()
            time_str = now.strftime("%Y%m%d%H%M%S")
            filename = f"{time_str} {self.click_count:05d}.txt"

            if getattr(sys, 'frozen', False):
                base_dir = os.path.dirname(sys.executable)
            else:
                base_dir = os.path.dirname(os.path.abspath(__file__))

            filepath = os.path.join(base_dir, filename)

            self.log_text.config(state=tk.NORMAL)
            # 导出时加上表头
            log_content = " 次数          间隔          时长\n" + self.log_text.get(1.0, tk.END)
            self.log_text.config(state=tk.DISABLED)

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(log_content)

            self.status_label.config(text=f"导出成功：{filename}", foreground="green")
            self.root.after(3000, lambda: self.status_label.config(text="状态：已停止", foreground="red"))

        except Exception as e:
            self.status_label.config(text=f"导出失败：{str(e)}", foreground="orange")
            self.root.after(3000, lambda: self.status_label.config(text="状态：已停止", foreground="red"))

    def read_config(self):
        try:
            space = int(self.space_entry.get())
            space_jit = int(self.space_jitter_entry.get())
            press = int(self.press_entry.get())
            press_jit = int(self.press_jitter_entry.get())

            if space <= 0 or space_jit < 0 or press <= 0 or press_jit < 0:
                return None

            return (
                space / 1000.0,
                space_jit / 1000.0,
                press / 1000.0,
                press_jit / 1000.0
            )
        except:
            return None

    def start_click(self):
        if self.running:
            return

        cfg = self.read_config()
        if not cfg:
            self.status_label.config(text="错误：请输入非负整数", foreground="orange")
            return

        self.base_space, self.space_jitter, self.base_press, self.press_jitter = cfg
        self.running = True

        if self.click_count > 0:
            self.append_separator()

        self.clear_btn.config(state=tk.DISABLED)
        self.export_btn.config(state=tk.DISABLED)

        self.status_label.config(
            text=f"运行中｜间隔:{int(self.base_space * 1000)}±{int(self.space_jitter * 1000)}ms 时长:{int(self.base_press * 1000)}±{int(self.press_jitter * 1000)}ms",
            foreground="green"
        )
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)

        self.click_thread = threading.Thread(target=self.click_loop, daemon=True)
        self.click_thread.start()

    def stop_click(self):
        if not self.running:
            return

        self.running = False

        self.clear_btn.config(state=tk.NORMAL)
        self.export_btn.config(state=tk.NORMAL)

        self.status_label.config(text="状态：已停止", foreground="red")
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)

    def click_loop(self):
        gc.disable()
        try:
            while self.running:
                actual_press = self.base_press + random.uniform(-self.press_jitter, self.press_jitter)
                actual_press = max(0.001, actual_press)

                actual_space = self.base_space + random.uniform(-self.space_jitter, self.space_jitter)
                actual_space = max(0.001, actual_space)

                if not self.running:
                    break

                pydirectinput.mouseDown(button='left', _pause=False)
                time.sleep(actual_press)
                pydirectinput.mouseUp(button='left', _pause=False)

                if not self.running:
                    break

                self.click_count += 1
                self.append_log(
                    self.click_count,
                    int(actual_space * 1000),
                    int(actual_press * 1000)
                )

                self.precise_sleep(actual_space)
        finally:
            gc.enable()

    def precise_sleep(self, t):
        start = time.perf_counter()
        while time.perf_counter() - start < t:
            if not self.running:
                break
            time.sleep(0.001)

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