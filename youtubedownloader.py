import customtkinter as ctk
import yt_dlp
import os
import time
import glob
import threading
import sys
import platform

# Function to correctly get path for resources in both dev and PyInstaller exe
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS  # PyInstaller temp folder
    except Exception:
        base_path = os.path.abspath(".")  # Dev environment
    return os.path.join(base_path, relative_path)

# Set appearance and theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

# Define resolutions and audio formats
resolutions = ['144', '360', '480', '720', '1080', '2160']
audio_formats = ['MP3', 'WAV', 'AAC']

class YouTubeDownloaderApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("YouTube Downloader")
        self.geometry("600x500")
        self.resizable(False, False)

        # URL Entry
        self.url_label = ctk.CTkLabel(self, text="YouTube URL:")
        self.url_label.pack(pady=(20, 5))
        self.url_entry = ctk.CTkEntry(self, width=500)
        self.url_entry.pack()

        # Format Selection
        self.format_label = ctk.CTkLabel(self, text="Download Format:")
        self.format_label.pack(pady=(20, 5))
        self.format_option = ctk.CTkOptionMenu(self, values=["MP4", "Audio"], command=self.toggle_format_options)
        self.format_option.set("MP4")
        self.format_option.pack()

        # Resolution Selection
        self.resolution_label = ctk.CTkLabel(self, text="Resolution (MP4 only):")
        self.resolution_label.pack(pady=(20, 5))
        self.resolution_option = ctk.CTkOptionMenu(self, values=resolutions)
        self.resolution_option.set("720")
        self.resolution_option.pack()

        # Audio Format Selection
        self.audio_format_label = ctk.CTkLabel(self, text="Audio Format (Audio only):")
        self.audio_format_label.pack(pady=(20, 5))
        self.audio_format_option = ctk.CTkOptionMenu(self, values=audio_formats)
        self.audio_format_option.set("MP3")
        # Hide audio options by default
        self.audio_format_label.pack_forget()
        self.audio_format_option.pack_forget()

        # Download Button
        self.download_button = ctk.CTkButton(self, text="Download", command=self.start_download_thread)
        self.download_button.pack(pady=(20, 5))

        # Progress Bar
        self.progress_bar = ctk.CTkProgressBar(self, width=500)
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=(20, 5))

        # Output Textbox
        self.output_textbox = ctk.CTkTextbox(self, width=550, height=100)
        self.output_textbox.pack(pady=(20, 5))
        self.output_textbox.configure(state="disabled")

    def toggle_format_options(self, choice):
        if choice == "MP4":
            # Show resolution options
            self.resolution_label.pack(pady=(20, 5))
            self.resolution_option.pack()
            # Hide audio options
            self.audio_format_label.pack_forget()
            self.audio_format_option.pack_forget()
        else:
            # Hide resolution options
            self.resolution_label.pack_forget()
            self.resolution_option.pack_forget()
            # Show audio options
            self.audio_format_label.pack(pady=(20, 5))
            self.audio_format_option.pack()

    def start_download_thread(self):
        thread = threading.Thread(target=self.download_video)
        thread.start()

    def append_output(self, message):
        self.output_textbox.configure(state="normal")
        self.output_textbox.insert("end", message + "\n")
        self.output_textbox.configure(state="disabled")
        self.output_textbox.see("end")

    def download_video(self):
        url = self.url_entry.get().strip()
        format_type = self.format_option.get()
        resolution = self.resolution_option.get()
        audio_format = self.audio_format_option.get()

        if not url:
            self.append_output("❗ Please enter a URL.")
            return

        # Use resource_path to find ffmpeg folder
        ffmpeg_path = resource_path("ffmpeg")
        ffmpeg_exe_name = "ffmpeg.exe" if platform.system() == "Windows" else "ffmpeg"
        ffmpeg_exe = os.path.join(ffmpeg_path, ffmpeg_exe_name)

        if not os.path.isfile(ffmpeg_exe):
            self.append_output(f"❌ Error: ffmpeg executable not found in {ffmpeg_path}. Please check your ffmpeg folder.")
            return

        output_dir = os.path.join(os.getcwd(), "downloads")
        os.makedirs(output_dir, exist_ok=True)

        filename_template = os.path.join(output_dir, '%(title)s.%(ext)s')

        self.append_output(f"📥 Downloading to: {output_dir}")
        self.append_output(f"🔧 Using ffmpeg from: {ffmpeg_path}")

        def progress_hook(d):
            if d['status'] == 'downloading':
                percentage_str = d.get('_percent_str', '0.0%').strip()
                try:
                    progress = float(percentage_str.replace('%', '')) / 100
                except Exception:
                    progress = 0
                self.progress_bar.set(progress)
            elif d['status'] == 'finished':
                self.progress_bar.set(1)
                self.append_output("Download finished, now post-processing...")

        ydl_opts = {
            'outtmpl': filename_template,
            'ffmpeg_location': ffmpeg_path,
            'progress_hooks': [progress_hook],
            'quiet': True,
            'no_warnings': True,
        }

        if format_type == 'MP4':
            try:
                res = int(resolution)
            except ValueError:
                res = 720
            ydl_opts.update({
                'format': f"bestvideo[height<={res}]+bestaudio/best",
                'merge_output_format': 'mp4',
            })
        else:
            codec = audio_format.lower()
            postprocessor = {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': codec,
            }
            if codec == 'mp3':
                postprocessor['preferredquality'] = '192'

            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [postprocessor]
            })

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            # Update timestamp of the downloaded file
            ext = 'mp4' if format_type == 'MP4' else audio_format.lower()
            pattern = os.path.join(output_dir, f'*.{ext}')
            files = glob.glob(pattern)
            if files:
                latest_file = max(files, key=os.path.getctime)
                current_time = time.time()
                os.utime(latest_file, (current_time, current_time))
                self.append_output(f"🕒 Updated timestamp for: {latest_file}")

            self.append_output("✅ Download complete!")
            self.progress_bar.set(0)
        except Exception as e:
            self.append_output(f"❌ Error: {e}")
            self.progress_bar.set(0)

if __name__ == "__main__":
    app = YouTubeDownloaderApp()
    app.mainloop()
