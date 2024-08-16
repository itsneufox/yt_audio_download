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

def save_config(destination_folder, language, dark_mode, audio_format):
    config = {
        'destination_folder': destination_folder,
        'language': language,
        'dark_mode': dark_mode,
        'format': audio_format
    }
    with open('config.json', 'w') as config_file:
        json.dump(config, config_file)

def load_config():
    if os.path.exists('config.json'):
        with open('config.json', 'r') as config_file:
            config = json.load(config_file)
            return config.get('destination_folder', ''), config.get('language', 'English'), config.get('dark_mode', False), config.get('format', 'wav')
    return '', 'English', False, 'wav'

def update_progress(percent, progress_var, progress_bar):
    progress_var.set(percent)
    progress_bar.update()

def download_audio(url, destination_folder, audio_format, progress_var, progress_bar, status_label):
    if getattr(sys, 'frozen', False):
        bundle_dir = sys._MEIPASS
    else:
        bundle_dir = os.path.dirname(os.path.abspath(__file__))

    ffmpeg_path = os.path.join(bundle_dir, 'ffmpeg', 'ffmpeg.exe')
    ffprobe_path = os.path.join(bundle_dir, 'ffmpeg', 'ffprobe.exe')

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(destination_folder, '%(title)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': audio_format,
            'preferredquality': '192',
        }],
        'ffmpeg_location': ffmpeg_path,
        'progress_hooks': [lambda d: progress_hook(d, progress_var, progress_bar, status_label)]
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        messagebox.showinfo(translations[current_language]['success_title'], translations[current_language]['download_complete'].format(audio_format.upper()))
    except Exception as e:
        messagebox.showerror(translations[current_language]['error_title'], translations[current_language]['download_error'].format(str(e)))

def progress_hook(d, progress_var, progress_bar, status_label):
    if d['status'] == 'downloading':
        total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
        downloaded_bytes = d.get('downloaded_bytes', 0)
        percent = int(downloaded_bytes / total_bytes * 100) if total_bytes > 0 else 0
        speed = d.get('speed', 0) or 0
        size_in_mib = total_bytes / 1024 / 1024 if total_bytes > 0 else 0
        speed_in_kib = speed / 1024 if speed > 0 else 0
        update_progress(percent, progress_var, progress_bar)
        status_label.config(text=translations[current_language]['downloading'].format(percent, speed_in_kib, size_in_mib))
    elif d['status'] == 'finished':
        update_progress(100, progress_var, progress_bar)
        status_label.config(text=translations[current_language]['conversion_complete'].format(audio_format.upper()))

def start_download(audio_format):
    url = url_entry.get()
    if not url:
        messagebox.showwarning(translations[current_language]['warning_title'], translations[current_language]['enter_url'])
        return

    destination_folder = destination_folder_var.get()
    if not destination_folder:
        messagebox.showwarning(translations[current_language]['warning_title'], translations[current_language]['choose_folder'])
        return

    save_config(destination_folder, current_language, dark_mode, audio_format)

    download_thread = Thread(target=download_audio, args=(url, destination_folder, audio_format, progress_var, progress_bar, status_label))
    download_thread.start()

def select_destination_folder():
    folder = filedialog.askdirectory()
    if folder:
        destination_folder_var.set(folder)

def toggle_mode():
    global dark_mode
    dark_mode = not dark_mode
    update_mode()
    mode_text = translations[current_language].get('light_mode', 'Light Mode') if dark_mode else translations[current_language].get('dark_mode', 'Dark Mode')
    mode_button.config(text=mode_text)

def update_mode():
    mode_text = translations[current_language].get('light_mode', 'Light Mode') if dark_mode else translations[current_language].get('dark_mode', 'Dark Mode')
    if dark_mode:
        root.tk_setPalette(background='#333', foreground='#FFF')
        style.configure('TFrame', background='#333')
        style.configure('TLabel', background='#333', foreground='#FFF')
        style.configure('TProgressbar', troughcolor='#555', background='#888', thickness=20)
        destination_entry.configure(bg='#555', fg='#FFF', insertbackground='white')
        url_entry.configure(bg='#555', fg='#FFF', insertbackground='white')
        mode_button.configure(bg='#555', fg='#FFF', text=mode_text)
        select_button.configure(bg='#555', fg='#FFF')
        mp3_button.configure(bg='#555', fg='#FFF')
        wav_button.configure(bg='#555', fg='#FFF')
        ogg_button.configure(bg='#555', fg='#FFF')
        flac_button.configure(bg='#555', fg='#FFF')
        m4a_button.configure(bg='#555', fg='#FFF')
    else:
        root.tk_setPalette(background='#FFF', foreground='#000')
        style.configure('TFrame', background='#FFF')
        style.configure('TLabel', background='#FFF', foreground='#000')
        style.configure('TProgressbar', troughcolor='#DDD', background='#0078d4', thickness=20)
        destination_entry.configure(bg='#FFF', fg='#000', insertbackground='black')
        url_entry.configure(bg='#FFF', fg='#000', insertbackground='black')
        mode_button.configure(bg='#F0F0F0', fg='#000', text=mode_text)
        select_button.configure(bg='#F0F0F0', fg='#000')
        mp3_button.configure(bg='#F0F0F0', fg='#000')
        wav_button.configure(bg='#F0F0F0', fg='#000')
        ogg_button.configure(bg='#F0F0F0', fg='#000')
        flac_button.configure(bg='#F0F0F0', fg='#000')
        m4a_button.configure(bg='#F0F0F0', fg='#000')

