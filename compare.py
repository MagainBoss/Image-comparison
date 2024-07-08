import tkinter as tk
from tkinter import filedialog
from tkinterdnd2 import DND_FILES, TkinterDnD
from PIL import Image, ImageTk
import cv2

MAX_DISPLAY_SIZE = 500


def resize_image(img, max_size):
    height, width = img.shape[:2]
    if width > max_size or height > max_size:
        scaling_factor = min(max_size / width, max_size / height)
        new_width = int(width * scaling_factor)
        new_height = int(height * scaling_factor)
        img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_AREA)
    return img, width, height


def open_image(canvas, label_info, file_path=None):
    if not file_path:
        file_path = filedialog.askopenfilename()
    if file_path:
        img = cv2.imread(file_path)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # Resize image to fit within MAX_DISPLAY_SIZE
        img_rgb, width, height = resize_image(img_rgb, MAX_DISPLAY_SIZE)

        img_pil = Image.fromarray(img_rgb)
        img_tk = ImageTk.PhotoImage(img_pil)

        canvas.create_image(0, 0, anchor=tk.NW, image=img_tk)
        canvas.image = img_tk
        canvas.file_path = file_path
        canvas.img_cv = img
        label_info.config(text=f"{file_path}\nResolution: {width}x{height}")


def compare_images():
    img1 = canvas_left.img_cv
    img2 = canvas_right.img_cv

    if img1 is None or img2 is None:
        return

    img1_gray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    img2_gray = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

    # Resize images to the same size if needed
    if img1_gray.shape != img2_gray.shape:
        img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
        img2_gray = cv2.resize(img2_gray, (img1_gray.shape[1], img1_gray.shape[0]))

    diff = cv2.absdiff(img1_gray, img2_gray)
    _, thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(img1, contours, -1, (0, 0, 255), 2)
    cv2.drawContours(img2, contours, -1, (0, 0, 255), 2)
    img1_rgb = cv2.cvtColor(img1, cv2.COLOR_BGR2RGB)
    img2_rgb = cv2.cvtColor(img2, cv2.COLOR_BGR2RGB)
    thresh = cv2.cvtColor(thresh, cv2.COLOR_GRAY2RGB)
    img1_rgb, _, __ = resize_image(img1_rgb, MAX_DISPLAY_SIZE)
    img2_rgb, _, __ = resize_image(img2_rgb, MAX_DISPLAY_SIZE)
    thresh, _, __ = resize_image(thresh, MAX_DISPLAY_SIZE)
    img1_pil = Image.fromarray(img1_rgb)
    img2_pil = Image.fromarray(img2_rgb)
    thresh_pil = Image.fromarray(thresh)
    img1_tk = ImageTk.PhotoImage(img1_pil)
    img2_tk = ImageTk.PhotoImage(img2_pil)
    thresh_tk = ImageTk.PhotoImage(thresh_pil)
    canvas_left.delete("all")
    canvas_left.create_image(0, 0, anchor=tk.NW, image=img1_tk)
    canvas_left.image = img1_tk
    canvas_right.delete("all")
    canvas_right.create_image(0, 0, anchor=tk.NW, image=img2_tk)
    canvas_right.image = img2_tk
    canvas_result.delete("all")
    canvas_result.create_image(0, 0, anchor=tk.NW, image=thresh_tk)
    canvas_result.image = thresh_tk


def reset_images():
    canvas_left.delete("all")
    canvas_right.delete("all")
    canvas_result.delete("all")
    label_info_left.config(text="")
    label_info_right.config(text="")


def drop(event, canvas, label_info):
    file_path = event.data
    if file_path.startswith("{") and file_path.endswith("}"):
        file_path = file_path[1:-1]
    open_image(canvas, label_info, file_path)


root = TkinterDnD.Tk()
root.title("Image Comparison Tool")
root.state("zoomed")  # Start maximized

# Create frames for layout
frame_left = tk.Frame(root, bd=2, relief="solid")
frame_left.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)

frame_right = tk.Frame(root, bd=2, relief="solid")
frame_right.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.BOTH, expand=True)

frame_buttons = tk.Frame(root)
frame_buttons.pack(side=tk.BOTTOM, pady=10)

frame_result = tk.Frame(root, bd=2, relief="solid")
frame_result.pack(side=tk.BOTTOM, padx=10, pady=10, fill=tk.BOTH, expand=True)

# Left Image
canvas_left = tk.Canvas(
    frame_left, width=MAX_DISPLAY_SIZE, height=MAX_DISPLAY_SIZE, bg="white"
)
canvas_left.pack(fill=tk.BOTH, expand=True)
btn_load_left = tk.Button(
    frame_left, text="Load", command=lambda: open_image(canvas_left, label_info_left)
)
btn_load_left.pack()
label_info_left = tk.Label(frame_left, text="", justify="left")
label_info_left.pack()
canvas_left.drop_target_register(DND_FILES)
canvas_left.dnd_bind(
    "<<Drop>>", lambda event: drop(event, canvas_left, label_info_left)
)


# Right Image
canvas_right = tk.Canvas(
    frame_right, width=MAX_DISPLAY_SIZE, height=MAX_DISPLAY_SIZE, bg="white"
)
canvas_right.pack(fill=tk.BOTH, expand=True)
btn_load_right = tk.Button(
    frame_right, text="Load", command=lambda: open_image(canvas_right, label_info_right)
)
btn_load_right.pack()
label_info_right = tk.Label(frame_right, text="", justify="left")
label_info_right.pack()
canvas_right.drop_target_register(DND_FILES)
canvas_right.dnd_bind(
    "<<Drop>>", lambda event: drop(event, canvas_right, label_info_right)
)

# Result Difference
canvas_result = tk.Canvas(
    frame_result, width=MAX_DISPLAY_SIZE, height=MAX_DISPLAY_SIZE, bg="white"
)
canvas_result.pack(fill=tk.BOTH, expand=True)

# Buttons
btn_compare = tk.Button(frame_buttons, text="Compare", command=compare_images)
btn_compare.pack(side=tk.LEFT, padx=5)
btn_reset = tk.Button(frame_buttons, text="Reset", command=reset_images)
btn_reset.pack(side=tk.LEFT, padx=5)

root.mainloop()
