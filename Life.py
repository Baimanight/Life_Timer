import tkinter as tk
from PIL import Image, ImageTk
import os, random, time, sys, re, json
from datetime import datetime

# ================= 配置区域 =================
# 建议确认此路径在 Ubuntu 下真实存在
IMAGE_DIR = os.path.expanduser("~/PICTURES/截图/Photo")  
HISTORY_FILE = os.path.expanduser("~/.Life_history.json")
MAX_WIDTH, MAX_HEIGHT = 1600, 900
FONT_SIZE = 32
# ===========================================

def parse_time(time_str):
    """解析时间字符串，如 25m, 1h, 10s"""
    units = {'s': 1, 'm': 60, 'h': 3600}
    match = re.match(r"(\d+)([smh])", time_str.lower())
    if not match: return None
    return int(match.group(1)) * units[match.group(2)]

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r') as f:
                return json.load(f)
        except: return {}
    return {}

def save_history(history):
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f)

def display_stats_grid(history):
    """以整齐的网格输出最近的统计数据"""
    print("\n\033[96m" + "┌" + "─"*15 + "┬" + "─"*12 + "┬" + "─"*15 + "┐")
    print(f"│ {'Date':^13} │ {'Count':^10} │ {'Total Time':^13} │")
    print("├" + "─"*15 + "┼" + "─"*12 + "┼" + "─"*15 + "┤")
    # 取最近5天
    dates = sorted(history.keys())[-5:]
    for d in dates:
        c = history[d]['count']
        t = history[d]['total_seconds'] // 60
        print(f"│ {d:^13} │ {c:^10} │ {t:>4} mins     │")
    print("└" + "─"*15 + "┴" + "─"*12 + "┴" + "─"*15 + "┘\033[0m\n")

def update_stats(seconds):
    history = load_history()
    today = datetime.now().strftime("%Y-%m-%d")
    is_first_run = today not in history
    
    if is_first_run:
        if history: display_stats_grid(history)
        history[today] = {"count": 0, "total_seconds": 0}
    
    history[today]["count"] += 1
    history[today]["total_seconds"] += seconds
    save_history(history)

def terminal_countdown(seconds):
    """在终端显示动态进度条"""
    start = seconds
    try:
        while seconds > 0:
            mins, secs = divmod(seconds, 60)
            percent = (start - seconds) / start
            bar = '█' * int(percent * 40) + '-' * (40 - int(percent * 40))
            # 增加颜色标识
            sys.stdout.write(f"\r\033[96m计时中: |{bar}| {mins:02d}:{secs:02d}\033[0m ")
            sys.stdout.flush()
            time.sleep(1)
            seconds -= 1
        print("\n\033[92m完成！弹出提醒界面...\033[0m")
    except KeyboardInterrupt:
        print("\n计时取消。")
        sys.exit()

def create_popup(text=" Congratulation! \nTake Your Life"):
    """Tkinter 弹窗，修复灰格问题"""
    root = tk.Tk()
    root.overrideredirect(True)
    root.attributes("-topmost", True)

    img_path = None
    if os.path.exists(IMAGE_DIR):
        valid = ('.png', '.jpg', '.jpeg')
        images = [f for f in os.listdir(IMAGE_DIR) if f.lower().endswith(valid)]
        if images:
            img_path = os.path.join(IMAGE_DIR, random.choice(images))

    if img_path:
        try:
            pil_img = Image.open(img_path)
            pil_img.thumbnail((MAX_WIDTH, MAX_HEIGHT), Image.Resampling.LANCZOS)
            tk_img = ImageTk.PhotoImage(pil_img)
            
            w, h = pil_img.size
            x = (root.winfo_screenwidth() // 2) - (w // 2)
            y = (root.winfo_screenheight() // 2) - (h // 2)
            root.geometry(f"{w}x{h}+{x}+{y}")

            canvas = tk.Canvas(root, width=w, height=h, highlightthickness=0, bg="black")
            canvas.pack()
            canvas.create_image(0, 0, image=tk_img, anchor="nw")
            
            # 文字（白色主体+黑色阴影）
            canvas.create_text(w/2+2, h/2+2, text=text, font=("Helvetica", FONT_SIZE, "bold"), fill="black", justify="center")
            canvas.create_text(w/2, h/2, text=text, font=("Helvetica", FONT_SIZE, "bold"), fill="white", justify="center")
            
            root.image = tk_img # 重要：防止垃圾回收导致灰块
            canvas.bind("<Button-1>", lambda e: root.destroy())
        except Exception as e:
            tk.Label(root, text=f"Error: {e}").pack()
    else:
        # 兜底显示
        root.geometry("500x300")
        tk.Label(root, text=text, font=("Arial", FONT_SIZE), bg="#2c3e50", fg="white").pack(fill="both", expand=True)
        root.bind("<Button-1>", lambda e: root.destroy())

    root.mainloop()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: Life 25m")
        sys.exit()

    total_seconds = parse_time(sys.argv[1])
    if total_seconds:
        # 1. 统计与显示网格
        update_stats(total_seconds)
        # 2. 终端计时
        terminal_countdown(total_seconds)
        # 3. 弹窗
        create_popup()
