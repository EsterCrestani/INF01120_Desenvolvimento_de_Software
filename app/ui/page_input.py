import customtkinter as ctk
from tkinter import filedialog, messagebox
from app.gerenciador_arquivo import GerenciadorArquivo
from app.ui.constantes import COR_TITULO, COR_BOTAO_ESCURO, COR_TEXTO_CINZA

COLUNAS_LEGENDA = [
    ("Notas Musicais:", [
        "A a G → Lá a Sol",
        "H → Si Bemol",
        "Mb → Mi Bemol",
        "a–h → Silêncio",
    ]),
    ("Volume:", [
        "+ / - → Volume +/-10",
    ]),
    ("Instrumentos:", [
        "! → Harmonica",
        "; → Tubular Bells",
        ", → Church Organ",
        "O, I, U → Gaita de Foles",
    ]),
    ("Oitavas:", [
        "? → Sobe oitava",
        "V → Desce oitava",
        "[n] → Atraso de n beats",
    ]),
    ("Especiais:", [
        "Consoantes não mapeadas geram silêncio",
    ]),
]


class PageInput(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller

        ctk.CTkLabel(
            self, text="Informe sua sequência musical:",
            font=("Arial", 22, "bold"), text_color=COR_BOTAO_ESCURO
        ).pack(pady=(16, 8))

        ctk.CTkButton(
            self, text="Carregue seu arquivo",
            font=("Arial", 18, "bold"), fg_color=COR_BOTAO_ESCURO,
            text_color="white", corner_radius=30, width=360, height=52,
            command=self._carregar
        ).pack(pady=6)

        ctk.CTkLabel(
            self, text="Ou edite aqui sua sequência",
            font=("Arial", 14, "bold"), text_color=COR_TITULO
        ).pack(pady=6)

        self.textbox = ctk.CTkTextbox(
            self, width=640, height=130, corner_radius=10,
            border_width=1, border_color="#cccccc", font=("Courier", 14)
        )
        self.textbox.pack(pady=6)
        self.textbox.insert("1.0", "[0] G A H C\n[4] D E F G")

        ctk.CTkButton(
            self, text="Avançar",
            font=("Arial", 20, "bold"), fg_color=COR_TITULO,
            text_color="white", corner_radius=30, width=260, height=52,
            command=self._avancar
        ).pack(pady=12)

        self._construir_legenda()

    def _construir_legenda(self):
        frame_leg = ctk.CTkFrame(
            self, fg_color="#f4f9fd",
            border_width=2, border_color=COR_TITULO, corner_radius=12
        )
        frame_leg.pack(fill="x", padx=16, pady=(4, 8))

        ctk.CTkLabel(
            frame_leg, text="Legenda:",
            font=("Arial", 14, "bold"), text_color=COR_BOTAO_ESCURO
        ).pack(anchor="nw", padx=14, pady=(8, 2))

        cols_frame = ctk.CTkFrame(frame_leg, fg_color="transparent")
        cols_frame.pack(fill="x", padx=14, pady=(0, 10))

        for titulo, itens in COLUNAS_LEGENDA:
            col = ctk.CTkFrame(cols_frame, fg_color="transparent")
            col.pack(side="left", fill="both", expand=True, padx=4, anchor="n")
            ctk.CTkLabel(
                col, text=titulo,
                font=("Arial", 12, "bold"), text_color=COR_BOTAO_ESCURO
            ).pack(anchor="w")
            for item in itens:
                ctk.CTkLabel(
                    col, text="• " + item,
                    font=("Arial", 10), text_color="#2c3e50",
                    justify="left", wraplength=130, anchor="w"
                ).pack(anchor="w")

    def _carregar(self):
        caminho = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if caminho:
            try:
                conteudo = GerenciadorArquivo.ler_arquivo_texto(caminho)
                self.textbox.delete("1.0", "end")
                self.textbox.insert("end", conteudo)
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao ler arquivo:\n{e}")

    def _avancar(self):
        texto = self.textbox.get("1.0", "end").strip()
        if not texto:
            messagebox.showwarning("Aviso", "A sequência não pode estar vazia.")
            return
        self.controller.maestro.preparar(texto)
        self.controller.show_frame("PageConfig")
