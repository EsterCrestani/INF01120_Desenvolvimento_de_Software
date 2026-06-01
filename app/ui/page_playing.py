import customtkinter as ctk
from app.ui.constantes import COR_BOTAO_ESCURO, COR_FUNDO_VOZ, NOMES_MIDI


class PagePlaying(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self._polling = False
        self._labels  = {}  # {id_voz: {campo: CTkLabel}}

        ctk.CTkLabel(
            self, text="🔊  Tocando...",
            font=("Arial", 22, "bold"), text_color=COR_BOTAO_ESCURO
        ).pack(pady=(12, 4))

        card = ctk.CTkFrame(self, fg_color=COR_FUNDO_VOZ, corner_radius=20)
        card.pack(fill="both", expand=True, padx=10, pady=(0, 8))

        ctk.CTkLabel(
            card, text="Estado das Vozes em Tempo Real",
            font=("Arial", 18, "bold"), text_color=COR_BOTAO_ESCURO
        ).pack(pady=(12, 4))

        self.scroll = ctk.CTkScrollableFrame(card, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=12, pady=4)

        barra = ctk.CTkFrame(self, fg_color="transparent")
        barra.pack(fill="x", pady=(0, 6))

        ctk.CTkButton(
            barra, text="■  Parar",
            font=("Arial", 18, "bold"), fg_color="#8b0000",
            text_color="white", corner_radius=30, width=200, height=48,
            command=self._parar
        ).pack()

    def on_show(self):
        for w in self.scroll.winfo_children():
            w.destroy()
        self._labels.clear()
        for voz in self.controller.maestro.vozes:
            self._criar_card_voz(voz)
        self._polling = True
        self._poll()

    def _criar_card_voz(self, voz):
        bloco = ctk.CTkFrame(self.scroll, fg_color="#daeaf5", corner_radius=12)
        bloco.pack(fill="x", pady=6, padx=4)

        header = ctk.CTkFrame(bloco, fg_color="transparent")
        header.pack(fill="x", padx=10, pady=(8, 2))

        ctk.CTkLabel(
            header, text=f"Voz {voz.id_voz + 1}",
            font=("Arial", 15, "bold"), text_color=COR_BOTAO_ESCURO
        ).pack(side="left")

        lbl_status = ctk.CTkLabel(
            header, text="⏳ Aguardando...",
            font=("Arial", 12), text_color="#888888"
        )
        lbl_status.pack(side="right")

        linha = ctk.CTkFrame(bloco, fg_color="transparent")
        linha.pack(padx=10, pady=(2, 10))

        def campo(parent, titulo):
            f = ctk.CTkFrame(parent, fg_color="transparent")
            f.pack(side="left", padx=10)
            ctk.CTkLabel(f, text=titulo, font=("Arial", 10, "bold"),
                         text_color="#555555").pack(anchor="w")
            lbl = ctk.CTkLabel(f, text="—", font=("Arial", 13, "bold"),
                               text_color=COR_BOTAO_ESCURO)
            lbl.pack(anchor="w")
            return lbl

        self._labels[voz.id_voz] = {
            "status":      lbl_status,
            "nota":        campo(linha, "🎵 Nota Atual:"),
            "oitava":      campo(linha, "🎼 Oitava:"),
            "instrumento": campo(linha, "🎸 Instrumento:"),
            "volume":      campo(linha, "🔊 Volume:"),
            "bpm":         campo(linha, "⏱️ BPM:"),
        }

    def _poll(self):
        if not self._polling:
            return
        maestro = self.controller.maestro
        if not maestro.vozes:
            return
        for voz in maestro.vozes:
            lbls = self._labels.get(voz.id_voz)
            if not lbls:
                continue
            if not voz.has_next():
                lbls["status"].configure(text="✅ Concluída", text_color="#22aa55")
            elif voz.partitura.posicao == 0:
                lbls["status"].configure(text="⏳ Aguardando...", text_color="#888888")
            else:
                lbls["status"].configure(text="▶️ Tocando", text_color=COR_BOTAO_ESCURO)
            lbls["nota"].configure(text=voz.nota_atual or "—")
            lbls["oitava"].configure(text=str(voz.oitava_atual))
            lbls["instrumento"].configure(
                text=NOMES_MIDI.get(voz.instrumento_atual, f"MIDI #{voz.instrumento_atual}")
            )
            lbls["volume"].configure(text=str(voz.volume_atual))
            lbls["bpm"].configure(text=str(maestro.bpm))
        self.after(350, self._poll)

    def _parar(self):
        self._polling = False
        self.controller.maestro.parar()
