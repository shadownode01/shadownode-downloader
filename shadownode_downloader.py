#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time
import subprocess
import shutil
import random
import re
from pathlib import Path

# ── ডাইনামিক এবং র‍্যান্ডম থিম কালার সিলেকশন ───────────────────────────────────
COLOR_PALETTES = [
    {"primary": "\033[96m", "secondary": "\033[95m", "accent": "\033[93m"},  # Cyan, Magenta, Yellow
    {"primary": "\033[92m", "secondary": "\033[96m", "accent": "\033[97m"},  # Green, Cyan, White
    {"primary": "\033[94m", "secondary": "\033[93m", "accent": "\033[92m"},  # Blue, Yellow, Green
    {"primary": "\033[95m", "secondary": "\033[91m", "accent": "\033[96m"},  # Magenta, Red, Cyan
    {"primary": "\033[93m", "secondary": "\033[92m", "accent": "\033[95m"}   # Yellow, Green, Magenta
]

selected_theme = random.choice(COLOR_PALETTES)

R  = "\033[0m"
B  = "\033[1m"
DG = "\033[90m"
RE = "\033[91m"
GR = "\033[92m"
WH = "\033[97m"

# থিম কালার অ্যাসাইনমেন্ট
PR = selected_theme["primary"]
SC = selected_theme["secondary"]
AC = selected_theme["accent"]

# ── মোবাইলের জন্য অপ্টিমাইজড উইডথ ─────────────────────────────────────────────
TERM_WIDTH = 52

# ── ইন্টার্নাল স্টোরেজ পাথ সেটআপ (Termux / Android Friendly) ───────────────────
if os.path.exists("/sdcard"):
    DOWNLOAD_DIR = "/sdcard/Download"
else:
    DOWNLOAD_DIR = str(Path.home() / "Downloads")

os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# ─────────────────────────────────────────────────────────────────────────────
#  ইউটিলিটি হেল্পার্স ও অ্যানিমেশন ইফেক্টস
# ─────────────────────────────────────────────────────────────────────────────

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def animated_print(text, delay=0.005, end="\n"):
    """টেক্সটগুলোকে টাইপিং অ্যানিমেশনের মত স্মুথলি প্রিন্ট করবে।"""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    sys.stdout.write(end)

def box_line(text, border_color=PR, text_color=WH):
    inner = TERM_WIDTH - 4
    padded = text.center(inner)
    print(f"{border_color}{B}║{R}{text_color}{B}{padded}{R}{border_color}{B}║{R}")

# ─────────────────────────────────────────────────────────────────────────────
#  ব্যানার / হেডার (মোবাইল স্ক্রিন সাইজ)
# ─────────────────────────────────────────────────────────────────────────────

BANNER = f"""{PR}{B}
 ╔══════════════════════════════════════════════════╗
 ║  ██████╗ ██╗  ██╗ █████╗ ██████╗  ██████╗ ██╗    ║
 ║  ██╔══██╗██║  ██║██╔══██╗██╔══██╗██╔═══██╗██║    ║
 ║  ██████╔╝███████║███████║██║  ██║██║   ██║██║    ║
 ║  ██╔═══╝ ██╔══██║██╔══██║██║  ██║██║   ██║╚═╝    ║
 ║  ██║     ██║  ██║██║  ██║██████╔╝╚██████╔╝██╗    ║
 ║  ╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝  ╚═════╝ ╚═╝    ║
 ╚══════════════════════════════════════════════════╝{R}"""

def show_banner(animate=False):
    clear()
    if animate:
        animated_print(BANNER, delay=0.002)
    else:
        print(BANNER)
        
    bc = PR
    print(f"{bc}{B}╔{'═'*(TERM_WIDTH-2)}╗{R}")
    box_line("⚡ SHADOWNODE DOWNLOADER ⚡", bc, SC)
    box_line("", bc)
    box_line("👤 Owner  : ShadowNode", bc, AC)
    box_line("🔖 Version: v3.0 Ultra Premium", bc, GR)
    box_line("📂 Save To: Internal Storage/Download", bc, DG)
    print(f"{bc}{B}╚{'═'*(TERM_WIDTH-2)}╝{R}")
    print()

# ─────────────────────────────────────────────────────────────────────────────
#  মেইন মেনু
# ─────────────────────────────────────────────────────────────────────────────

def show_menu():
    bc = GR
    print(f"{bc}{B}╔{'═'*(TERM_WIDTH-2)}╗{R}")
    box_line("📋  M A I N   M E N U", bc, WH)
    print(f"{bc}{B}╠{'═'*(TERM_WIDTH-2)}╣{R}")
    box_line("", bc)
    box_line(f"  {AC}[1]{R}{WH}  🎬  High Quality (Single Video) ", bc, WH)
    box_line("", bc)
    box_line(f"  {AC}[2]{R}{WH}  📦  Batch Downloader (Multi)    ", bc, WH)
    box_line("", bc)
    box_line(f"  {AC}[3]{R}{WH}  ⚡  Fast Download (Low Quality) ", bc, WH)
    box_line("", bc)
    box_line(f"  {RE}[4]{R}{WH}  🚪  Clean & Exit               ", bc, WH)
    box_line("", bc)
    print(f"{bc}{B}╚{'═'*(TERM_WIDTH-2)}╝{R}")
    print()

