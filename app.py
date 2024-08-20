import os
import json
import subprocess
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, Toplevel
from tkinter.ttk import Progressbar, Label, Frame, Style
from threading import Thread

repo_label = None

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
            return (config.get('destination_folder', ''), 
                    config.get('language', 'ENG'), 
                    config.get('dark_mode', False), 
                    config.get('format', 'wav'))
    return ('', 'ENG', False, 'wav')

def set_language(lang):
    global current_language
    current_language = lang
    update_language()
    save_config(destination_folder_var.get(), current_language, dark_mode, audio_format)

def update_progress(percent, progress_var, progress_bar):
    progress_var.set(percent)
    progress_bar.update()

def download_audio(url, destination_folder, audio_format, progress_var, progress_bar, status_label, download_count_label):
    ffmpeg_path = get_ffmpeg_path()
    if not ffmpeg_path:
        messagebox.showerror(translations[current_language]['error_title'], translations[current_language]['ffmpeg_missing'])
        return

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(destination_folder, '%(playlist)s/%(title)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': audio_format,
            'preferredquality': '192',
        }],
        'ffmpeg_location': ffmpeg_path,
        'progress_hooks': [lambda d: progress_hook(d, progress_var, progress_bar, status_label, download_count_label, audio_format)],
        'noplaylist': False,
        'playlistend': 0
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        messagebox.showinfo(translations[current_language]['success_title'], translations[current_language]['download_complete'].format(audio_format.upper()))
    except Exception as e:
        messagebox.showerror(translations[current_language]['error_title'], translations[current_language]['download_error'].format(str(e)))

def get_ffmpeg_path():
    if getattr(sys, 'frozen', False):
        bundle_dir = sys._MEIPASS
    else:
        bundle_dir = os.path.dirname(os.path.abspath(__file__))
    
    ffmpeg_path = os.path.join(bundle_dir, 'ffmpeg', 'ffmpeg.exe')
    if not os.path.isfile(ffmpeg_path):
        ffmpeg_path = None
    return ffmpeg_path

def progress_hook(d, progress_var, progress_bar, status_label, download_count_label, audio_format):
    if not hasattr(progress_hook, 'downloaded_videos'):
        progress_hook.downloaded_videos = 0
        progress_hook.total_videos = 0

    if d['status'] == 'downloading':
        if progress_hook.total_videos == 0:
            progress_hook.total_videos = d.get('playlist_count', 1)

        total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
        downloaded_bytes = d.get('downloaded_bytes', 0)
        percent = int(downloaded_bytes / total_bytes * 100) if total_bytes > 0 else 0
        speed = d.get('speed', 0) or 0
        size_in_mib = total_bytes / 1024 / 1024 if total_bytes > 0 else 0
        speed_in_kib = speed / 1024 if speed > 0 else 0
        update_progress(percent, progress_var, progress_bar)
        status_label.config(text=translations[current_language]['downloading'].format(percent, speed_in_kib, size_in_mib))

    elif d['status'] == 'finished':
        progress_hook.downloaded_videos += 1
        update_progress(100, progress_var, progress_bar)
        status_label.config(text=translations[current_language]['conversion_complete'].format(audio_format.upper()))
        download_count_label.config(text=translations[current_language]['download_count'].format(progress_hook.downloaded_videos, progress_hook.total_videos))

    elif d['status'] == 'processing':
        status_label.config(text=translations[current_language]['processing'].format(audio_format.upper()))

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

    download_thread = Thread(target=download_audio, args=(url, destination_folder, audio_format, progress_var, progress_bar, status_label, download_count_label))
    download_thread.start()

def select_destination_folder():
    folder = filedialog.askdirectory()
    if folder:
        destination_folder_var.set(folder)

def toggle_mode():
    global dark_mode
    global repo_label
    dark_mode = not dark_mode
    update_mode()
    
    if repo_label is not None:
        update_link_color(repo_label)
        
    mode_text = translations[current_language]['light_mode'] if dark_mode else translations[current_language]['dark_mode']
    mode_menu.entryconfig(0, label=mode_text)

