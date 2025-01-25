import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import pyttsx3
import os


class ImageGalleryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Gallery with Object Recitation")
        self.root.geometry("800x600")

        # Initialize text-to-speech engine
        self.engine = pyttsx3.init()

        # UI Elements
        self.gallery_frame = tk.Frame(root)
        self.gallery_frame.pack(fill=tk.BOTH, expand=True)

        self.select_button = tk.Button(
            root, text="Select Folder", command=self.select_folder
        )
        self.select_button.pack(pady=10)

        self.image_files = []
        self.thumbnails = []

    def select_folder(self):
        # Open folder dialog to select an image folder
        folder_path = filedialog.askdirectory()
        if folder_path:
            # Get all image files in the folder
            self.image_files = [
                os.path.join(folder_path, f)
                for f in os.listdir(folder_path)
                if f.lower().endswith((".jpg", ".jpeg", ".png", ".bmp", ".gif"))
            ]
            if self.image_files:
                self.display_thumbnails()
            else:
                self.speak("No images found in the selected folder.")
                self.clear_gallery()
                tk.Label(
                    self.gallery_frame, text="No Images Found", fg="red"
                ).pack()

    def display_thumbnails(self):
        self.clear_gallery()

        # Create thumbnails for all images and display in a grid
        for index, file_path in enumerate(self.image_files):
            img = Image.open(file_path)
            img.thumbnail((100, 100))
            thumb = ImageTk.PhotoImage(img)
            self.thumbnails.append(thumb)

            btn = tk.Button(
                self.gallery_frame,
                image=thumb,
                command=lambda path=file_path: self.display_full_image(path),
            )
            btn.grid(row=index // 5, column=index % 5, padx=5, pady=5)

    def display_full_image(self, file_path):
        # Create a new window to display the full-size image
        full_image_window = tk.Toplevel(self.root)
        full_image_window.title("Full Image")

        img = Image.open(file_path)
        img.thumbnail((500, 500))
        full_img = ImageTk.PhotoImage(img)

        label = tk.Label(full_image_window, image=full_img)
        label.image = full_img  # Keep reference to avoid garbage collection
        label.pack()

        # Speak the name of the image
        self.speak_image_name(file_path)

    def clear_gallery(self):
        # Clear existing thumbnails
        for widget in self.gallery_frame.winfo_children():
            widget.destroy()
        self.thumbnails = []

    def speak_image_name(self, file_path):
        # Speak the image name
        image_name = os.path.splitext(os.path.basename(file_path))[0]
        self.speak(f"The image name is {image_name}")

    def speak(self, text):
        self.engine.say(text)
        self.engine.runAndWait()


# Create the application window
root = tk.Tk()
app = ImageGalleryApp(root)
root.mainloop()
