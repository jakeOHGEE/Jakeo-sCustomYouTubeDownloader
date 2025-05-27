Jakeo's Custom YT Downloader v0.0.1 (Alpha)
Welcome to Jakeo’s Custom YouTube Downloader! This is an early alpha release of a simple, user-friendly app for downloading YouTube videos and audio.

Features:
Download YouTube videos in MP4 format with selectable resolutions (144p to 2160p).
Download audio only in popular formats (MP3, WAV, AAC).
Progress bar showing download status.
Automatic merging of video and audio streams for MP4 downloads using ffmpeg.
Standalone .exe file with embedded ffmpeg binaries for easy use without extra setup.

Important Notes:
This app uses yt-dlp under the hood for downloading and processing media.
ffmpeg is embedded within the app, so no separate installation is required.
The app integrates the opual library to handle certain post-processing tasks.
Audio playback: Some media players may not support certain audio codecs or containers (especially AAC or WAV), so if audio files do not play, try using VLC or another versatile media player.

How to Use:
Enter the YouTube URL.
Select "MP4" for video or "Audio" for audio-only downloads.
Choose your desired resolution (for video) or audio format.
Click Download and wait for the progress bar to complete.
Find your downloaded file in the downloads folder in the app’s directory.

Known Issues:
Audio files may not be compatible with all media players.
Static Terminal
This is an alpha version: bugs and missing features are expected.

Feedback:
Feel free to open issues or pull requests on the GitHub repo.
