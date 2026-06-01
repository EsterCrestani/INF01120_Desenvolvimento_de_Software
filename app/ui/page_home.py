import customtkinter as ctk
from app.ui.constantes import COR_TITULO, COR_BOTAO_ESCURO


class PageHome(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller

        ctk.CTkLabel(
            self, text="Gerador de\nsequências\nmusicais",
            font=("Arial", 52, "bold"), text_color=COR_TITULO, justify="center"
        ).pack(pady=(60, 50))

        ctk.CTkButton(
            self, text="clique aqui para começar",
            font=("Arial", 17, "bold"), fg_color=COR_BOTAO_ESCURO,
            text_color="white", corner_radius=30, width=320, height=54,
            command=lambda: controller.show_frame("PageInput")
        ).pack(pady=10)

        ctk.CTkButton(
            self, text="Informações",
            font=("Arial", 14), fg_color="transparent",
            text_color=COR_TITULO, border_width=1, border_color=COR_TITULO,
            corner_radius=20, width=160, height=34,
            command=self._abrir_modal
        ).pack(pady=18)

    def _abrir_modal(self):
        modal = ctk.CTkToplevel(self)
        modal.title("Como funciona")
        modal.geometry("460x440")
        modal.configure(fg_color=COR_BOTAO_ESCURO)
        modal.transient(self.winfo_toplevel())
        modal.grab_set()

        ctk.CTkLabel(
            modal, text="Gerador de Sequências Musicais",
            font=("Arial", 18, "bold"), text_color=COR_TITULO
        ).pack(pady=(20, 5))

        ctk.CTkLabel(
            modal, text="Como funciona:",
            font=("Arial", 14, "bold"), text_color="white"
        ).pack(anchor="w", padx=24, pady=(10, 4))

        linhas = [
            "NOTAS: A a G = Lá a Sol  |  H = Si bemol  |  Mb = Mi bemol",
            "PAUSAS: a a h = Pausa/Silêncio",
            "OITAVAS: ? = Sobe oitava  |  V = Desce oitava",
            "TEMPO: > = Acelera BPM  |  < = Desacelera BPM",
            "INSTRUMENTOS: ! = Harmonica  |  ; = Tubular Bells  |  , = Church Organ",
            "O, I, U = Gaita de Foles  |  Espaço = Dobra volume",
            "ATRASO: [n] no início da linha = Voz entra n beats depois",
            "Consoantes não mapeadas repetem a nota anterior (ou pausa).",
        ]
        for linha in linhas:
            ctk.CTkLabel(
                modal, text="• " + linha,
                font=("Arial", 12), text_color="#d0e8f8",
                justify="left", wraplength=400, anchor="w"
            ).pack(anchor="w", padx=28, pady=1)

        ctk.CTkButton(
            modal, text="Fechar", fg_color=COR_TITULO,
            text_color=COR_BOTAO_ESCURO, width=100, corner_radius=20,
            command=modal.destroy
        ).pack(pady=20)