def update_mode():
    mode_text = translations[current_language]['light_mode'] if dark_mode else translations[current_language]['dark_mode']
    if dark_mode:
        root.tk_setPalette(background='#333', foreground='#FFF')
        style.configure('TFrame', background='#333')
        style.configure('TLabel', background='#333', foreground='#FFF')
        style.configure('TProgressbar', troughcolor='#555', background='#888', thickness=20)
        destination_entry.configure(bg='#555', fg='#FFF', insertbackground='white')
        url_entry.configure(bg='#555', fg='#FFF', insertbackground='white')
        select_button.configure(bg='#555', fg='#FFF')
        mp3_button.configure(bg='#555', fg='#FFF')
        wav_button.configure(bg='#555', fg='#FFF')
        flac_button.configure(bg='#555', fg='#FFF')
    else:
        root.tk_setPalette(background='#FFF', foreground='#000')
        style.configure('TFrame', background='#FFF')
        style.configure('TLabel', background='#FFF', foreground='#000')
        style.configure('TProgressbar', troughcolor='#DDD', background='#0078d4', thickness=20)
        destination_entry.configure(bg='#FFF', fg='#000', insertbackground='black')
        url_entry.configure(bg='#FFF', fg='#000', insertbackground='black')
        select_button.configure(bg='#F0F0F0', fg='#000')
        mp3_button.configure(bg='#F0F0F0', fg='#000')
        wav_button.configure(bg='#F0F0F0', fg='#000')
        flac_button.configure(bg='#F0F0F0', fg='#000')
    mode_menu.entryconfig(0, label=mode_text)

def update_language():
    translations_for_current_language = translations.get(current_language, {})
    
    root.title(translations_for_current_language.get('window_title', "YouTube Audio Downloader"))
    
    header.config(text=translations_for_current_language.get('window_title', "YouTube Audio Downloader"))
    url_label.config(text=translations_for_current_language.get('url_label', "Video Link:"))
    destination_label.config(text=translations_for_current_language.get('destination_label', "Destination Folder:"))
    mp3_button.config(text=translations_for_current_language.get('mp3_button', "MP3"))
    wav_button.config(text=translations_for_current_language.get('wav_button', "WAV"))
    flac_button.config(text=translations_for_current_language.get('flac_button', "FLAC"))
    version_label.config(text=translations_for_current_language.get('version_label', "Version: 1.0"))
    select_button.config(text=translations_for_current_language.get('choose_export_folder', "Choose Export Folder"))
    status_label.config(text=translations_for_current_language.get('waiting', "Waiting..."))

    mode_text = translations_for_current_language.get('light_mode') if dark_mode else translations_for_current_language.get('dark_mode')
    mode_menu.entryconfig(0, label=mode_text)

    menu_bar.delete(0, 'end')

    menu_bar.add_cascade(label=translations_for_current_language.get('language_menu', "Language"), menu=language_menu)
    
    menu_bar.add_cascade(label=translations_for_current_language.get('mode_menu', "Mode"), menu=mode_menu)
    
    menu_bar.add_command(label=translations_for_current_language.get('about_menu', "About"), command=open_about_window)

    update_mode()




def open_about_window():
    about_window = Toplevel(root)
    about_window.title(translations[current_language]['about_title'])
    about_window.geometry("450x350")

    icon_path = os.path.join(os.path.dirname(__file__), 'ico', 'icon.ico')
    about_window.iconbitmap(icon_path)

    icon_image = tk.PhotoImage(file=os.path.join(os.path.dirname(__file__), 'ico', 'icon.png'))

    icon_label = tk.Label(about_window, image=icon_image)
    icon_label.image = icon_image
    icon_label.pack(pady=10)

    title_label = tk.Label(about_window, text=translations[current_language]['about_tool_name'], font=('Arial', 18, 'bold'))
    title_label.pack(pady=10)

    version_label = tk.Label(about_window, text=translations[current_language]['version_label'])
    version_label.pack(pady=5)

    repo_label = tk.Label(about_window, text=translations[current_language]['repo_link'], cursor='hand2')
    repo_label.pack(pady=5)
    repo_label.bind("<Button-1>", lambda e: open_link(translations[current_language]['repo_link']))

    contributors_label = tk.Label(about_window, text=translations[current_language]['contributors'])
    contributors_label.pack(pady=5)

    update_link_color(repo_label)

    about_window.mainloop()

def update_link_color(label):

    if dark_mode:
        label.config(fg='#ADD8E6')
    else:
        label.config(fg='blue')


