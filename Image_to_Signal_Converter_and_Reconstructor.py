import cv2
import numpy as np
import matplotlib.pyplot as plt
from tkinter import Tk, Label, Button, Frame, filedialog, messagebox
from PIL import Image, ImageTk
import tkinter.simpledialog as sd
import os

# Global Variables
img = None
signal_normalized = None
img_shape = None

# Resizing Image to fit within 400x400 box (keeping aspect ratio)
def resize_to_fit(image, max_size=(400, 400)):
    h, w = image.shape[:2]
    max_w, max_h = max_size
    scale = min(max_w / w, max_h / h)
    new_w, new_h = int(w * scale), int(h * scale)
    resized_img = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)
    return resized_img

# Loading Image
def load_image():
    global img, img_shape
    filetypes = [("Image files", "*.jpg *.jpeg *.png *.bmp *.tif")]
    file_path = filedialog.askopenfilename(title="Select an Image", filetypes=filetypes)

    if file_path:
        img = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            messagebox.showerror("Error", "Could not load image. Try a different format.")
            return

        img_shape = img.shape  # store for reconstruction

        # Resize image to fit display (preserve aspect ratio)
        display_img = resize_to_fit(img, (400, 400))

        # Convert to tkinter image and show
        imgtk = ImageTk.PhotoImage(Image.fromarray(display_img))
        label_img.config(image=imgtk)
        label_img.image = imgtk

        label_status.config(text=f"Loaded image: {os.path.basename(file_path)} ({img_shape[0]}x{img_shape[1]})")
    else:
        messagebox.showwarning("Warning", "No image selected.")

# Converting Image into 1D Signal
def convert_to_signal():
    global img, signal_normalized

    if img is None:
        messagebox.showwarning("Warning", "Please load an image first.")
        return

    # Flatten and normalize
    signal = img.flatten()
    signal_normalized = signal / 255.0

    # Plot waveform
    plt.figure(figsize=(8, 4))
    plt.plot(signal_normalized, color='blue')
    plt.title("1D Signal Representation of Image")
    plt.xlabel("Sample Index")
    plt.ylabel("Amplitude (Normalized Pixel Intensity)")
    plt.grid(True)
    plt.show()

    label_status.config(text=f"Signal generated: {len(signal_normalized)} samples")
    messagebox.showinfo("Success", "Image successfully converted into 1D signal!")

# Saving Signal as CSV
def save_signal():
    global signal_normalized, img_shape

    if signal_normalized is None:
        messagebox.showwarning("Warning", "No signal found. Please convert an image first.")
        return

    file_path = filedialog.asksaveasfilename(
        defaultextension=".csv", filetypes=[("CSV files", "*.csv")], title="Save 1D Signal"
    )

    if file_path:
        # Save both shape and signal (for later reconstruction)
        np.savetxt(file_path, signal_normalized, delimiter=",")
        shape_path = file_path.replace(".csv", "_shape.txt")
        with open(shape_path, "w") as f:
            f.write(f"{img_shape[0]},{img_shape[1]}")

        label_status.config(text=f"Signal saved: {file_path}")
        messagebox.showinfo("Saved", f"Signal saved successfully!\n\nFile: {file_path}")
    else:
        messagebox.showwarning("Cancelled", "Signal save cancelled.")

# Loading CSV and Reconstructing Image
def load_and_reconstruct():
    global signal_normalized

    # Select the CSV file
    file_path = filedialog.askopenfilename(title="Select Signal CSV", filetypes=[("CSV files", "*.csv")])
    if not file_path:
        return

    try:
        # Load the saved signal
        loaded_signal = np.loadtxt(file_path, delimiter=",")

        # Try to load stored shape file
        shape_path = file_path.replace(".csv", "_shape.txt")
        if os.path.exists(shape_path):
            with open(shape_path, "r") as f:
                shape_str = f.read().strip().split(",")
                height, width = int(shape_str[0]), int(shape_str[1])
        else:
            # Ask user if shape not found
            height = sd.askinteger("Image Height", "Enter image height (pixels):")
            width = sd.askinteger("Image Width", "Enter image width (pixels):")

        # Reconstruct the image
        reconstructed_signal = loaded_signal * 255
        reconstructed_image = reconstructed_signal.reshape((height, width)).astype(np.uint8)

        # Resize for display
        display_reconstructed = resize_to_fit(reconstructed_image, (400, 400))

        # Display reconstructed image
        imgtk = ImageTk.PhotoImage(Image.fromarray(display_reconstructed))
        label_reconstructed.config(image=imgtk)
        label_reconstructed.image = imgtk

        label_status.config(text=f"Reconstructed image ({height}x{width})")
        messagebox.showinfo("Reconstruction Complete", "Image successfully reconstructed from CSV!")

    except Exception as e:
        messagebox.showerror("Error", f"Failed to reconstruct image:\n{e}")

# Tkinter GUI Setup
root = Tk()
root.title("Image ↔ Signal Converter & Reconstructor")
root.geometry("1280x720")
root.configure(bg="#BFBFBF")

Label(root, text="Image to Signal Converter and Reconstructor", font=("Calibri", 18, "bold"), bg="#BFBFBF").pack(pady=10)

Button(root, text="Load Image", command=load_image, font=("Calibri", 12), bg="#ECECEC", fg="black", width=25).pack(pady=8)
Button(root, text="Convert into Signal", command=convert_to_signal, font=("Calibri", 12), bg="#ECECEC", fg="black", width=25).pack(pady=8)
Button(root, text="Save Signal (CSV)", command=save_signal, font=("Calibri", 12), bg="#ECECEC", fg="black", width=25).pack(pady=8)
Button(root, text="Load CSV & Reconstruct Image", command=load_and_reconstruct, font=("Calibri", 12), bg="#ECECEC", fg="black", width=25).pack(pady=8)

# Side-by-side layout for Original & Reconstructed images
image_frame = Frame(root, bg="#BFBFBF")
image_frame.pack(pady=20, anchor="center")

# Left side (Original Image)
left_frame = Frame(image_frame, bg="#BFBFBF", width=400, height=400)
left_frame.pack(side="left", padx=40)
left_frame.pack_propagate(False)

Label(left_frame, text="Original Image", bg="#f0f0f0", font=("Calibri", 13, "bold")).pack(pady=4)
label_img = Label(left_frame, bg="#e0e0e0", width=400, height=400)
label_img.pack(pady=5)

# Right side (Reconstructed Image)
right_frame = Frame(image_frame, bg="#BFBFBF", width=400, height=400)
right_frame.pack(side="left", padx=40)
right_frame.pack_propagate(False)

Label(right_frame, text="Reconstructed Image", bg="#f0f0f0", font=("Calibri", 13, "bold")).pack(pady=4)
label_reconstructed = Label(right_frame, bg="#e0e0e0", width=400, height=400)
label_reconstructed.pack(pady=5)

label_status = Label(root, text="Status: Ready", font=("Calibri", 12, "bold"), bg="#f0eeee", fg="black")
label_status.pack(pady=10)

root.mainloop()