def set_language(lang):
    global current_language
    current_language = lang
    update_language()
    save_config(destination_folder_var.get(), current_language, dark_mode, audio_format)

def update_language():
    translations_for_current_language = translations.get(current_language, {})
    root.title(translations_for_current_language.get('window_title', "YouTube Audio Downloader"))
    url_label.config(text=translations_for_current_language.get('url_label', "Video Link:"))
    destination_label.config(text=translations_for_current_language.get('destination_label', "Destination Folder:"))
    mp3_button.config(text=translations_for_current_language.get('mp3_button', "MP3"))
    wav_button.config(text=translations_for_current_language.get('wav_button', "WAV"))
    ogg_button.config(text=translations_for_current_language.get('ogg_button', "OGG"))
    flac_button.config(text=translations_for_current_language.get('flac_button', "FLAC"))
    m4a_button.config(text=translations_for_current_language.get('m4a_button', "M4A"))
    status_label.config(text=translations_for_current_language.get('waiting', "Waiting..."))
    header.config(text=translations_for_current_language.get('window_title', "YouTube Audio Downloader"))
    version_label.config(text=translations_for_current_language.get('version_label', f"Version: {version}"))
    mode_text = translations_for_current_language.get('light_mode', 'Light Mode') if dark_mode else translations_for_current_language.get('dark_mode', 'Dark Mode')
    mode_button.config(text=mode_text)

version = "1.0.0"
translations = {
    'English': {
        'window_title': "YouTube Audio Downloader",
        'url_label': "Video Link:",
        'destination_label': "Destination Folder:",
        'mp3_button': "MP3",
        'wav_button': "WAV",
        'ogg_button': "OGG",
        'flac_button': "FLAC",
        'm4a_button': "M4A",
        'mode_button': "Dark Mode",
        'download_complete': "The audio has been successfully downloaded as {}.",
        'download_error': "An error occurred: {}",
        'downloading': "Downloading: {}% - Speed: {:.2f} KiB/s - Size: {:.2f} MiB",
        'conversion_complete': "Conversion complete: {}",
        'waiting': "Waiting...",
        'success_title': "Download Complete",
        'error_title': "Download Error",
        'warning_title': "Warning",
        'enter_url': "Please enter a video URL.",
        'choose_folder': "Please select a destination folder.",
        'dark_mode': "Dark Mode",
        'light_mode': "Light Mode",
        'version_label': f"Version: {version}"
    },
    'PT-BR': {
        'window_title': "Descargador de Ýudio do YouTube",
        'url_label': "Link do Vídeo:",
        'destination_label': "Pasta de Destino:",
        'mp3_button': "MP3",
        'wav_button': "WAV",
        'ogg_button': "OGG",
        'flac_button': "FLAC",
        'm4a_button': "M4A",
        'mode_button': "Modo Escuro",
        'download_complete': "O áudio foi baixado com sucesso como {}.",
        'download_error': "Ocorreu um erro: {}",
        'downloading': "Baixando: {}% - Velocidade: {:.2f} KiB/s - Tamanho: {:.2f} MiB",
        'conversion_complete': "Conversão completa: {}",
        'waiting': "Aguardando...",
        'success_title': "Download Concluído",
        'error_title': "Erro de Download",
        'warning_title': "Aviso",
        'enter_url': "Por favor, insira um URL de vídeo.",
        'choose_folder': "Por favor, selecione uma pasta de destino.",
        'dark_mode': "Modo Escuro",
        'light_mode': "Modo Claro",
        'version_label': f"Versão: {version}"
    },
    'PT-PT': {
        'window_title': "Descarregador de Ýudio do YouTube",
        'url_label': "Link do Vídeo:",
        'destination_label': "Pasta de Destino:",
        'mp3_button': "MP3",
        'wav_button': "WAV",
        'ogg_button': "OGG",
        'flac_button': "FLAC",
        'm4a_button': "M4A",
        'mode_button': "Modo Escuro",
        'download_complete': "O áudio foi descarregado com sucesso como {}.",
        'download_error': "Ocorreu um erro: {}",
        'downloading': "A descarregar: {}% - Velocidade: {:.2f} KiB/s - Tamanho: {:.2f} MiB",
        'conversion_complete': "Conversão completa: {}",
        'waiting': "A aguardar...",
        'success_title': "Download Completo",
        'error_title': "Erro de Download",
        'warning_title': "Aviso",
        'enter_url': "Por favor, insira um URL de vídeo.",
        'choose_folder': "Por favor, selecione uma pasta de destino.",
        'dark_mode': "Modo Escuro",
        'light_mode': "Modo Claro",
        'version_label': f"Versão: {version}"
    }
}