# ─────────────────────────────────────────────────────────────────────────────
#  লাইভ রিয়েল-টাইম ব্যাটারি প্রোগ্রেস বার (0% - 100%)
# ─────────────────────────────────────────────────────────────────────────────

def draw_progress_bar(percent, label="Downloading"):
    """প্রকৃত পারসেন্টেজ অনুযায়ী ব্যাটারি স্টাইলের প্রোগ্রেস বার দেখাবে।"""
    width = 15
    filled = int(round(width * percent / 100))
    
    # প্রোগ্রেস অনুযায়ী কালার পরিবর্তন
    if percent < 35:
        bar_color = RE
    elif percent < 75:
        bar_color = AC
    else:
        bar_color = GR
        
    bar = f"[{bar_color}{B}{'█' * filled}{DG}{'░' * (width - filled)}{R}] {bar_color}{B}{percent:3d}%{R}"
    tip = f"{AC}{B}┤{R}"
    sys.stdout.write(f"\r  {WH}{B}{label}... {R}🔋 {tip}{bar} ")
    sys.stdout.flush()

# ─────────────────────────────────────────────────────────────────────────────
#  কোর ডাউনলোড ইঞ্জিন (yt-dlp স্ট্রীম হ্যান্ডলার)
# ─────────────────────────────────────────────────────────────────────────────

def run_download(url, quality="high", label="Downloading"):
    """yt-dlp রান করে এবং রিয়েল টাইমে আউটপুট রিড করে পারসেন্টেজ বের করে।"""
    output_template = os.path.join(DOWNLOAD_DIR, "%(title).50s.%(ext)s")

    if quality == "high":
        fmt = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"
    else:
        fmt = "worstvideo+worstaudio/worst"

    cmd = [
        "yt-dlp",
        "--format", fmt,
        "--merge-output-format", "mp4",
        "--output", output_template,
        "--no-playlist",
        "--newline",
        url,
    ]

    try:
        # ডাউনলোড শুরুর পূর্বে ০% বার শো করা
        draw_progress_bar(0, label)
        
        process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1
        )
        
        # yt-dlp এর আউটপুট লাইভ ট্র্যাকিং করা
        percent_pattern = re.compile(r"\[download\]\s+(\d+\.\d+)%")
        
        while True:
            line = process.stdout.readline()
            if not line and process.poll() is not None:
                break
            
            match = percent_pattern.search(line)
            if match:
                current_percent = int(float(match.group(1)))
                draw_progress_bar(current_percent, label)
                
        process.wait()
        
        if process.returncode == 0:
            draw_progress_bar(100, label)
            print() # নিউ লাইনের জন্য
            return True, None
        else:
            stderr_output = process.stderr.read()
            err = stderr_output.strip().split("\n")[-1] if stderr_output.strip() else "Error in downloading"
            print()
            return False, err
            
    except Exception as e:
        print()
        return False, str(e)

# ─────────────────────────────────────────────────────────────────────────────
#  সাকসেস এবং এরর মেসেজ বক্স
# ─────────────────────────────────────────────────────────────────────────────

def show_success(count=1):
    print(f"\n  {GR}{B}╔══════════════════════════════════════════╗{R}")
    if count == 1:
        print(f"  {GR}{B}║  ✅  Download Complete!                  ║{R}")
    else:
        print(f"  {GR}{B}║  ✅  All {count} Downloads Complete!           ║{R}")
    print(f"  {GR}{B}║  📁  Saved to Internal Storage/Download  ║{R}")
    print(f"  {GR}{B}╚══════════════════════════════════════════╝{R}")
    animated_print(f"\n  {DG}Returning to main menu in 3 seconds...{R}", delay=0.01)
    time.sleep(3)

def show_error(msg):
    print(f"\n  {RE}{B}╔══════════════════════════════════════════╗{R}")
    print(f"  {RE}{B}║  ✗  Download Failed!                     ║{R}")
    print(f"  {RE}{B}╚══════════════════════════════════════════╝{R}")
    print(f"  {RE}Error: {msg[:45]}...{R}" if len(msg) > 45 else f"  {RE}Error: {msg}{R}")
    animated_print(f"\n  {DG}Returning to main menu in 3 seconds...{R}", delay=0.01)
    time.sleep(3)

# ─────────────────────────────────────────────────────────────────────────────
#  ফিচার সমূহ
# ─────────────────────────────────────────────────────────────────────────────

