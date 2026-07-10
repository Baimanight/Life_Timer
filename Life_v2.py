import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageTk
import os, random, time, sys, re, json
from datetime import datetime

# ================= Setup =================
IMAGE_DIRS = [
    os.path.expanduser("~/PICTURES/截图/Photo"),
    os.path.expanduser("~/PICTURES/截图/Atmospheric"),
]

HISTORY_FILE = os.path.expanduser("~/.Life_history.json")
FONT_SIZE = 32

LAST_SHOWN_IMAGE = None

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")
# ===========================================

# ===========================================
# 1. History Module
# ===========================================
def upgrade_history(history):
    if "version" in history and history["version"] == 2:
        return history
    new_history = {"version": 2, "daily": {}, "sessions": []}
    for key, value in history.items():
        if isinstance(value, dict) and "count" in value:
            new_history["daily"][key] = value
    return new_history

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r') as f:
                return upgrade_history(json.load(f))
        except: 
            return {"version": 2, "daily": {}, "sessions": []}
    return {"version": 2, "daily": {}, "sessions": []}

def save_history(history):
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=4)

def update_stats(seconds):
    history = load_history()
    today = datetime.now().strftime("%Y-%m-%d")
    now_iso = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    
    if today not in history["daily"]:
        history["daily"][today] = {"count": 0, "total_seconds": 0}
    
    history["daily"][today]["count"] += 1
    history["daily"][today]["total_seconds"] += seconds
    
    history["sessions"].append({"time": now_iso, "seconds": seconds})
    save_history(history)

def format_human_time(total_minutes):
    if total_minutes <= 0:
        return "0m"
        
    MIN_IN_HOUR = 60
    MIN_IN_DAY = 60 * 24
    MIN_IN_MONTH = 60 * 24 * 30
    MIN_IN_YEAR = 60 * 24 * 365
    
    rem = total_minutes
    years, rem = divmod(rem, MIN_IN_YEAR)
    months, rem = divmod(rem, MIN_IN_MONTH)
    days, rem = divmod(rem, MIN_IN_DAY)
    hours, mins = divmod(rem, MIN_IN_HOUR)
    
    parts = []
    if years > 0: parts.append(f"{years}y")
    if months > 0: parts.append(f"{months}m")
    if days > 0: parts.append(f"{days}d")
    if hours > 0: parts.append(f"{hours}h")
    if mins > 0 or not parts: parts.append(f"{mins}m")
    
    return " ".join(parts[:2])

def get_summary():
    history = load_history()
    today = datetime.now().strftime("%Y-%m-%d")
    
    today_count = history["daily"].get(today, {}).get("count", 0)
    today_mins = history["daily"].get(today, {}).get("total_seconds", 0) // 60
    
    total_count = sum(day["count"] for day in history["daily"].values())
    total_mins = sum(day["total_seconds"] for day in history["daily"].values()) // 60
    
    today_time_str = format_human_time(today_mins)
    total_time_str = format_human_time(total_mins)
    
    return today_count, today_time_str, total_count, total_time_str


# ===========================================
# 2. Timer Module
# ===========================================
def parse_time(time_str):
    time_str = str(time_str).strip().lower()
    if not time_str:
        return None
    if re.match(r"^\d+$", time_str):
        return int(time_str) * 60
        
    pattern = re.compile(r'(?P<val>\d+(?:\.\d+)?)(?P<unit>[smh])')
    matches = pattern.findall(time_str)
    if not matches:
        return None
        
    units = {'s': 1, 'm': 60, 'h': 3600}
    total_seconds = 0.0
    for val, unit in matches:
        total_seconds += float(val) * units[unit]
    return int(total_seconds)

def terminal_countdown(seconds):
    start = seconds
    try:
        while seconds > 0:
            mins, secs = divmod(seconds, 60)
            percent = (start - seconds) / start
            bar = '█' * int(percent * 40) + '-' * (40 - int(percent * 40))
            sys.stdout.write(f"\r\033[96mTiming: |{bar}| {mins:02d}:{secs:02d}\033[0m ")
            sys.stdout.flush()
            time.sleep(1)
            seconds -= 1
        print("\n\033[92m Congratulation! \033[0m")
    except KeyboardInterrupt:
        print("\nStop")
        sys.exit()


