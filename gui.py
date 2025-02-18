import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from PIL import Image, ImageTk
from image_stego import ImageSteganography
from audio_stego import AudioSteganography
from video_stego import VideoSteganography
import threading

class SteganographyGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SecureStego - Advanced Steganography Tool")
        self.root.geometry("1000x800")
        self.setup_ui()
        self.setup_menu()
        self.current_file = None
        self.preview_image = None
        self.dark_mode = False

    def setup_menu(self):
        menu_bar = tk.Menu(self.root)
        
        # File menu
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menu_bar.add_cascade(label="File", menu=file_menu)
        
        # Help menu
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        menu_bar.add_cascade(label="Help", menu=help_menu)
        
        # Theme menu
        theme_menu = tk.Menu(menu_bar, tearoff=0)
        theme_menu.add_command(label="Toggle Dark Mode", command=self.toggle_dark_mode)
        menu_bar.add_cascade(label="Theme", menu=theme_menu)
        
        self.root.config(menu=menu_bar)

    def setup_ui(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Media type selection
        media_frame = ttk.LabelFrame(main_frame, text="Select Media Type")
        media_frame.pack(fill=tk.X, pady=5)
        
        self.media_type = tk.StringVar(value="Image")
        media_options = ["Image", "Audio", "Video"]
        for option in media_options:
            ttk.Radiobutton(media_frame, text=option, variable=self.media_type,
                           value=option, command=self.update_ui).pack(side=tk.LEFT, padx=5)

        # Preview area
        self.preview_frame = ttk.LabelFrame(main_frame, text="Preview")
        self.preview_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.preview_label = ttk.Label(self.preview_frame)
        self.preview_label.pack(expand=True)

        # Message input
        msg_frame = ttk.LabelFrame(main_frame, text="Secret Message")
        msg_frame.pack(fill=tk.X, pady=5)
        
        self.message_entry = scrolledtext.ScrolledText(msg_frame, height=4, wrap=tk.WORD)
        self.message_entry.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(msg_frame, text="Load Message from File", 
                  command=self.load_message_from_file).pack(side=tk.LEFT, pady=5)
        ttk.Button(msg_frame, text="Clear Message", 
                  command=lambda: self.message_entry.delete(1.0, tk.END)).pack(side=tk.RIGHT, pady=5)

        # Action buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(btn_frame, text="Encode", command=self.encode, 
                  style="Accent.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Decode", command=self.decode, 
                  style="Accent.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Clear All", command=self.clear_all).pack(side=tk.RIGHT)

        # Status bar
        self.status_bar = ttk.Label(self.root, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Configure styles
        self.root.style = ttk.Style()
        self.root.style.configure("Accent.TButton", font=('Helvetica', 10, 'bold'))
        self.root.style.map("Accent.TButton",
                          foreground=[('active', 'white'), ('!active', 'black')],
                          background=[('active', '#347083'), ('!active', '#4595b4')])

    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        bg_color = "#2E2E2E" if self.dark_mode else "white"
        fg_color = "white" if self.dark_mode else "black"
        self.root.configure(bg=bg_color)
        for widget in self.root.winfo_children():
            widget.configure(bg=bg_color, fg=fg_color)

    def update_ui(self):
        media_type = self.media_type.get()
        self.clear_preview()
        self.status_bar.config(text=f"Selected media type: {media_type}")

    def open_file(self):
        media_type = self.media_type.get()
        filetypes = self.get_file_types(media_type)
        self.current_file = filedialog.askopenfilename(filetypes=filetypes)
        if self.current_file:
            self.show_preview(self.current_file)
            self.status_bar.config(text=f"Loaded: {self.current_file}")

    def save_file(self):
        media_type = self.media_type.get()
        filetypes = self.get_file_types(media_type)
        filename = filedialog.asksaveasfilename(filetypes=filetypes, defaultextension=filetypes[0][1])
        return filename

    def get_file_types(self, media_type):
        return {
            "Image": [("Image files", "*.png *.bmp *.jpg *.jpeg")],
            "Audio": [("Audio files", "*.wav *.mp3")],
            "Video": [("Video files", "*.avi *.mp4")]
        }.get(media_type, [("All files", "*.*")])

    def show_preview(self, file_path):
        media_type = self.media_type.get()
        try:
            if media_type == "Image":
                img = Image.open(file_path)
                img.thumbnail((400, 400))
                self.preview_image = ImageTk.PhotoImage(img)
                self.preview_label.config(image=self.preview_image)
                self.preview_label.image = self.preview_image
            elif media_type == "Audio":
                self.preview_label.config(image='')
                self.preview_label.config(text=f"Audio File: {file_path}\n\nPreview not available for audio files.")
            elif media_type == "Video":
                self.preview_label.config(image='')
                self.preview_label.config(text=f"Video File: {file_path}\n\nPreview not available for video files.")
        except Exception as e:
            messagebox.showerror("Preview Error", f"Could not load preview: {str(e)}")

    def clear_preview(self):
        self.preview_label.config(image='')
        self.preview_label.config(text='')
        self.preview_image = None

    def load_message_from_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    self.message_entry.delete(1.0, tk.END)
                    self.message_entry.insert(tk.END, f.read())
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load message: {str(e)}")

    def encode(self):
        media_type = self.media_type.get()
        message = self.message_entry.get("1.0", tk.END).strip()
        
        if not message:
            messagebox.showwarning("Input Error", "Please enter a message to encode!")
            return
            
        try:
            output_path = self.save_file()
            if not output_path:
                return
                
            self.status_bar.config(text="Encoding... Please wait")
            self.root.update_idletasks()
            
            key = None
            if self.dark_mode:
                key = "mysecretkey"  # Example key for encryption

            if media_type == "Image":
                ImageSteganography.encode(self.current_file, message, output_path, key)
            elif media_type == "Audio":
                AudioSteganography.encode(self.current_file, message, output_path, key)
            elif media_type == "Video":
                VideoSteganography.encode(self.current_file, message, output_path, key)
                
            self.status_bar.config(text=f"Encoded successfully to: {output_path}")
            messagebox.showinfo("Success", "Message encoded successfully!")
            
        except Exception as e:
            messagebox.showerror("Encoding Error", f"Failed to encode: {str(e)}")
            self.status_bar.config(text="Encoding failed")
        finally:
            self.root.update_idletasks()

    def decode(self):
        media_type = self.media_type.get()
        if not self.current_file:
            messagebox.showwarning("Input Error", "Please select a file to decode!")
            return
            
        try:
            self.status_bar.config(text="Decoding... Please wait")
            self.root.update_idletasks()
            
            key = None
            if self.dark_mode:
                key = "mysecretkey"  # Example key for decryption

            if media_type == "Image":
                message = ImageSteganography.decode(self.current_file, key)
            elif media_type == "Audio":
                message = AudioSteganography.decode(self.current_file, key)
            elif media_type == "Video":
                message = VideoSteganography.decode(self.current_file, key)
                
            self.message_entry.delete(1.0, tk.END)
            self.message_entry.insert(tk.END, message)
            self.status_bar.config(text="Decoding completed successfully")
            messagebox.showinfo("Decoded Message", f"Decoded message:\n\n{message}")
            
        except Exception as e:
            messagebox.showerror("Decoding Error", f"Failed to decode: {str(e)}")
            self.status_bar.config(text="Decoding failed")
        finally:
            self.root.update_idletasks()

    def clear_all(self):
        self.current_file = None
        self.message_entry.delete(1.0, tk.END)
        self.clear_preview()
        self.status_bar.config(text="Ready")

    def show_about(self):
        about_text = """SecureStego - Advanced Steganography Tool
Version 3.0
Developed by Shambhu Kapadi
        
Features:
- Encode/decode messages in images, audio, and video files
- AES encryption for added security
- Multi-format support (PNG, BMP, JPEG, WAV, MP3, AVI, MP4)
- Batch processing for multiple files
- Real-time preview and progress indicators
- Dark mode and theme customization"""
        messagebox.showinfo("About SecureStego", about_text)

if __name__ == "__main__":
    root = tk.Tk()
    app = SteganographyGUI(root)
    root.mainloop()
