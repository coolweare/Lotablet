import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import pyttsx3
import os
import threading
from twilio.rest import Client


class ImageGalleryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Londyn's App")
        self.root.geometry("900x700")
        self.root.configure(bg="#f4f4f4")  # Light background color

        # Initialize text-to-speech engine
        self.engine = pyttsx3.init()

        # Configure text-to-speech engine
        self.engine.setProperty('rate', 150)  # Set speech rate
        self.engine.setProperty('volume', 0.9)  # Set volume

        # Select US English female voice
        voices = self.engine.getProperty('voices')
        for voice in voices:
            if "en_US" in voice.languages and "female" in voice.name.lower():
                self.engine.setProperty('voice', voice.id)
                break

        # Twilio Configuration
        self.twilio_account_sid = "your_account_sid"  # Replace with your Account SID
        self.twilio_auth_token = "your_auth_token"    # Replace with your Auth Token
        self.twilio_phone_number = "+1234567890"      # Replace with your Twilio phone number
        self.target_phone_number = "+0987654321"      # Replace with the recipient's phone number

        # Create a frame for navigation buttons
        self.nav_frame = tk.Frame(root, bg="#e0e0e0", pady=10)
        self.nav_frame.grid(row=0, column=0, columnspan=3, sticky="ew")

        # Create a frame for the gallery
        self.gallery_frame = tk.Frame(root, bg="#ffffff", bd=2, relief=tk.GROOVE)
        self.gallery_frame.grid(row=1, column=0, columnspan=3, sticky="nsew")

        # Configure grid weights for dynamic resizing
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Load button images
        self.home_icon = self.load_icon("/home/ubuntu/lotab/img/buttons/home_icon.jpeg")  # Replace with your home icon path
        self.yes_icon = self.load_icon("/home/ubuntu/lotab/img/buttons/yes_icon.png")    # Replace with your yes icon path
        self.no_icon = self.load_icon("/home/ubuntu/lotab/img/buttons/no_icon.jpeg")      # Replace with your no icon path
        self.sms_icon = self.load_icon("/home/ubuntu/lotab/img/buttons/sms_icon.png")    # Replace with your SMS icon path
        self.sick_icon = self.load_icon("/home/ubuntu/lotab/img/buttons/sick_icon.jpeg")  # Replace with your sick icon path

        # Navigation buttons
        self.home_button = tk.Button(
            self.nav_frame, image=self.home_icon, command=self.load_main_folder,
            bg="#4CAF50", fg="white", font=("Arial", 12, "bold"), padx=10, pady=5
        )
        self.home_button.grid(row=0, column=0, padx=10)

        self.yes_button = tk.Button(
            self.nav_frame, image=self.yes_icon, command=self.on_yes_clicked,
            bg="#4CAF50", fg="white", font=("Arial", 12, "bold"), padx=10, pady=5
        )
        self.yes_button.grid(row=0, column=1, padx=10)

        self.no_button = tk.Button(
            self.nav_frame, image=self.no_icon, command=self.on_no_clicked,
            bg="#F44336", fg="white", font=("Arial", 12, "bold"), padx=10, pady=5
        )
        self.no_button.grid(row=0, column=2, padx=10)

        self.sick_button = tk.Button(
            self.nav_frame, image=self.sick_icon, command=self.load_sick_folder,
            bg="#2196F3", padx=10, pady=5
        )
        self.sick_button.grid(row=0, column=3, padx=10)

        self.sms_button = tk.Button(
            self.nav_frame, image=self.sms_icon, command=self.send_sms,
            bg="#FF9800", fg="white", font=("Arial", 12, "bold"), padx=10, pady=5
        )
        self.sms_button.grid(row=0, column=4, padx=10)

        self.image_files = []
        self.thumbnails = []

        # Main folder and Sick folder paths
        self.main_folder = "/home/ubuntu/lotab/img/"  # Replace with your main folder path
        self.sick_folder = "/home/ubuntu/lotab/img/sick"  # Subfolder for sick images

        # Current folder (used to determine speech output)
        self.current_folder = self.main_folder

        # Load main folder on startup
        self.load_main_folder()

    def load_icon(self, path):
        """Load an image for a button."""
        try:
            icon = Image.open(path)
            icon.thumbnail((50, 50))  # Resize to fit button
            return ImageTk.PhotoImage(icon)
        except Exception as e:
            print(f"Error loading icon from {path}: {e}")
            return None

    def load_folder(self, folder_path):
        self.current_folder = folder_path  # Update current folder
        if os.path.exists(folder_path):
            # Get all image files in the folder
            self.image_files = [
                os.path.join(folder_path, f)
                for f in os.listdir(folder_path)
                if f.lower().endswith((".jpg", ".jpeg", ".png", ".bmp", ".gif"))
            ]

            # Check if the folder contains any image files
            if self.image_files:
                self.display_thumbnails()
            else:
                # Notify if no images are found
                self.clear_gallery()
                tk.Label(
                    self.gallery_frame, text="No Images Found in the Folder",
                    fg="red", font=("Arial", 14), bg="#ffffff"
                ).pack()
        else:
            # Notify if the folder does not exist
            self.clear_gallery()
            tk.Label(
                self.gallery_frame, text="Folder Not Found",
                fg="red", font=("Arial", 14), bg="#ffffff"
            ).pack()

    def load_main_folder(self):
        # Load the main folder
        self.load_folder(self.main_folder)

    def load_sick_folder(self):
        # Load the sick folder
        self.load_folder(self.sick_folder)

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
                command=lambda path=file_path: self.speak_image_name(path),
                bg="#ffffff"
            )
            btn.grid(row=index // 5, column=index % 5, padx=10, pady=10)

    def clear_gallery(self):
        # Clear existing thumbnails
        for widget in self.gallery_frame.winfo_children():
            widget.destroy()
        self.thumbnails = []

    def speak_image_name(self, file_path):
        # Extract the image name
        image_name = os.path.splitext(os.path.basename(file_path))[0]
        print(f"Image Name: {image_name}")  # Debug: Print the image name

        # Custom speech output based on folder
        if self.current_folder == self.sick_folder:
            speech_text = f"MY {image_name} hurts"
        else:
            speech_text = f"Please {image_name}"

        print(f"Speaking: {speech_text}")  # Debug: Print the speech text
        self.speak(speech_text)

    def preprocess_text(self, text):
        # Replace problematic words with synonyms or phonetic spellings
        substitutions = {
            #"bath": "Take a Bath",  # Synonym
            "water": "waw-ter",  # Phonetic spelling
        }
        for word, replacement in substitutions.items():
            text = text.replace(word, replacement)
        return text

    def speak(self, text):
        # Preprocess text before speaking
        text = self.preprocess_text(text)
        threading.Thread(target=self._speak, args=(text,)).start()

    def _speak(self, text):
        try:
            print(f"Speaking (processed): {text}")
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            print(f"Error in speech synthesis: {e}")
            messagebox.showerror("Speech Error", f"Could not say: {text}")


    def send_sms(self):
        # Send an SMS using Twilio
        try:
            client = Client(self.twilio_account_sid, self.twilio_auth_token)
            message = client.messages.create(
                body="Hello, this is a test SMS from the Image Gallery App!",
                from_=self.twilio_phone_number,
                to=self.target_phone_number
            )
            messagebox.showinfo("SMS Sent", f"Message sent successfully! SID: {message.sid}")
        except Exception as e:
            messagebox.showerror("SMS Error", f"Failed to send SMS: {e}")

    def on_yes_clicked(self):
        # Action for Yes button
        speech_text = f"Yes Please"
        self.speak(speech_text)
        messagebox.showinfo("Response", "You clicked Yes!")

    def on_no_clicked(self):
        # Action for No button
        speech_text = f"No Thank you"
        self.speak(speech_text)
        messagebox.showinfo("Response", "You clicked No!")


# Create the application window
root = tk.Tk()
app = ImageGalleryApp(root)
root.mainloop()