def open_link(url):
    if sys.platform.startswith('linux'):
        subprocess.Popen(['xdg-open', url])
    elif sys.platform.startswith('win'):
        subprocess.Popen(['start', url], shell=True)
    elif sys.platform.startswith('darwin'):
        subprocess.Popen(['open', url])

translations = {
    'ENG': {
        'window_title': "YouTube Audio Downloader",
        'url_label': "Video Link:",
        'destination_label': "Destination Folder:",
        'mp3_button': "MP3",
        'wav_button': "WAV",
        'flac_button': "FLAC",
        'language_menu': "Language",
        'mode_menu': "Mode",
        'dark_mode': "Dark Mode",
        'light_mode': "Light Mode",
        'download_complete': "Download complete as {}.",
        'download_error': "An error occurred: {}",
        'downloading': "Downloading: {}% - Speed: {:.2f} KiB/s - Size: {:.2f} MiB",
        'conversion_complete': "Conversion complete: {}",
        'waiting': "Waiting...",
        'success_title': "Download Complete",
        'error_title': "Download Error",
        'warning_title': "Input Error",
        'enter_url': "Please enter a video URL.",
        'choose_folder': "Please choose a destination folder.",
        'download_count': "Downloaded {}/{} videos",
        'processing': "Processing: {}",
        'version_label': "Version: 1.1.1",
        'about_menu': "About",
        'about_title': "About",
        'about_tool_name': "YouTube Audio Downloader",
        'repo_link': "Repository: https://github.com/itsneufox/yt_audio_download",
        'contributors': "Contributors: itsneufox, guighfunky, itsrn",
        'choose_export_folder': "Choose Export Folder",
        'ffmpeg_missing': "FFmpeg executable not found. Please make sure 'ffmpeg.exe' is in the 'ffmpeg' folder."
    },
    'PT-BR': {
        'window_title': "Baixador de Áudio do YouTube",
        'url_label': "Link do Vídeo:",
        'destination_label': "Pasta de Destino:",
        'mp3_button': "MP3",
        'wav_button': "WAV",
        'flac_button': "FLAC",
        'language_menu': "Linguagem",
        'mode_menu': "Modo",
        'dark_mode': "Modo Escuro",
        'light_mode': "Modo Claro",
        'download_complete': "O áudio foi baixado com sucesso como {}.",
        'download_error': "Ocorreu um erro: {}",
        'downloading': "Baixando: {}% - Velocidade: {:.2f} KiB/s - Tamanho: {:.2f} MiB",
        'conversion_complete': "Conversão completa: {}",
        'waiting': "Aguardando...",
        'success_title': "Download Completo",
        'error_title': "Erro no Download",
        'warning_title': "Erro de Entrada",
        'enter_url': "Por favor, insira o URL de um vídeo.",
        'choose_folder': "Por favor, escolha uma pasta de destino.",
        'download_count': "Baixado {}/{} vídeos",
        'processing': "Processando: {}",
        'version_label': "Versão: 1.1.1",
        'about_menu': "Sobre",
        'about_title': "Sobre",
        'about_tool_name': "Baixador de Áudio do YouTube",
        'repo_link': "Repositório: https://github.com/itsneufox/yt_audio_download",
        'contributors': "Contribuidores: itsneufox, guighfunky, itsrn",
        'choose_export_folder': "Escolher Pasta de Exportação",
        'ffmpeg_missing': "Executável do FFmpeg não encontrado. Certifique-se de que 'ffmpeg.exe' está na pasta 'ffmpeg'."
    },
    'PT-PT': {
        'window_title': "Descarregador de Áudio do YouTube",
        'url_label': "Link do Vídeo:",
        'destination_label': "Pasta de Destino:",
        'mp3_button': "MP3",
        'wav_button': "WAV",
        'flac_button': "FLAC",
        'language_menu': "Linguagem",
        'mode_menu': "Modo",
        'dark_mode': "Modo Escuro",
        'light_mode': "Modo Claro",
        'download_complete': "O áudio foi descarregado com sucesso como {}.",
        'download_error': "Ocorreu um erro: {}",
        'downloading': "A descarregar: {}% - Velocidade: {:.2f} KiB/s - Tamanho: {:.2f} MiB",
        'conversion_complete': "Conversão completa: {}",
        'waiting': "A aguardar...",
        'success_title': "Descarregamento Completo",
        'error_title': "Erro no Descarregamento",
        'warning_title': "Erro de Entrada",
        'enter_url': "Por favor, insira o URL de um vídeo.",
        'choose_folder': "Por favor, escolha uma pasta de destino.",
        'download_count': "Descarregado {}/{} vídeos",
        'processing': "A Processar: {}",
        'version_label': "Versão: 1.1.1",
        'about_menu': "Sobre",
        'about_title': "Sobre",
        'about_tool_name': "Descarregador de Áudio do YouTube",
        'repo_link': "Repositório: https://github.com/itsneufox/yt_audio_download",
        'contributors': "Contribuidores: itsneufox, guighfunky, itsrn",
        'choose_export_folder': "Escolher Pasta de Exportação",
        'ffmpeg_missing': "Executável do FFmpeg não encontrado. Certifique-se de que 'ffmpeg.exe' está na pasta 'ffmpeg'."
    },
    'ES': {
        'window_title': "Descargador de Audio de YouTube",
        'url_label': "Enlace del Video:",
        'destination_label': "Carpeta de Destino:",
        'mp3_button': "MP3",
        'wav_button': "WAV",
        'flac_button': "FLAC",
        'language_menu': "Idioma",
        'mode_menu': "Modo",
        'dark_mode': "Modo Oscuro",
        'light_mode': "Modo Claro",
        'download_complete': "El audio se ha descargado con éxito como {}.",
        'download_error': "Ocurrió un error: {}",
        'downloading': "Descargando: {}% - Velocidad: {:.2f} KiB/s - Tamaño: {:.2f} MiB",
        'conversion_complete': "Conversión completa: {}",
        'waiting': "Esperando...",
        'success_title': "Descarga Completa",
        'error_title': "Error de Descarga",
        'warning_title': "Error de Entrada",
        'enter_url': "Por favor, introduce la URL de un video.",
        'choose_folder': "Por favor, elige una carpeta de destino.",
        'download_count': "Descargado {}/{} videos",
        'processing': "Procesando: {}",
        'version_label': "Versión: 1.1.1",
        'about_menu': "Acerca de",
        'about_title': "Acerca de",
        'about_tool_name': "Descargador de Audio de YouTube",
        'repo_link': "Repositorio: https://github.com/itsneufox/yt_audio_download",
        'contributors': "Colaboradores: itsneufox, guighfunky, itsrn",
        'choose_export_folder': "Elegir Carpeta de Exportación",
        'ffmpeg_missing': "No se encontró el ejecutable de FFmpeg. Asegúrate de que 'ffmpeg.exe' esté en la carpeta 'ffmpeg'."
    },
    'FR': {
        'window_title': "Téléchargeur Audio YouTube",
        'url_label': "Lien de la Vidéo :",
        'destination_label': "Dossier de Destination :",
        'mp3_button': "MP3",
        'wav_button': "WAV",
        'flac_button': "FLAC",
        'language_menu': "Langue",
        'mode_menu': "Mode",
        'dark_mode': "Mode Sombre",
        'light_mode': "Mode Clair",
        'download_complete': "L'audio a été téléchargé avec succès en {}.",
        'download_error': "Une erreur s'est produite : {}",
        'downloading': "Téléchargement : {}% - Vitesse : {:.2f} KiB/s - Taille : {:.2f} MiB",
        'conversion_complete': "Conversion terminée : {}",
        'waiting': "En attente...",
        'success_title': "Téléchargement Terminé",
        'error_title': "Erreur de Téléchargement",
        'warning_title': "Erreur d'Entrée",
        'enter_url': "Veuillez entrer l'URL d'une vidéo.",
        'choose_folder': "Veuillez choisir un dossier de destination.",
        'download_count': "Téléchargé {}/{} vidéos",
        'processing': "Traitement : {}",
        'version_label': "Version : 1.1.1",
        'about_menu': "À Propos",
        'about_title': "À Propos",
        'about_tool_name': "Téléchargeur Audio YouTube",
        'repo_link': "Répertoire : https://github.com/itsneufox/yt_audio_download",
        'contributors': "Contributeurs : itsneufox, guighfunky, itsrn",
        'choose_export_folder': "Choisir Dossier d'Exportation",
        'ffmpeg_missing': "L'exécutable FFmpeg est introuvable. Assurez-vous que 'ffmpeg.exe' est dans le dossier 'ffmpeg'."
    },
    'DE': {
        'window_title': "YouTube Audio Downloader",
        'url_label': "Video-Link:",
        'destination_label': "Zielordner:",
        'mp3_button': "MP3",
        'wav_button': "WAV",
        'flac_button': "FLAC",
        'language_menu': "Sprache",
        'mode_menu': "Modus",
        'dark_mode': "Dunkler Modus",
        'light_mode': "Heller Modus",
        'download_complete': "Das Audio wurde erfolgreich als {} heruntergeladen.",
        'download_error': "Es ist ein Fehler aufgetreten: {}",
        'downloading': "Herunterladen: {}% - Geschwindigkeit: {:.2f} KiB/s - Größe: {:.2f} MiB",
        'conversion_complete': "Konvertierung abgeschlossen: {}",
        'waiting': "Warten...",
        'success_title': "Download Abgeschlossen",
        'error_title': "Download-Fehler",
        'warning_title': "Eingabefehler",
        'enter_url': "Bitte geben Sie die URL eines Videos ein.",
        'choose_folder': "Bitte wählen Sie einen Zielordner.",
        'download_count': "Heruntergeladen {}/{} Videos",
        'processing': "Verarbeitung: {}",
        'version_label': "Version: 1.1.1",
        'about_menu': "Über",
        'about_title': "Über",
        'about_tool_name': "YouTube Audio Downloader",
        'repo_link': "Repository: https://github.com/itsneufox/yt_audio_download",
        'contributors': "Mitwirkende: itsneufox, guighfunky, itsrn",
        'choose_export_folder': "Exportordner wählen",
        'ffmpeg_missing': "FFmpeg-Programm nicht gefunden. Stellen Sie sicher, dass sich 'ffmpeg.exe' im Ordner 'ffmpeg' befindet."
    },
    'IT': {
        'window_title': "Downloader Audio YouTube",
        'url_label': "Link del Video:",
        'destination_label': "Cartella di Destinazione:",
        'mp3_button': "MP3",
        'wav_button': "WAV",
        'flac_button': "FLAC",
        'language_menu': "Lingua",
        'mode_menu': "Modalità",
        'dark_mode': "Modalità Scura",
        'light_mode': "Modalità Chiara",
        'download_complete': "L'audio è stato scaricato con successo come {}.",
        'download_error': "Si è verificato un errore: {}",
        'downloading': "Scaricando: {}% - Velocità: {:.2f} KiB/s - Dimensione: {:.2f} MiB",
        'conversion_complete': "Conversione completata: {}",
        'waiting': "In attesa...",
        'success_title': "Download Completato",
        'error_title': "Errore di Download",
        'warning_title': "Errore di Inserimento",
        'enter_url': "Per favore, inserisci l'URL di un video.",
        'choose_folder': "Per favore, scegli una cartella di destinazione.",
        'download_count': "Scaricato {}/{} video",
        'processing': "Elaborazione: {}",
        'version_label': "Versione: 1.1.1",
        'about_menu': "Informazioni",
        'about_title': "Informazioni",
        'about_tool_name': "Downloader Audio YouTube",
        'repo_link': "Repository: https://github.com/itsneufox/yt_audio_download",
        'contributors': "Collaboratori: itsneufox, guighfunky, itsrn",
        'choose_export_folder': "Scegli Cartella di Esportazione",
        'ffmpeg_missing': "File eseguibile di FFmpeg non trovato. Assicurati che 'ffmpeg.exe' sia nella cartella 'ffmpeg'."
    },
    'HE': {
        'window_title': "YouTube Audio Downloader",
        'url_label': "קישור לסרטון:",
        'destination_label': "תיקיית היעד:",
        'mp3_button': "MP3",
        'wav_button': "WAV",
        'flac_button': "FLAC",
        'language_menu': "שפה",
        'mode_menu': "מצב",
        'dark_mode': "עיצוב חשוך",
        'light_mode': "עיצוב מואר",
        'download_complete': "ההורדה הסתיימה כ {}.",
        'download_error': "קרתה תקלה: {}",
        'downloading': "מוריד: {}% - מהירות: {:.2f} KiB/s - גודל: {:.2f} MiB",
        'conversion_complete': "ההמרה הושלמה: {}",
        'waiting': "ממתין...",
        'success_title': "ההורדה הושלמה",
        'error_title': "שגיאת הורדה",
        'warning_title': "שגיאה בקלט",
        'enter_url': "אנא הזן קישור תקין של סרטון.",
        'choose_folder': "אנא בחר תיקיית יעד.",
        'download_count': "הורדו {}/{} סרטונים",
        'processing': "מעבד: {}",
        'version_label': "גרסה: 1.1.1",
        'about_menu': "אודות",
        'about_title': "אודות",
        'about_tool_name': "YouTube Audio Downloader",
        'repo_link': "רפוזיטורי: https://github.com/itsneufox/yt_audio_download",
        'contributors': "תורמים: itsneufox, guighfunky, itsrn",
        'choose_export_folder': "בחר תיקיית יעד",
        'ffmpeg_missing': "הקובץ של FFmpeg לא נמצא. אנא וודא שהקובץ 'ffmpeg.exe' נמצא בתוך התיקייה 'ffmpeg'."
    }

}


