import os
import warnings

import customtkinter as ctk  # pyright: ignore[reportMissingTypeStubs], usado conforme documentação

from app.interface import InterfaceApp

# Suprime o banner do pygame e o aviso de pkg_resources
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
warnings.filterwarnings("ignore", category=UserWarning, module="pygame")

def main():
    root = ctk.CTk()
    InterfaceApp(root)

    root.mainloop()

if __name__ == "__main__":
    main()
