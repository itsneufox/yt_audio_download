# my_youtube_downloader.spec
# -*- mode: python ; coding: utf-8 -*-

import sys
from PyInstaller.utils.hooks import copy_metadata

block_cipher = None

a = Analysis(
    ['app.py'],
    pathex=['/path/to/my_youtube_downloader'],
    binaries=[
        ('bin/ffmpeg.exe', 'bin'),
        ('bin/ffprobe.exe', 'bin')
    ],
    datas=[],
    hiddenimports=['yt_dlp'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    cipher=block_cipher,
    noarchive=False
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='yt_audio_download',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    windowed=True
)
