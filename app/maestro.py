import threading
import time
from typing import Callable, List
from app.voz import Voz
from app.reproducao_audio import ReproducaoAudio
from app.gerador_midi import GeradorMIDI
from app.tokens import DURACAO_BEAT_PADRAO

# Constantes de Andamento (BPM)
BPM_PADRAO = 120

# Constantes de Tempo
SEGUNDOS_POR_MINUTO = 60.0

class Maestro:
    """
    Classe responsável por orquestrar a execução das vozes, gerenciar o andamento (BPM)
    e coordenar o áudio e a geração de MIDI.
    """
    def __init__(self, callback_finalizacao: Callable | None = None):
        self.reproducao = ReproducaoAudio()
        self.gerador_midi = GeradorMIDI()
        self.tocando = False
        self.bpm = BPM_PADRAO
        self.vozes: List[Voz] = []
        self.callback_finalizacao = callback_finalizacao


    def preparar(self, texto: str):
        self.vozes = self._criar_vozes(texto)
        self.bpm = BPM_PADRAO
        self.gerador_midi = GeradorMIDI(bpm_inicial=self.bpm)


    def _criar_vozes(self, texto: str) -> List[Voz]:
        """Cria uma Voz para cada linha não vazia do texto."""
        vozes: List[Voz] = []
        for i, linha in enumerate(texto.splitlines()):
            linha_limpa = linha.strip()
            if linha_limpa:
                vozes.append(Voz(id_voz=i, linha_texto=linha_limpa))
        return vozes


    def tocar(self):
        if not self.vozes or self.tocando:
            return

        self.tocando = True
        for voz in self.vozes:
            voz.preparar_para_tocar(self.reproducao, self.gerador_midi)

        threading.Thread(target=self._loop_musical, daemon=True).start()


    def _loop_musical(self):
        """Loop principal que processa um beat de cada vez para todas as vozes."""
        vozes = self.vozes
        beats = {voz.id_voz: 0 for voz in vozes}
        notas_tocando = {}

        while self.tocando and any(voz.has_next() for voz in vozes):
            duracao_beat = SEGUNDOS_POR_MINUTO / self.bpm
            teve_evento = False

            for voz in vozes:
                if not voz.has_next():
                    continue

                # Gerencia o atraso inicial de cada voz
                if beats[voz.id_voz] < voz.atraso_inicial:
                    beats[voz.id_voz] += 1
                    self.gerador_midi.registrar_pausa(voz.id_voz, DURACAO_BEAT_PADRAO)
                    continue

                token = voz.partitura.proximo_token()
                if not token:
                    continue

                teve_evento = True
                token.processar(voz, self, notas_tocando)

            if not teve_evento and not any(voz.has_next() for voz in vozes):
                break

            # Espera o tempo de um beat
            time.sleep(duracao_beat)
            self._silenciar_notas(notas_tocando)

        self.parar()


    def parar(self):
        self.tocando = False
        self.reproducao.parar_reproducao()
        if self.callback_finalizacao:
            self.callback_finalizacao()


    def _silenciar_notas(self, notas_tocando):
        """Desliga todas as notas que foram tocadas no beat atual."""
        for id_voz, (nota, oitava, canal) in list(notas_tocando.items()):
            self.reproducao.silenciar_nota(nota, oitava, canal)
        notas_tocando.clear()