dest_folder, current_language, dark_mode, audio_format = load_config()

root = tk.Tk()
root.geometry("800x365")
icon_path = os.path.join(os.path.dirname(__file__), 'ico', 'icon.ico')
root.iconbitmap(icon_path)
root.title(translations[current_language]['window_title'])

destination_folder_var = tk.StringVar(value=dest_folder)
progress_var = tk.DoubleVar()

style = Style()
frame = Frame(root, padding=10)
frame.pack(fill=tk.BOTH, expand=True)

header = Label(frame, text=translations[current_language]['window_title'], font=('Arial', 16))
header.pack(pady=10)

url_label = Label(frame, text=translations[current_language]['url_label'])
url_label.pack(anchor=tk.W)
url_entry = tk.Entry(frame, width=50)
url_entry.pack(fill=tk.X, pady=5)

destination_label = Label(frame, text=translations[current_language]['destination_label'])
destination_label.pack(anchor=tk.W)
destination_entry = tk.Entry(frame, textvariable=destination_folder_var, width=50)
destination_entry.pack(fill=tk.X, pady=5)

select_button = tk.Button(frame, text=translations[current_language]['choose_export_folder'], command=select_destination_folder)
select_button.pack(pady=5)

progress_bar = Progressbar(frame, variable=progress_var, maximum=100)
progress_bar.pack(fill=tk.X, pady=10)

