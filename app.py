import os
import json
import subprocess
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.ttk import Progressbar, Label, Frame, Style
from threading import Thread

try:
    import yt_dlp
except ImportError:
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'yt-dlp'])

# Function to save the destination folder in the config.json file
def save_config(destination_folder):
    with open('config.json', 'w') as config_file:
        json.dump({'destination_folder': destination_folder}, config_file)

# Function to load the destination folder from the config.json file
def load_config():
    if os.path.exists('config.json'):
        with open('config.json', 'r') as config_file:
            config = json.load(config_file)
            return config.get('destination_folder', '')
    return ''

# Function to update the progress bar
def update_progress(percent, progress_var, progress_bar):
    progress_var.set(percent)
    progress_bar.update()

# Function to download the audio
def download_audio(url, destination_folder, progress_var, progress_bar, status_label):
    # Get the path to the directory where the executable is located
    if getattr(sys, 'frozen', False):
        # If the app is running as a bundled executable
        bundle_dir = sys._MEIPASS
    else:
        # If running in a normal Python environment
        bundle_dir = os.path.dirname(os.path.abspath(__file__))

    # Define the paths to ffmpeg and ffprobe
    ffmpeg_path = os.path.join(bundle_dir, 'ffmpeg', 'ffmpeg.exe')
    ffprobe_path = os.path.join(bundle_dir, 'ffmpeg', 'ffprobe.exe')

    # Debug: Print the ffmpeg and ffprobe paths
    print(f"ffmpeg_path: {ffmpeg_path}")
    print(f"ffprobe_path: {ffprobe_path}")
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(destination_folder, '%(title)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '192',
        }],
        'ffmpeg_location': ffmpeg_path,  # Set path to ffmpeg and ffprobe
        'progress_hooks': [lambda d: progress_hook(d, progress_var, progress_bar, status_label)]
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        messagebox.showinfo("Download Complete", "The audio has been successfully downloaded.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

# Hook function for the progress bar
def progress_hook(d, progress_var, progress_bar, status_label):
    if d['status'] == 'downloading':
        total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
        downloaded_bytes = d.get('downloaded_bytes', 0)
        percent = int(downloaded_bytes / total_bytes * 100) if total_bytes > 0 else 0
        speed = d.get('speed', 0) or 0
        size_in_mib = total_bytes / 1024 / 1024 if total_bytes > 0 else 0
        speed_in_kib = speed / 1024 if speed > 0 else 0
        update_progress(percent, progress_var, progress_bar)
        status_label.config(text=f"Downloading: {percent}% - Speed: {speed_in_kib:.2f} KiB/s - Size: {size_in_mib:.2f} MiB")
    elif d['status'] == 'finished':
        update_progress(100, progress_var, progress_bar)
        status_label.config(text="Conversion to WAV completed")

# Function to start the download in a separate thread
def start_download():
    url = url_entry.get()
    if not url:
        messagebox.showwarning("Warning", "Please enter the video link.")
        return

    destination_folder = destination_folder_var.get()
    if not destination_folder:
        messagebox.showwarning("Warning", "Please choose the destination folder.")
        return

    save_config(destination_folder)

    download_thread = Thread(target=download_audio, args=(url, destination_folder, progress_var, progress_bar, status_label))
    download_thread.start()

# Function to select the destination folder
def select_destination_folder():
    folder = filedialog.askdirectory()
    if folder:
        destination_folder_var.set(folder)

# Function to toggle dark mode and white mode
def toggle_mode():
    global dark_mode
    dark_mode = not dark_mode
    update_mode()

def update_mode():
    if dark_mode:
        root.tk_setPalette(background='#333', foreground='#FFF')
        style.configure('TFrame', background='#333')
        style.configure('TLabel', background='#333', foreground='#FFF')
        style.configure('TProgressbar', troughcolor='#555', background='#888', thickness=20)  # Progressbar colors
        destination_entry.configure(bg='#555', fg='#FFF', insertbackground='white')
        url_entry.configure(bg='#555', fg='#FFF', insertbackground='white')
        mode_button.configure(bg='#555', fg='#FFF')
        select_button.configure(bg='#555', fg='#FFF')
        download_button.configure(bg='#555', fg='#FFF')
        mode_button.configure(text="Light Mode")
    else:
        root.tk_setPalette(background='#FFF', foreground='#000')
        style.configure('TFrame', background='#FFF')
        style.configure('TLabel', background='#FFF', foreground='#000')
        style.configure('TProgressbar', troughcolor='#DDD', background='#0078d4', thickness=20)  # Progressbar colors
        destination_entry.configure(bg='#FFF', fg='#000', insertbackground='black')
        url_entry.configure(bg='#FFF', fg='#000', insertbackground='black')
        mode_button.configure(bg='#F0F0F0', fg='#000')
        select_button.configure(bg='#F0F0F0', fg='#000')
        download_button.configure(bg='#F0F0F0', fg='#000')
        mode_button.configure(text="Dark Mode")

# GUI
root = tk.Tk()
root.title("YouTube Audio Downloader")
root.geometry("500x300")

dark_mode = False  # Start with light mode

# Set up style
style = Style()
style.configure('TFrame', background='#FFF')
style.configure('TLabel', background='#FFF', foreground='#000')
style.configure('TProgressbar', troughcolor='#DDD', background='#0078d4', thickness=20)  # Initial Progressbar style

frame = Frame(root, padding=10)
frame.pack(expand=True, fill='both')

# URL Entry
Label(frame, text="Video Link:").pack(pady=5, anchor='w')
url_entry = tk.Entry(frame, width=60)
url_entry.pack(pady=5, fill='x')

# Destination Folder
Label(frame, text="Destination Folder:").pack(pady=5, anchor='w')
destination_folder_var = tk.StringVar()
destination_folder_var.set(load_config())

destination_frame = Frame(frame)
destination_frame.pack(pady=5, fill='x')
destination_entry = tk.Entry(destination_frame, textvariable=destination_folder_var, width=50)
destination_entry.pack(side=tk.LEFT, padx=5, fill='x', expand=True)
select_button = tk.Button(destination_frame, text="Select", command=select_destination_folder)
select_button.pack(side=tk.RIGHT, padx=5)

# Progress Bar
Label(frame, text="Progress:").pack(pady=5, anchor='w')
progress_var = tk.IntVar()
progress_bar = Progressbar(frame, orient='horizontal', length=400, mode='determinate', maximum=100, variable=progress_var)
progress_bar.pack(pady=5)

# Status Label
status_label = Label(frame, text="Waiting...")
status_label.pack(pady=5)

# Mode Toggle Button
mode_button = tk.Button(root, command=toggle_mode, text="Dark Mode", width=15)
mode_button.place(relx=1.0, rely=0.0, anchor='ne', x=-10, y=10)  # Place in the top-right corner

# Download Button
download_button = tk.Button(frame, text="Download Audio", command=start_download)
download_button.pack(pady=20)

update_mode()  # Apply the initial mode

root.mainloop()
