import customtkinter as ctk
from app.interface import InterfaceApp

def main():
    root = ctk.CTk()
    app = InterfaceApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
