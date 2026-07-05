import tkinter as tk
from tkinter import filedialog, messagebox
import json
import os
import shutil

# =========================
# 路径
# =========================
translations_path = ""
target_path = ""
entries = {}

# =========================
# 提示文本
# =========================
TIP_TEXT = "请选择【游戏根目录】下的 Translations 文件夹（版本14.2.7）"

# =========================
# 状态更新
# =========================
def set_status(text, mode="normal"):
    if mode == "error":
        top_tip.config(text=text, bg="red", fg="white")
    elif mode == "success":
        top_tip.config(text=text, bg="green", fg="white")
    else:
        top_tip.config(text=text, bg="#f0f0f0", fg="black")

# =========================
# JSON读取
# =========================
def load_rules():
    with open("rules.json", "r", encoding="utf-8") as f:
        return json.load(f)

rules = load_rules()

# =========================
# 选择目录
# =========================
def select_folder():
    global translations_path, target_path

    messagebox.showinfo("提示", TIP_TEXT)

    translations_path = filedialog.askdirectory()

    if not translations_path:
        return

    zh_path = os.path.join(translations_path, "zh_Hans")
    zh_self_path = os.path.join(translations_path, "zh_self")

    if not os.path.exists(zh_path):
        set_status("文件夹选择错误，请确认选择游戏根目录下的 Translations 文件夹", "error")
        return

    if not os.path.exists(zh_self_path):
        shutil.copytree(zh_path, zh_self_path)

    target_path = zh_self_path
    set_status("✔ 文件夹正确，可以开始修改", "normal")

# =========================
# 文件读写
# =========================
def read_lines(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.readlines()
    except:
        return []

def write_lines(path, lines):
    with open(path, "w", encoding="utf-8") as f:
        f.writelines(lines)

# =========================
# 修改逻辑
# =========================
def apply_rule(rule, value):
    if not value.strip():
        return

    file_path = os.path.join(target_path, rule["file"])

    if not os.path.exists(file_path):
        set_status(f"❌ 未找到文件: {rule['file']}", "error")
        return

    lines = read_lines(file_path)

    idx = rule["line"] - 1
    if idx < 0 or idx >= len(lines):
        return

    line = lines[idx].rstrip("\n")

    if rule["type"] == "line":
        lines[idx] = value + "\n"

    elif rule["type"] == "part":
        parts = line.split("~")
        if len(parts) >= 2:
            parts[1] = value
            lines[idx] = "~".join(parts) + "\n"

    write_lines(file_path, lines)

# =========================
# 执行修改
# =========================
def run():
    if not target_path:
        set_status("❗ 请先选择 Translations 文件夹", "error")
        return

    for r in rules["class_rules"]:
        apply_rule(r, entries[r["label"]].get())

    for r in rules["item_rules"]:
        apply_rule(r, entries[r["label"]].get())

    set_status("✔ 修改完成，重启游戏以应用修改", "success")

# =========================
# UI
# =========================
root = tk.Tk()
root.title("SCP文本修改工具（顶部提示版）")
root.geometry("700x800")

# =========================
# 🔥 顶部提示栏（重点）
# =========================
top_tip = tk.Label(
    root,
    text=TIP_TEXT,
    bg="#f0f0f0",
    fg="black",
    font=("Arial", 11, "bold"),
    padx=10,
    pady=8
)
top_tip.pack(fill="x")

# =========================
# 按钮区域
# =========================
btn_frame = tk.Frame(root)
btn_frame.pack(pady=10)

tk.Button(btn_frame, text="选择 Translations 文件夹", command=select_folder).pack(side="left", padx=5)
tk.Button(btn_frame, text="开始修改", command=run).pack(side="left", padx=5)

# =========================
# 滚动区域
# =========================
canvas = tk.Canvas(root)
scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)

frame = tk.Frame(canvas)

frame.bind(
    "<Configure>",
    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)

canvas.create_window((0, 0), window=frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# =========================
# UI生成
# =========================
tk.Label(frame, text="=== Class Names ===").pack(anchor="w")

for r in rules["class_rules"]:
    tk.Label(frame, text=r["label"]).pack(anchor="w")
    e = tk.Entry(frame, width=60)
    e.pack(pady=2)
    entries[r["label"]] = e

tk.Label(frame, text="=== Items ===").pack(anchor="w")

for r in rules["item_rules"]:
    tk.Label(frame, text=r["label"]).pack(anchor="w")
    e = tk.Entry(frame, width=60)
    e.pack(pady=2)
    entries[r["label"]] = e

root.mainloop()