destination_folder, current_language, dark_mode, audio_format = load_config()

root = tk.Tk()
root.geometry("800x450")
root.title(translations[current_language]['window_title'])

style = Style()
style.configure('TFrame', background='#FFF')
style.configure('TLabel', background='#FFF', foreground='#000')
style.configure('TProgressbar', troughcolor='#DDD', background='#0078d4', thickness=20)

frame = Frame(root, padding=10)
frame.pack(expand=True, fill='both')

header = Label(frame, text=translations[current_language]['window_title'], font=('Arial', 16, 'bold'))
header.pack(pady=(10, 0))

version_label = Label(frame, text=translations[current_language]['version_label'], font=('Arial', 12, 'italic'))
version_label.pack(pady=(5, 20)) 

url_label = Label(frame, text=translations[current_language]['url_label'])
url_label.pack(pady=5, anchor='w')
url_entry = tk.Entry(frame, width=60)
url_entry.pack(pady=5, fill='x')

destination_label = Label(frame, text=translations[current_language]['destination_label'])
destination_label.pack(pady=5, anchor='w')
destination_folder_var = tk.StringVar()
destination_folder_var.set(destination_folder)

destination_frame = Frame(frame)
destination_frame.pack(pady=5, fill='x')
destination_entry = tk.Entry(destination_frame, textvariable=destination_folder_var, width=50)
destination_entry.pack(side=tk.LEFT, padx=5, fill='x', expand=True)
select_button = tk.Button(destination_frame, text="Select", command=select_destination_folder)
select_button.pack(side=tk.RIGHT, padx=5)

formats_frame = Frame(frame)
formats_frame.pack(pady=(20, 10))

mp3_button = tk.Button(formats_frame, text=translations[current_language]['mp3_button'], command=lambda: start_download('mp3'))
mp3_button.pack(side=tk.LEFT, padx=5)

wav_button = tk.Button(formats_frame, text=translations[current_language]['wav_button'], command=lambda: start_download('wav'))
wav_button.pack(side=tk.LEFT, padx=5)

ogg_button = tk.Button(formats_frame, text=translations[current_language]['ogg_button'], command=lambda: start_download('ogg'))
ogg_button.pack(side=tk.LEFT, padx=5)

flac_button = tk.Button(formats_frame, text=translations[current_language]['flac_button'], command=lambda: start_download('flac'))
flac_button.pack(side=tk.LEFT, padx=5)

m4a_button = tk.Button(formats_frame, text=translations[current_language]['m4a_button'], command=lambda: start_download('m4a'))
m4a_button.pack(side=tk.LEFT, padx=5)

progress_var = tk.IntVar()
progress_bar = Progressbar(frame, orient='horizontal', length=500, mode='determinate', maximum=100, variable=progress_var)
progress_bar.pack(pady=(20, 30))

status_label = Label(frame, text=translations[current_language].get('waiting', "Waiting..."))
status_label.pack(pady=5)

mode_button = tk.Button(root, command=toggle_mode, text=translations[current_language]['mode_button'], width=15)
mode_button.pack(side=tk.RIGHT, padx=10, pady=10, anchor='se') 

language_frame = Frame(root)
language_frame.pack(side=tk.LEFT, padx=10, pady=10, anchor='sw')

eng_button = tk.Button(language_frame, text="ENG", command=lambda: set_language('English'))
eng_button.pack(side=tk.LEFT, padx=5)

pt_br_button = tk.Button(language_frame, text="PT-BR", command=lambda: set_language('PT-BR'))
pt_br_button.pack(side=tk.LEFT, padx=5)

pt_pt_button = tk.Button(language_frame, text="PT-PT", command=lambda: set_language('PT-PT'))
pt_pt_button.pack(side=tk.LEFT, padx=5)

update_mode()
update_language()

root.mainloop()
