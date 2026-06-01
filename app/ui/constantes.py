# Constantes visuais compartilhadas por todas as páginas
import customtkinter as ctk

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

COR_FUNDO_JANELA = "#140e38"
COR_FUNDO_CARD   = "#ffffff"
COR_TITULO       = "#82bade"
COR_BOTAO_ESCURO = "#1a1053"
COR_TEXTO_CINZA  = "#888888"
COR_FUNDO_VOZ    = "#a8d0e8"

NOMES_MIDI = {
    0: "Piano", 6: "Cravinhos", 14: "Tubular Bells", 19: "Church Organ",
    20: "Órgão", 22: "Harmonica", 70: "Fagote", 109: "Gaita de Foles"
}

IDS_MIDI  = [0, 6, 14, 19, 20, 22, 70, 109]
NOMES_OPT = [f"{NOMES_MIDI[i]} (#{i})" for i in IDS_MIDI]
