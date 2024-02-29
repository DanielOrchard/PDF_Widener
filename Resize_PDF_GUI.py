import tkinter as tk
from tkinter import font, Scale, Checkbutton, IntVar, Button, messagebox, Label
from PIL import Image, ImageTk
from tkinterdnd2 import DND_FILES, TkinterDnD
import resize_pdf  # Ensure this script is in the same directory or adjust the import path
import os
import re

def update_layout(event=None):
    root.update_idletasks()
    global bg_photo, bg_image

    window_width = root.winfo_width()
    # window_height = root.winfo_height()
    window_height = root.winfo_height() - hbox.winfo_reqheight() - checkbox.winfo_reqheight() - 0


    if window_height > 1 and window_width > 1:
            # Calculate new dimensions maintaining the aspect ratio
            if window_width > window_height:
                # Window is wider than it is tall
                new_height = window_height
                new_width = new_height  # Square image maintains aspect ratio
            else:
                # Window is taller than it is wide
                new_width = window_width
                new_height = new_width  # Square image maintains aspect ratio

            resized_bg_image = bg_image.resize((new_width, new_height), Image.LANCZOS)
            bg_photo = ImageTk.PhotoImage(resized_bg_image)
            canvas.itemconfig(bg_image_on_canvas, image=bg_photo)
            canvas.image = bg_photo  # Update the reference

            # Center the image on the canvas
            canvas.coords(bg_image_on_canvas, (window_width - new_width) / 2, (window_height - new_height) / 2)

def on_processing_complete(created_filepath):
    message = "Success! Created Files:\n\n"
    print(created_filepath)
    # Iterate over filepaths and append filenames to the message
    for filepath in created_filepath:
        directory_path = os.path.dirname(filepath)
        filename = os.path.basename(filepath)
        message += f"{filename}\n"

    # Add directory path to the end of the message
    message += f"\nYou can find them at: {directory_path}"

    # Display the message box
    messagebox.showinfo("Processing Complete", message)


def on_drop(event):
    # Splitting the event data by lines in case multiple files are dropped
   
    file_paths = re.findall(r'\{.*?\}', event.data)
    file_paths = [path.strip('{}') for path in file_paths]  # Remove curly braces
    print("Extracted file paths:", file_paths)  # Check the extracted paths

    created_files = []
    for file_path_raw in file_paths:
        # Stripping any whitespace and quotes from each file path
        file_path = file_path_raw.strip().replace('"', '').replace('{', '').replace('}', '')
        print(file_path)

        # Check if the file path ends with '.pdf'
        if file_path.lower().endswith('.pdf'):
            # Normalize the file path to remove any irregularities
            normalized_file_path = os.path.normpath(file_path)
            print(f"Add Lines = {checkbox_var.get()}")
            print(normalized_file_path)
            output_file = resize_pdf.resize_from_gui(normalized_file_path, scale.get(), checkbox_var.get())
            if (output_file):
                created_files.append(output_file)
                
        else:
            print(f"Skipped non-PDF file: {file_path}")
    
    on_processing_complete(created_files)

def reset_scale():
    scale.set(1.75)  # Reset the slider to 1.75

root = TkinterDnD.Tk()
root.title('PDF Resizer')
window_width = 500
window_height = 500
root.geometry(f'{window_width}x{window_height}')  # Adjust size as needed

# Load and resize the background image
bg_image_path = os.path.join("assets", "images", "bg.png")
bg_image = Image.open(bg_image_path)
bg_photo = ImageTk.PhotoImage(bg_image)

# Create a canvas for the background and the drag-and-drop text
canvas = tk.Canvas(root)
canvas.pack(fill="both", expand=True)
bg_image_on_canvas = canvas.create_image(0, 0, image=bg_photo, anchor="nw")
canvas.image = bg_photo  # Keep a reference to avoid garbage collection

# Define font
customFont = font.Font(family="Helvetica", size=16, weight="bold")
funFont = font.Font(family="Comic Sans MS", size=14, weight="bold")
checkboxFont = font.Font(family="Helvetica", size=12)  # Larger font for checkbox

# Add drag-and-drop instructions to the canvas
canvas.create_text(window_width / 2, 30, text='"Drop your PDFs on Me!"', fill="#404040", font=funFont)

hbox = tk.Frame(root)
hbox.pack(side=tk.BOTTOM, pady=5)

# Slider Label
slider_label = Label(hbox, text="Space Scale:", font=funFont)
slider_label.pack(side=tk.LEFT, padx=5, anchor="s")

# Slider
scale = Scale(hbox, from_=1, to=3, font=funFont, resolution=0.01, orient=tk.HORIZONTAL, length=220)
scale.set(1.75)  # Default value
scale.pack(side=tk.LEFT, padx=5, anchor="s")

# Reset Button
reset_button = Button(hbox, text="Reset", font=funFont, command=lambda: scale.set(1.75))
reset_button.pack(side=tk.LEFT, padx=5, anchor="s")

# Checkbox
checkbox_var = IntVar(value=1)
checkbox = Checkbutton(root, text="Add Lines", variable=checkbox_var, font=funFont)
checkbox.pack(side=tk.BOTTOM, pady=1)

# Bind the drop event to the canvas instead of root
canvas.drop_target_register(DND_FILES)
canvas.dnd_bind('<<Drop>>', on_drop)

# Bind the resize event
root.bind("<Configure>", update_layout)

update_layout()

# Run the application
root.mainloop()
