"""Plain full-screen backdrop window for the demo recording (close with Escape or by killing the process)."""
import tkinter as tk
root = tk.Tk()
root.title("Erdamchi demo backdrop")
root.configure(bg="#1b1a2a")
root.attributes("-fullscreen", True)
root.bind("<Escape>", lambda e: root.destroy())
root.mainloop()