# ===========================================
# 3. 阶段一：全屏休息大图弹窗 (彻底剥离)
# ===========================================
class LifePhotoPopup(tk.Tk):
    def __init__(self, text_overlay=" Congratulation! \nTake Your Life"):
        super().__init__()
        self.text_overlay = text_overlay
        
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        
        global LAST_SHOWN_IMAGE
        all_images = []
        valid_exts = ('.png', '.jpg', '.jpeg', '.bmp', '.gif')
        for directory in IMAGE_DIRS:
            if os.path.exists(directory):
                files = [os.path.join(directory, f) for f in os.listdir(directory) if f.lower().endswith(valid_exts)]
                all_images.extend(files)

        if len(all_images) > 1 and LAST_SHOWN_IMAGE in all_images:
            choices = [img for img in all_images if img != LAST_SHOWN_IMAGE]
            img_path = random.choice(choices)
        else:
            img_path = random.choice(all_images) if all_images else None

        if img_path:
            LAST_SHOWN_IMAGE = img_path
            try:
                pil_img = Image.open(img_path)
                orig_w, orig_h = pil_img.size
                scale_factor = min(screen_w / orig_w, screen_h / orig_h)
                new_w, new_h = int(orig_w * scale_factor), int(orig_h * scale_factor)
                pil_img = pil_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
                self.tk_img = ImageTk.PhotoImage(pil_img)
                
                self.geometry(f"{new_w}x{new_h}+{(screen_w-new_w)//2}+{(screen_h-new_h)//2}")
                canvas = tk.Canvas(self, width=new_w, height=new_h, highlightthickness=0, bg="black")
                canvas.pack(fill="both", expand=True)
                canvas.create_image(new_w//2, new_h//2, image=self.tk_img, anchor="center")
                
                canvas.create_text(new_w/2+2, new_h/2+2, text=self.text_overlay, font=("Helvetica", FONT_SIZE, "bold"), fill="black", justify="center")
                canvas.create_text(new_w/2, new_h/2, text=self.text_overlay, font=("Helvetica", FONT_SIZE, "bold"), fill="white", justify="center")
                
                canvas.bind("<Button-1>", lambda e: self.destroy())
                return
            except Exception as e:
                print(f"Image load error: {e}")
        
        # 如果没有图片或加载失败，一瞬间销毁以直接跨入下一阶段
        self.after(10, self.destroy)


# ===========================================
# 4. 阶段二：独立且固定 360x300 的配置窗口
# ===========================================
class NextReminderWindow(ctk.CTk):
    def __init__(self, last_input_str):
        super().__init__()
        self.result_seconds = None
        self.last_input_str = last_input_str
        
        # 天然保留系统原生精美外框装饰器，方便系统级聚焦与拖拽
        self.title("Next Reminder")
        self.attributes("-topmost", True)
        
        # 📐 强制应用独立固定的视窗大小
        window_width, window_height = 360, 270
        
        # 🗺️ 绝对居中算法
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        center_x = (screen_w - window_width) // 2
        center_y = (screen_h - window_height) // 2
        self.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")
        
        # 纯 ctk 深色模式布局流
        self.configure(fg_color="#1a1a1a")
        self.grid_columnconfigure(0, weight=1)
        
        # 1. 标题
        self.title_label = ctk.CTkLabel(self, text="Next Reminder", font=("Helvetica", 18, "bold"), text_color="#ffffff")
        self.title_label.grid(row=0, column=0, pady=(24, 12), sticky="ew")
        
        # 2. 文本输入框 (字号 17 粗体，高度 38，独立宽度完美适配)
        self.entry = ctk.CTkEntry(
            self, width=290, height=38, placeholder_text="e.g. 20m", 
            font=("Helvetica", 17, "bold"), fg_color="#262626", border_color="#3a3a3a", corner_radius=10
        )
        self.entry.insert(0, self.last_input_str)
        self.entry.grid(row=1, column=0, pady=10)
        
        # 3. 优化记录看板
        today_c, today_time_str, total_c, total_time_str = get_summary()
        stats_text = f"Today   {today_c:3d}  ·  {today_time_str}\nTotal   {total_c:3d}  ·  {total_time_str}"
        
        self.stats_label = ctk.CTkLabel(self, text=stats_text, font=("Helvetica", 15, "bold"), justify="left", text_color="#e0e0e0")
        self.stats_label.grid(row=2, column=0, pady=(12, 16), padx=45, sticky="w")
        
        # 4. 底部控制选项栏 Frame
        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.grid(row=3, column=0, pady=(0, 20), padx=38, sticky="e")
        
        # Cancel & Start 按钮字号 15 号粗体 (bold)
        self.cancel_btn = ctk.CTkButton(
            self.btn_frame, text="Cancel", width=86, height=32, 
            font=("Helvetica", 15, "bold"), fg_color="#333333", hover_color="#444444", text_color="#ffffff", command=self.on_cancel
        )
        self.cancel_btn.pack(side="left", padx=(0, 12))
        
        self.start_btn = ctk.CTkButton(
            self.btn_frame, text="Start", width=86, height=32, 
            font=("Helvetica", 15, "bold"), fg_color="#1f538d", hover_color="#2969b0", text_color="#ffffff", command=self.on_start
        )
        self.start_btn.pack(side="left")
        
        # 全局输入事件绑定与无缝强力聚焦流
        self.entry.bind("<KeyRelease>", self.validate_input)
        self.bind_all("<Return>", lambda e: self.shortcut_enter())
        self.bind_all("<Escape>", lambda e: self.on_cancel())
        
        self.bind("<Button-1>", lambda e: self.force_focus_entry(), add="+")
        self.bind("<FocusIn>", lambda e: self.force_focus_entry())
        
        # 盲打接管就绪
        self.force_focus_entry()
        self.validate_input()
        self.after(50, self.setup_grab)

    def setup_grab(self):
        try: self.grab_set()
        except: pass

    def force_focus_entry(self):
        self.entry.focus_force()
        self.entry.select_range(0, tk.END)
        self.entry.icursor(tk.END)

    def validate_input(self, event=None):
        val = self.entry.get().strip()
        parsed = parse_time(val)
        if parsed and parsed > 0:
            self.start_btn.configure(state="normal", fg_color="#1f538d")
        else:
            self.start_btn.configure(state="disabled", fg_color="#2b2b2b")

    def shortcut_enter(self):
        if self.start_btn.cget("state") == "normal":
            self.on_start()

    def on_start(self):
        val = self.entry.get().strip()
        parsed = parse_time(val)
        if parsed:
            self.result_seconds = parsed
            global CURRENT_INPUT_STR
            CURRENT_INPUT_STR = val
            try: self.grab_release()
            except: pass
            self.destroy()

    def on_cancel(self):
        self.result_seconds = None
        try: self.grab_release()
        except: pass
        self.destroy()


# ===========================================
# 5. 主事件环循环调度器
# ===========================================
def run_ui_cycle(last_input_str):
    # 第一步：干净利落地拉起全屏大图视窗，直到被用户点击后销毁
    photo_app = LifePhotoPopup()
    photo_app.mainloop()
    
    # 第二步：在大图已经完全释放后，以独立全新的 ctk 状态锁死建立 360x300 的配置视窗
    reminder_app = NextReminderWindow(last_input_str)
    reminder_app.mainloop()
    
    return reminder_app.result_seconds


# ===========================================
# 6. Main Loop
# ===========================================
CURRENT_INPUT_STR = "20m"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        initial_seconds = parse_time("20m")
    else:
        CURRENT_INPUT_STR = sys.argv[1]
        initial_seconds = parse_time(CURRENT_INPUT_STR)
        if not initial_seconds:
            print("\033[91mInvalid initial time format!\033[0m")
            sys.exit()

    current_seconds = initial_seconds

    while True:
        terminal_countdown(current_seconds)
        update_stats(current_seconds)
        current_seconds = run_ui_cycle(CURRENT_INPUT_STR)
        if current_seconds is None:
            print("\n\033[93mLife cycle terminated by user. Take care!\033[0m")
            break