def feature_single():
    show_banner()
    print(f"  {PR}{B}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{R}")
    print(f"  {SC}{B}  🎬  HIGH QUALITY SINGLE DOWNLOADER{R}")
    print(f"  {PR}{B}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{R}\n")
    print(f"  {WH}Paste your video URL and press Enter:{R}\n")

    try:
        url = input(f"  {AC}{B}🔗 URL ➤ {R}").strip()
    except (KeyboardInterrupt, EOFError):
        return

    if not url:
        print(f"\n  {RE}No URL entered.{R}")
        time.sleep(1.5)
        return

    print()
    ok, err = run_download(url, quality="high", label="HQ Fetching")

    if ok:
        show_success(1)
    else:
        show_error(err)

def feature_multi():
    show_banner()
    print(f"  {PR}{B}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{R}")
    print(f"  {SC}{B}  📦  BATCH DOWNLOADER (MULTI){R}")
    print(f"  {PR}{B}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{R}\n")

    try:
        count_str = input(f"  {AC}{B}📊 How many videos to download? ➤ {R}").strip()
        count = int(count_str)
        if count < 1:
            raise ValueError
    except (ValueError, KeyboardInterrupt, EOFError):
        print(f"\n  {RE}Invalid input.{R}")
        time.sleep(1.5)
        return

    urls = []
    print(f"\n  {WH}Enter {count} URLs one by one:{R}\n")
    for i in range(1, count + 1):
        try:
            url = input(f"  {AC}{B}🔗 URL {i}/{count} ➤ {R}").strip()
        except (KeyboardInterrupt, EOFError):
            return
        if url:
            urls.append(url)
        else:
            print(f"  {RE}Skipped (empty URL).{R}")

    if not urls:
        print(f"\n  {RE}No URLs provided.{R}")
        time.sleep(1.5)
        return

    print()
    success_count = 0
    for idx, url in enumerate(urls, 1):
        display_url = url[:35] + "..." if len(url) > 35 else url
        print(f"\n  {PR}{B}[{idx}/{len(urls)}]{R} {WH}{display_url}{R}")
        
        ok, err = run_download(url, quality="high", label=f"Batch [{idx}/{len(urls)}]")

        if ok:
            success_count += 1
        else:
            print(f"  {RE}  ✗ Failed: {err}{R}")

    show_success(success_count)

def feature_fast():
    show_banner()
    print(f"  {PR}{B}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{R}")
    print(f"  {SC}{B}  ⚡  FAST DOWNLOADER (LOW QUALITY){R}")
    print(f"  {PR}{B}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{R}\n")
    print(f"  {WH}Paste your video URL (Fast Mode):{R}\n")

    try:
        url = input(f"  {AC}{B}🔗 URL ➤ {R}").strip()
    except (KeyboardInterrupt, EOFError):
        return

    if not url:
        print(f"\n  {RE}No URL entered.{R}")
        time.sleep(1.5)
        return

    print()
    ok, err = run_download(url, quality="low", label="Fast Fetching")

    if ok:
        show_success(1)
    else:
        show_error(err)

def feature_exit():
    clear() 
    sys.exit(0)

# ─────────────────────────────────────────────────────────────────────────────
#  এনভায়রনমেন্ট চেক ও মেইন লুপ
# ─────────────────────────────────────────────────────────────────────────────

def check_ytdlp():
    if shutil.which("yt-dlp"):
        return True
    print(f"\n  {RE}{B}[✗] yt-dlp not found!{R}")
    print(f"  {AC}Install it using:{R} pip install yt-dlp\n")
    return False

def main():
    # গ্লোবাল ভেরিয়েবলগুলো ফাংশনের শুরুতেই ডিক্লেয়ার করা হলো
    global selected_theme, PR, SC, AC
    
    if not check_ytdlp():
        input(f"\n  {AC}Press Enter to exit...{R}")
        sys.exit(1)

    show_banner(animate=True)
    
    while True:
        show_menu()

        try:
            choice = input(f"  {AC}{B}➤ Select Option [1-4]: {R}").strip()
        except (KeyboardInterrupt, EOFError):
            feature_exit()

        if choice == "1":
            feature_single()
        elif choice == "2":
            feature_multi()
        elif choice == "3":
            feature_fast()
        elif choice == "4":
            feature_exit()
        else:
            print(f"\n  {RE}{B}[!] Invalid option. Please choose 1-4.{R}")
            time.sleep(1.2)
            
        # প্রতিবার নতুন করে লুপ ঘোরার সময় র‍্যান্ডম কালার স্কিম সেটআপ
        selected_theme = random.choice(COLOR_PALETTES)
        PR = selected_theme["primary"]
        SC = selected_theme["secondary"]
        AC = selected_theme["accent"]
        show_banner(animate=False)

if __name__ == "__main__":
    main()
