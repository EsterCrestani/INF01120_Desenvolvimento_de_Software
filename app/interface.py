import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
from app.maestro import Maestro
from app.gerenciador_arquivo import GerenciadorArquivo

# Configuração global de aparência
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# Cores
COR_FUNDO_JANELA = "#140e38"
COR_FUNDO_CARD   = "#ffffff"
COR_TITULO       = "#82bade"
COR_BOTAO_ESCURO = "#1a1053"
COR_TEXTO_CINZA  = "#888888"
COR_FUNDO_VOZ    = "#a8d0e8"


class InterfaceApp:
    def __init__(self, root: ctk.CTk):
        self.root = root
        self.root.title("Gerador de Sequências Musicais")
        self.root.geometry("960x720")
        self.root.configure(fg_color=COR_FUNDO_JANELA)

        self.maestro = Maestro(callback_finalizacao=self.on_play_finished)
        self.caminho_midi_salvo = None

        # Card branco central
        self.container = ctk.CTkFrame(self.root, fg_color=COR_FUNDO_CARD, corner_radius=40)
        self.container.pack(fill="both", expand=True, padx=40, pady=40)

        # Botão "Encerrar sessão" fixo no topo direito
        ctk.CTkButton(
            self.container, text="Encerrar sessão",
            fg_color="transparent", text_color=COR_TEXTO_CINZA,
            hover_color="#f0f0f0", font=("Arial", 13),
            command=self.root.destroy, width=120
        ).place(relx=1.0, rely=0.0, anchor="ne", x=-15, y=12)

        # Páginas
        self.frames = {}
        for F in (PageHome, PageInput, PageConfig, PagePlaying, PageFinished):
            name = F.__name__
            frame = F(parent=self.container, controller=self)
            self.frames[name] = frame

        self.show_frame("PageHome")

    def show_frame(self, page_name):
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
        self.maestro.salvar_midi(self.caminho_midi_salvo)
        self.root.after(0, lambda: self.show_frame("PageFinished"))


# ─────────────────────────── PAGE HOME ──────────────────────────────
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
            "VOLUME: Espaço = Dobra o volume da voz",
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


# ─────────────────────────── PAGE INPUT ─────────────────────────────
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

        # ── Legenda detalhada ──────────────────────────────────────
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

        COLUNAS = [
            ("Notas Musicais:", [
                "A a G → Lá a Sol",
                "H → Si Bemol",
                "Mb → Mi Bemol",
                "a–h → Silêncio",
            ]),
            ("Volume:", [
                "Espaço → dobra o volume",
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
                "> / < → BPM +/−10",
                "Consoantes não mapeadas repetem nota anterior ou geram silêncio",
            ]),
        ]

        for titulo, itens in COLUNAS:
            col = ctk.CTkFrame(cols_frame, fg_color="transparent")
            col.pack(side="left", fill="both", expand=True, padx=4, anchor="n")
            ctk.CTkLabel(
                col, text=titulo,
                font=("Arial", 12, "bold"), text_color=COR_BOTAO_ESCURO
            ).pack(anchor="w")
            for item in itens:
                ctk.CTkLabel(
                    col, text="• " + item,
                    font=("Arial", 10), text_color=COR_TEXTO_CINZA,
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


# ─────────────────────────── PAGE CONFIG ────────────────────────────
class PageConfig(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller

        # Título fora do card azul
        ctk.CTkLabel(
            self, text="Configurações Iniciais:",
            font=("Arial", 24, "bold"), text_color=COR_BOTAO_ESCURO
        ).pack(pady=(12, 6))

        # Card azul
        card = ctk.CTkFrame(self, fg_color=COR_FUNDO_VOZ, corner_radius=20)
        card.pack(fill="both", expand=True, padx=10, pady=(0, 8))

        self.scroll = ctk.CTkScrollableFrame(card, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=12, pady=12)

        # Barra de botões fixa na base
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

        vozes = self.controller.maestro.partitura.get_vozes()
        for voz in vozes:
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

        # Instrumento — usa instrumento_atual (já pode ter sido alterado pelo char inicial)
        ids_midi = [0, 6, 14, 19, 20, 22, 70, 109]
        nomes = ["Piano (#0)", "Cravinhos (#6)", "Tubular B. (#14)",
                 "Church Org. (#19)", "Órgão (#20)", "Harmonica (#22)", "Fagote (#70)", "Gaita de Foles (#109)"]
        inst_atual = voz.instrumento_atual
        idx = ids_midi.index(inst_atual) if inst_atual in ids_midi else 0
        self._dropdown(linha, "Instrumento:", nomes, nomes[idx],
                       lambda val, v=voz: setattr(v, "instrumento_atual",
                                                  ids_midi[nomes.index(val)]))

        # Oitava
        oitavas = [f"Oitava {i}" for i in range(1, 10)]
        self._dropdown(linha, "Oitava:", oitavas, f"Oitava {voz.oitava_base}",
                       lambda val, v=voz: setattr(v, "oitava_atual",
                                                  int(val.replace("Oitava ", ""))))

        # Andamento (global)
        self._seta(linha, "Andamento:",
                   f"{self.controller.maestro.bpm} BPM",
                   lambda lbl: self._alt_bpm(-10, lbl),
                   lambda lbl: self._alt_bpm(+10, lbl))

        # Volume
        self._seta(linha, "Volume:", str(voz.volume_atual),
                   lambda lbl, v=voz: self._alt_vol(v, -10, lbl),
                   lambda lbl, v=voz: self._alt_vol(v, +10, lbl))

    # ── helpers ──────────────────────────────────────────────────────
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


# ─────────────────────────── PAGE PLAYING ───────────────────────────
NOMES_MIDI = {
    0: "Piano", 6: "Cravinhos", 14: "Tubular Bells", 19: "Church Organ",
    20: "Órgão", 22: "Harmonica", 70: "Fagote", 109: "Gaita de Foles"
}

class PagePlaying(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self._polling = False
        self._labels  = {}   # {id_voz: {campo: CTkLabel}}

        self.lbl_tocando = ctk.CTkLabel(
            self, text="🔊  Tocando...",
            font=("Arial", 22, "bold"), text_color=COR_BOTAO_ESCURO
        )
        self.lbl_tocando.pack(pady=(12, 4))

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
        for voz in self.controller.maestro.partitura.get_vozes():
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
        if not maestro.partitura:
            return
        for voz in maestro.partitura.get_vozes():
            lbls = self._labels.get(voz.id_voz)
            if not lbls:
                continue
            if not voz.has_next():
                lbls["status"].configure(text="✅ Concluída", text_color="#22aa55")
            elif voz.indice_leitura <= voz.atraso_inicial:
                lbls["status"].configure(text="⏳ Aguardando...", text_color="#888888")
            else:
                lbls["status"].configure(text="▶️ Tocando", text_color=COR_BOTAO_ESCURO)
            nota_str = voz.nota_anterior if voz.nota_anterior else "—"
            lbls["nota"].configure(text=nota_str)
            lbls["oitava"].configure(text=str(voz.oitava_atual))
            nome_inst = NOMES_MIDI.get(voz.instrumento_atual, f"MIDI #{voz.instrumento_atual}")
            lbls["instrumento"].configure(text=nome_inst)
            lbls["volume"].configure(text=str(voz.volume_atual))
            lbls["bpm"].configure(text=str(maestro.bpm))
        self.after(350, self._poll)

    def _parar(self):
        self._polling = False
        self.controller.maestro.parar()


# ─────────────────────────── PAGE FINISHED ──────────────────────────
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
