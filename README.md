# 🎵 YouTube Audio Downloader

A simple GUI application for downloading audio from YouTube videos and converting it to WAV format. This application uses `yt-dlp` for downloading and `ffmpeg` for audio conversion.

## 📋 Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
  - [Install Dependencies](#install-dependencies)
  - [Add ffmpeg and ffprobe](#add-ffmpeg-and-ffprobe)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)
- [Credits](#credits)

## 🚀 Features

- Download audio from YouTube videos.
- Convert audio to WAV format.
- Progress bar showing download and conversion status.
- Dark and light mode toggle.
- GUI-based file and folder selection.

## 🛠️ Requirements

- Python 3.6+
- `yt-dlp`
- `tkinter` (comes with standard Python installation)
- `ffmpeg` and `ffprobe` for audio processing

## 📥 Installation

### Install Dependencies

1. **Clone the repository**:

    ```bash
    git clone https://github.com/yourusername/my_youtube_downloader.git
    cd my_youtube_downloader
    ```

2. **Install Python dependencies**:

    Create a `requirements.txt` file in your project directory with the following content:

    ```
    yt-dlp
    ```

    Install the dependencies using pip:

    ```bash
    pip install -r requirements.txt
    ```

### Add ffmpeg and ffprobe

1. **Download ffmpeg and ffprobe**:

    - **Windows**: Download the executables from [FFmpeg Official Site](https://ffmpeg.org/download.html) and extract them. Place `ffmpeg.exe` and `ffprobe.exe` in a directory, e.g., `bin/`.

    - **Mac**: Install using Homebrew:
      ```bash
      brew install ffmpeg
      ```

    - **Linux**: Install using your package manager:
      ```bash
      sudo apt-get install ffmpeg
      ```

2. **Include ffmpeg and ffprobe in your project**:

    - Create a `bin/` directory in your project folder and place `ffmpeg` and `ffprobe` executables inside it.

    Example folder structure:

    ```
    my_youtube_downloader/
    ├── bin/
    │   ├── ffmpeg
    │   └── ffprobe
    ├── app.py
    ├── requirements.txt
    ├── my_youtube_downloader.spec
    └── README.md
    ```

## 🎬 Usage

1. **Run the application**:

    ```bash
    python app.py
    ```

2. **Enter the YouTube video link** and select the destination folder where you want to save the audio file.

3. **Click "Download Audio"** to start the download and conversion process.

4. **Monitor the progress** using the progress bar and status label.

5. **Toggle between light and dark modes** using the mode button.

## 🤝 Contributing

Contributions are welcome! Please fork the repository, make your changes, and submit a pull request.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🎖️ Credits

This project is based on the work of [guighfunky](https://github.com/guighfunky) from the repository [baixador_audio_yt](https://github.com/guighfunky/baixador_audio_yt). Thank you for your contributions!
