import customtkinter as ctk
from app.ui.constantes import (
    COR_BOTAO_ESCURO, COR_TEXTO_CINZA, COR_FUNDO_VOZ,
    IDS_MIDI, NOMES_OPT
)


class PageConfig(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller

        ctk.CTkLabel(
            self, text="Configurações Iniciais:",
            font=("Arial", 24, "bold"), text_color=COR_BOTAO_ESCURO
        ).pack(pady=(12, 6))

        card = ctk.CTkFrame(self, fg_color=COR_FUNDO_VOZ, corner_radius=20)
        card.pack(fill="both", expand=True, padx=10, pady=(0, 8))

        self.scroll = ctk.CTkScrollableFrame(card, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=12, pady=12)

        barra = ctk.CTkFrame(self, fg_color="transparent")
        barra.pack(fill="x", pady=(0, 6))

        ctk.CTkButton(
            barra, text="← Voltar",
            font=("Arial", 14), fg_color="transparent",
            text_color=COR_TEXTO_CINZA, border_width=1, border_color="#cccccc",
            corner_radius=20, width=100, height=38,
            command=lambda: controller.show_frame("PageInput")
        ).pack(side="left", padx=16)

        ctk.CTkButton(
            barra, text="🔊  Tocar",
            font=("Arial", 18, "bold"), fg_color=COR_BOTAO_ESCURO,
            text_color="white", corner_radius=30, width=200, height=48,
            command=self._tocar
        ).pack(side="right", padx=16)

    def on_show(self):
        for w in self.scroll.winfo_children():
            w.destroy()
        for voz in self.controller.maestro.partitura.get_vozes():
            self._criar_linha_voz(voz)

    def _criar_linha_voz(self, voz):
        bloco = ctk.CTkFrame(self.scroll, fg_color="transparent")
        bloco.pack(fill="x", pady=6)

        ctk.CTkLabel(
            bloco, text=f"Voz {voz.id_voz + 1}",
            font=("Arial", 15, "bold"), text_color=COR_BOTAO_ESCURO
        ).pack()

        linha = ctk.CTkFrame(bloco, fg_color="transparent")
        linha.pack()

        inst_atual = voz.instrumento_atual
        idx = IDS_MIDI.index(inst_atual) if inst_atual in IDS_MIDI else 0
        self._dropdown(linha, "Instrumento:", NOMES_OPT, NOMES_OPT[idx],
                       lambda val, v=voz: setattr(v, "instrumento_atual",
                                                  IDS_MIDI[NOMES_OPT.index(val)]))

        oitavas = [f"Oitava {i}" for i in range(1, 10)]
        self._dropdown(linha, "Oitava:", oitavas, f"Oitava {voz.oitava_base}",
                       lambda val, v=voz: setattr(v, "oitava_atual",
                                                  int(val.replace("Oitava ", ""))))

        self._seta(linha, "Andamento:", f"{self.controller.maestro.bpm} BPM",
                   lambda lbl: self._alt_bpm(-10, lbl),
                   lambda lbl: self._alt_bpm(+10, lbl))

        self._seta(linha, "Volume:", str(voz.volume_atual),
                   lambda lbl, v=voz: self._alt_vol(v, -10, lbl),
                   lambda lbl, v=voz: self._alt_vol(v, +10, lbl))

    def _dropdown(self, parent, titulo, valores, inicial, cmd):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.pack(side="left", padx=8)
        ctk.CTkLabel(f, text=titulo, font=("Arial", 11, "bold"),
                     text_color="white").pack(anchor="w")
        opt = ctk.CTkOptionMenu(f, values=valores,
                                fg_color=COR_BOTAO_ESCURO,
                                button_color=COR_BOTAO_ESCURO,
                                width=140, font=("Arial", 11), command=cmd)
        opt.set(inicial)
        opt.pack()

    def _seta(self, parent, titulo, inicial, cmd_menos, cmd_mais):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.pack(side="left", padx=8)
        ctk.CTkLabel(f, text=titulo, font=("Arial", 11, "bold"),
                     text_color="white").pack(anchor="w")
        row = ctk.CTkFrame(f, fg_color=COR_BOTAO_ESCURO, corner_radius=8)
        row.pack()
        lbl = ctk.CTkLabel(row, text=inicial, text_color="white", width=80,
                           font=("Arial", 12))
        ctk.CTkButton(row, text="◄", width=28, height=28,
                      fg_color="transparent", hover_color="#302070",
                      font=("Arial", 10),
                      command=lambda: cmd_menos(lbl)).pack(side="left")
        lbl.pack(side="left")
        ctk.CTkButton(row, text="►", width=28, height=28,
                      fg_color="transparent", hover_color="#302070",
                      font=("Arial", 10),
                      command=lambda: cmd_mais(lbl)).pack(side="left")

    def _alt_bpm(self, delta, lbl):
        novo = max(10, self.controller.maestro.bpm + delta)
        self.controller.maestro.bpm = novo
        lbl.configure(text=f"{novo} BPM")

    def _alt_vol(self, voz, delta, lbl):
        novo = max(0, min(127, voz.volume_atual + delta))
        voz.volume_atual = novo
        lbl.configure(text=str(novo))

    def _tocar(self):
        self.controller.maestro.tocar()
        self.controller.show_frame("PagePlaying")
