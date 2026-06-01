import os
import customtkinter as ctk
from app.maestro import Maestro
from app.ui import PageHome, PageInput, PageConfig, PagePlaying, PageFinished
from app.ui.constantes import COR_FUNDO_JANELA, COR_FUNDO_CARD, COR_TEXTO_CINZA


class InterfaceApp:
    def __init__(self, root: ctk.CTk):
        self.root = root
        self.root.title("Gerador de Sequências Musicais")
        self.root.geometry("960x720")
        self.root.configure(fg_color=COR_FUNDO_JANELA)

        self.maestro = Maestro(callback_finalizacao=self.on_play_finished)
        self.caminho_midi_salvo = None

        self.container = ctk.CTkFrame(self.root, fg_color=COR_FUNDO_CARD, corner_radius=40)
        self.container.pack(fill="both", expand=True, padx=40, pady=40)

        ctk.CTkButton(
            self.container, text="Encerrar sessão",
            fg_color="transparent", text_color=COR_TEXTO_CINZA,
            hover_color="#f0f0f0", font=("Arial", 13),
            command=self.root.destroy, width=120
        ).place(relx=1.0, rely=0.0, anchor="ne", x=-15, y=12)

        self.frames = {}
        for F in (PageHome, PageInput, PageConfig, PagePlaying, PageFinished):
            frame = F(parent=self.container, controller=self)
            self.frames[F.__name__] = frame

        self.show_frame("PageHome")

    def show_frame(self, page_name: str):
        for frame in self.frames.values():
            frame.place_forget()
        frame = self.frames[page_name]
        frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.92, relheight=0.88)
        if hasattr(frame, "on_show"):
            frame.on_show()

    def on_play_finished(self):
        if not os.path.exists("saida"):
            os.makedirs("saida")
        self.caminho_midi_salvo = os.path.abspath("saida/arquivo.mid")
        self.maestro.gerador_midi.salvar(self.caminho_midi_salvo)
        self.root.after(0, lambda: self.show_frame("PageFinished"))
