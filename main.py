import os
import warnings

# Suprime o banner do pygame e o aviso de pkg_resources
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
warnings.filterwarnings("ignore", category=UserWarning, module="pygame")

import customtkinter as ctk
from app.interface import InterfaceApp

def main():
    root = ctk.CTk()
    app = InterfaceApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
