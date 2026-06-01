import customtkinter as ctk
from app.ui.constantes import COR_TITULO


class PageFinished(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller

        ctk.CTkLabel(
            self, text="Sua sequência\nencerrou!",
            font=("Arial", 52, "bold"), text_color=COR_TITULO, justify="center"
        ).pack(pady=(80, 40))

        self.lbl_caminho = ctk.CTkLabel(
            self,
            text="Seu arquivo .mid já está disponível em: saida/arquivo.mid",
            font=("Arial", 15, "bold"), text_color=COR_TITULO, wraplength=600
        )
        self.lbl_caminho.pack(pady=16)

        ctk.CTkButton(
            self, text="Fazer Nova Sequência",
            font=("Arial", 16, "bold"), fg_color="transparent",
            text_color=COR_TITULO, border_width=2, border_color=COR_TITULO,
            corner_radius=20, width=260, height=44,
            command=lambda: controller.show_frame("PageHome")
        ).pack(pady=40)

    def on_show(self):
        if self.controller.caminho_midi_salvo:
            self.lbl_caminho.configure(
                text=f"Seu arquivo .mid já está disponível em:\n{self.controller.caminho_midi_salvo}"
            )
