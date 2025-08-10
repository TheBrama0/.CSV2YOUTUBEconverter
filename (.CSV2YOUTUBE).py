# MIT License
# Copyright (c) 2025 Brahamanandam Naik.
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction...


import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import requests
import urllib.parse
import re
import os
import time
import threading
import json
import random
from dotenv import load_dotenv
from supabase import create_client
from datetime import datetime
import tkinter.font as tkFont

# Load environment variables
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Config file for storing username locally
CONFIG_FILE = "user_config.json"

def load_username():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)
                username = data.get("username", "").strip()
                if username:
                    print(f"👤 Loaded username: {username}")
                    return username
        except Exception as e:
            print("⚠️ Failed to load username config:", e)
    return None

def save_username(username):
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump({"username": username.strip()}, f)
            print(f"💾 Username saved locally: {username}")
    except Exception as e:
        print("⚠️ Failed to save username config:", e)

def get_or_request_username(root):
    username = load_username()
    if not username:
        import tkinter.simpledialog as simpledialog
        root.withdraw()  # hide main window while prompting
        username = simpledialog.askstring("Username Required", "Please enter your username:")
        root.deiconify()
        if username and username.strip():
            save_username(username.strip())
        else:
            messagebox.showerror("Username Required", "Username is required to continue.")
            root.destroy()
            exit()
    return username

# Global flags and references
is_paused = False
stop_requested = False
current_links = []
fetch_limit = 20  # Default limit

# GUI element references
entry_file = None
entry_delay = None
entry_limit = None
btn_start = None
btn_pause = None
btn_stop = None
progress_bar = None
progress_label = None

def get_first_youtube_result(song, artist):
    query = f"{song} {artist}".strip()
    search_url = "https://www.youtube.com/results?search_query=" + urllib.parse.quote(query)
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(search_url, headers=headers)
        html = response.text
        video_ids = re.findall(r'"videoId":"(.*?)"', html)
        if video_ids:
            return f"https://www.youtube.com/watch?v={video_ids[0]}"
    except Exception as e:
        print(f"⚠️ Error searching '{query}': {e}")
    return ""

def save_partial_csv(df, file_path):
    output_file = os.path.splitext(file_path)[0] + '_with_links.csv'
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"💾 Progress saved to: {output_file}")

def update_progress(processed, total):
    global progress_bar, progress_label
    percent = (processed / total) * 100 if total else 0
    progress_bar["value"] = percent
    progress_label.config(text=f"Progress: {processed}/{total} ({percent:.1f}%)")

def browse_file():
    global entry_file
    filepath = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if filepath:
        entry_file.delete(0, tk.END)
        entry_file.insert(0, filepath)

def check_supabase(song, artist):
    try:
        response = supabase.table("fetched_links") \
            .select("youtube_link") \
            .eq("song", song) \
            .eq("artist", artist) \
            .limit(1) \
            .execute()
        if response.data:
            return response.data[0]["youtube_link"]
        return None
    except Exception as e:
        print("🔍 Supabase lookup failed:", e)
        return None

def insert_to_supabase(song, artist, link, username):
    try:
        data = {
            "song": song,
            "artist": artist,
            "youtube_link": link,
            "username": username,
            "fetched_at": datetime.utcnow().isoformat()
        }
        supabase.table("fetched_links").insert(data).execute()
        print(f"✅ Inserted into Supabase: {song} - {link} by {username}")
    except Exception as e:
        print("⚠️ Supabase insert failed:", e)

def update_fetch_limit():
    """Update the fetch limit based on user input."""
    global fetch_limit
    try:
        new_limit = int(entry_fetch_limit.get())
        if new_limit > 0:
            fetch_limit = new_limit
            messagebox.showinfo("✅ Success", f"Fetch limit updated to {fetch_limit}")
        else:
            messagebox.showwarning("Invalid Input", "Fetch limit must be a positive number.")
    except ValueError:
        messagebox.showwarning("Invalid Input", "Please enter a valid number.")