status_label = Label(frame, text=translations[current_language]['waiting'])
status_label.pack()

download_count_label = Label(frame, text="")
download_count_label.pack()

button_frame = Frame(frame)
button_frame.pack(pady=10)

mp3_button = tk.Button(button_frame, text=translations[current_language]['mp3_button'], command=lambda: start_download('mp3'))
mp3_button.pack(side=tk.LEFT, padx=5)

wav_button = tk.Button(button_frame, text=translations[current_language]['wav_button'], command=lambda: start_download('wav'))
wav_button.pack(side=tk.LEFT, padx=5)

flac_button = tk.Button(button_frame, text=translations[current_language]['flac_button'], command=lambda: start_download('flac'))
flac_button.pack(side=tk.LEFT, padx=5)

menu_bar = tk.Menu(root)
root.config(menu=menu_bar)

language_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Language", menu=language_menu)
language_menu.add_command(label="English", command=lambda: set_language('ENG'))
language_menu.add_command(label="Español", command=lambda: set_language('ES'))
language_menu.add_command(label="Français", command=lambda: set_language('FR'))
language_menu.add_command(label="Deutsch", command=lambda: set_language('DE'))
language_menu.add_command(label="Italiano", command=lambda: set_language('IT'))
language_menu.add_command(label="Hebrew", command=lambda: set_language('HE'))
language_menu.add_command(label="Português (BR)", command=lambda: set_language('PT-BR'))
language_menu.add_command(label="Português (PT)", command=lambda: set_language('PT-PT'))

mode_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label=translations[current_language]['mode_menu'], menu=mode_menu)
mode_menu.add_command(label=translations[current_language]['dark_mode'], command=toggle_mode)

menu_bar.add_command(label=translations[current_language]['about_menu'], command=open_about_window)


version_label = Label(frame, text=translations[current_language]['version_label'])
version_label.pack(pady=10)

update_mode()
update_language()
root.mainloop()
