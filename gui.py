import tkinter as tk
from tkinter import messagebox

SHOW_INFO = True

def show_info(title: str, message: str) -> None:
    """
    Displays an informational message box.

    Args:
        title (str): The title of the message box.
        message (str): The message to display.
    """
    if not SHOW_INFO:
        return

    root = tk.Tk()
    root.withdraw()  # Hide the main window
    messagebox.showinfo(title, message)
    root.destroy()


def show_error(title: str, message: str) -> None:
    """
    Displays an error message box.

    Args:
        title (str): The title of the message box.
        message (str): The error message to display.
    """
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    messagebox.showerror(title, message)
    root.destroy()