def process_csv(file_path, delay_seconds, max_links, username):
    global is_paused, stop_requested, current_links, progress_bar, progress_label, fetch_limit
    try:
        df = pd.read_csv(file_path)
        if 'YouTube Link' not in df.columns:
            df['YouTube Link'] = ''

        links = df['YouTube Link'].tolist()
        current_links = links
        total_rows = len(df)
        fetched_count = 0
        processed_count = 0
        youtube_requests = 0  # counter for YouTube scrapes

        for idx, row in df.iterrows():
            if stop_requested:
                print("🛑 Stop requested. Ending loop.")
                break

            if max_links > 0 and fetched_count >= max_links:
                print(f"✅ Reached max fetch limit: {max_links}")
                break

            if isinstance(links[idx], str) and links[idx].startswith("http"):
                print(f"⏭ Skipping row {idx+1}, already has link")
                processed_count += 1
                update_progress(processed_count, total_rows)
                continue

            while is_paused and not stop_requested:
                print("⏸ Paused... waiting")
                time.sleep(0.5)

            song = str(row.get('Track Name', '')).strip()
            artist = str(row.get('Artist Name(s)', '')).strip()
            if not song or song.lower() == 'nan' or not artist or artist.lower() == 'nan':
                print(f"⚠️ Skipping row {idx+1} (missing song/artist)")
                links[idx] = ""
                processed_count += 1
                update_progress(processed_count, total_rows)
                continue

            print(f"🔍 Searching: {song} by {artist}")

            cached_link = check_supabase(song, artist)
            if cached_link:
                print(f"↪️ Found in Supabase: {cached_link}")
                link = cached_link
            else:
                link = get_first_youtube_result(song, artist)
                youtube_requests += 1  # only count YouTube hits
                insert_to_supabase(song, artist, link, username)

                # Every `fetch_limit` YT requests, add random delay
                if youtube_requests % fetch_limit == 0:
                    extra_delay = random.randint(30, 120)
                    message = f"⏳ Hit {youtube_requests} YouTube requests, sleeping {extra_delay} seconds for safety..."
                    print(message)
                    progress_label.config(text=message)  # Update GUI
                    root.update_idletasks()  # Ensure GUI updates immediately
                    time.sleep(extra_delay)

            print(f"→ Final Link: {link}")
            links[idx] = link
            fetched_count += 1
            processed_count += 1

            update_progress(processed_count, total_rows)
            time.sleep(delay_seconds)

        df['YouTube Link'] = links
        save_partial_csv(df, file_path)

        if not stop_requested:
            messagebox.showinfo("✅ Done!", f"Fetched {fetched_count} links and saved file.")
        else:
            messagebox.showinfo("🛑 Stopped", f"Stopped early. Fetched {fetched_count} links.")

    except Exception as e:
        messagebox.showerror("❌ Error", f"Something went wrong:\n{e}")
    finally:
        btn_start.config(state=tk.NORMAL)
        btn_pause.config(state=tk.DISABLED, text="Pause")
        btn_stop.config(state=tk.DISABLED)
        progress_bar["value"] = 0
        progress_label.config(text="Progress: 0/0 (0%)")

def start_processing():
    global is_paused, stop_requested
    stop_requested = False
    is_paused = False

    file_path = entry_file.get().strip()
    try:
        delay_seconds = float(entry_delay.get())
    except ValueError:
        messagebox.showwarning("Invalid Delay", "Enter a valid delay like 1.5")
        return

    try:
        max_links = int(entry_limit.get())
        if max_links < 0:
            raise ValueError
    except ValueError:
        messagebox.showwarning("Invalid Limit", "Enter 0 or a positive number for max links")
        return

    if file_path:
        btn_start.config(state=tk.DISABLED)
        btn_pause.config(state=tk.NORMAL)
        btn_stop.config(state=tk.NORMAL)
        threading.Thread(target=process_csv, args=(file_path, delay_seconds, max_links, username), daemon=True).start()
    else:
        messagebox.showwarning("No File", "Please select a CSV file first.")

def toggle_pause():
    global is_paused
    is_paused = not is_paused
    btn_pause.config(text="Resume" if is_paused else "Pause")

def stop_and_save():
    global stop_requested
    stop_requested = True
    btn_pause.config(state=tk.DISABLED)
    btn_stop.config(state=tk.DISABLED)
    print("⏹ Saving requested. Waiting for thread to finish...")

# --- GUI Setup ---
root = tk.Tk()
root.title("YouTube Link Finder")

# Get or request username on startup
username = get_or_request_username(root)
tk.Label(root, text=f"👤 Username: {username}").pack(pady=5)

tk.Label(root, text="🎵 Select your CSV file:").pack(pady=5)
frame = tk.Frame(root)
frame.pack(pady=5)

entry_file = tk.Entry(frame, width=50)
entry_file.pack(side=tk.LEFT, padx=5)

btn_browse = tk.Button(frame, text="Browse", command=browse_file)
btn_browse.pack(side=tk.LEFT)

tk.Label(root, text="⏱ Delay between searches(sec)(KEEP VALUE:>=3)):").pack(pady=5)
entry_delay = tk.Entry(root)
entry_delay.insert(0, "3")
entry_delay.pack()

tk.Label(root, text="🔢 Max number of links to fetch (0 = no limit):").pack(pady=5)
entry_limit = tk.Entry(root)
entry_limit.insert(0, "0")
entry_limit.pack()

# --- Progress Bar ---
progress_label = tk.Label(root, text="Progress: 0/0 (0%)")
progress_label.pack(pady=5)

progress_bar = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
progress_bar.pack(pady=5)

# --- Buttons ---
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

btn_start = tk.Button(button_frame, text="▶️ Start", command=start_processing)
btn_start.grid(row=0, column=0, padx=5)

btn_pause = tk.Button(button_frame, text="Pause", command=toggle_pause, state=tk.DISABLED)
btn_pause.grid(row=0, column=1, padx=5)

btn_stop = tk.Button(button_frame, text="⏹ Stop & Save", command=stop_and_save, state=tk.DISABLED)
btn_stop.grid(row=0, column=2, padx=5)

# Add GUI elements for fetch limit
tk.Label(root, text="🔢 Fetch limit before sleep:").pack(pady=5)
fetch_limit_frame = tk.Frame(root)
fetch_limit_frame.pack(pady=5)

entry_fetch_limit = tk.Entry(fetch_limit_frame, width=10)
entry_fetch_limit.insert(0, str(fetch_limit))  # Set default value
entry_fetch_limit.pack(side=tk.LEFT, padx=5)

btn_update_limit = tk.Button(fetch_limit_frame, text="Update Limit", command=update_fetch_limit)
btn_update_limit.pack(side=tk.LEFT, padx=5)

root.mainloop()