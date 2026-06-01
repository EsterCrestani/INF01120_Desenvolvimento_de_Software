import threading
import time
from typing import Callable, Optional
from app.partitura import Partitura
from app.reproducao_audio import ReproducaoAudio
from app.gerador_midi import GeradorMIDI

# Constantes de Andamento (BPM)
BPM_PADRAO = 120
BPM_AJUSTE = 10
BPM_MINIMO = 10

# Constantes de Tempo
SEGUNDOS_POR_MINUTO = 60.0
DURACAO_BEAT_PADRAO = 1.0

class Maestro:
    """
    Classe responsável por orquestrar a execução das vozes, gerenciar o andamento (BPM)
    e coordenar o áudio e a geração de MIDI.
    """
    def __init__(self, callback_finalizacao: Optional[Callable] = None):
        self.reproducao = ReproducaoAudio()
        self.gerador_midi = None
        self.tocando = False
        self.bpm = BPM_PADRAO
        self.partitura = None
        self.callback_finalizacao = callback_finalizacao
        
    def preparar(self, texto: str):
        self.partitura = Partitura(texto)
        self.bpm = BPM_PADRAO
        self.gerador_midi = GeradorMIDI(bpm_inicial=self.bpm)
        
    def tocar(self):
        if not self.partitura or self.tocando:
            return
            
        self.tocando = True
        self.partitura.reiniciar_todas()
        
        # Define instrumentos iniciais nas saídas (Audio e MIDI)
        for voz in self.partitura.get_vozes():
            self.reproducao.setInstrumento(voz.instrumento_atual, voz.canal)
            self.gerador_midi.registrar_instrumento(voz.id_voz, voz.canal, voz.instrumento_atual)
            
        threading.Thread(target=self._loop_musical, daemon=True).start()
        
    def parar(self):
        self.tocando = False
        self.reproducao.pararReproducao()
        if self.callback_finalizacao:
            self.callback_finalizacao()
            
    def salvar_midi(self, caminho: str):
        if self.gerador_midi:
            self.gerador_midi.salvar(caminho)

    def _loop_musical(self):
        """Loop principal que processa um beat de cada vez para todas as vozes."""
        vozes = self.partitura.get_vozes()
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
                
                token = voz.ler_proximo_token()
                if not token:
                    continue
                    
                teve_evento = True
                self._processar_token(voz, token, notas_tocando)
                    
            if not teve_evento and not any(voz.has_next() for voz in vozes):
                break
                
            # Espera o tempo de um beat
            time.sleep(duracao_beat)
            self._silenciar_notas(notas_tocando)
            
        self.parar()

    def _processar_token(self, voz, token, notas_tocando):
        """Aplica o token lido na voz atual (Toca nota, muda instrumento, etc)."""
        tipo = token['tipo']
        
        if tipo == 'NOTA':
            nota = token['char']
            self.reproducao.reproduzirNota(nota, voz.oitava_atual, voz.volume_atual, voz.canal)
            self.gerador_midi.registrar_nota(voz.id_voz, voz.canal, nota, voz.oitava_atual, voz.volume_atual, DURACAO_BEAT_PADRAO)
            notas_tocando[voz.id_voz] = (nota, voz.oitava_atual, voz.canal)
            
        elif tipo == 'PAUSA':
            self.gerador_midi.registrar_pausa(voz.id_voz, DURACAO_BEAT_PADRAO)
            
        elif tipo == 'INSTRUMENTO':
            self.reproducao.setInstrumento(voz.instrumento_atual, voz.canal)
            self.gerador_midi.registrar_instrumento(voz.id_voz, voz.canal, voz.instrumento_atual)
            
        elif tipo == 'BPM_UP':
            self.bpm += BPM_AJUSTE
            self.gerador_midi.alterar_bpm(self.bpm)
            
        elif tipo == 'BPM_DOWN':
            self.bpm = max(BPM_MINIMO, self.bpm - BPM_AJUSTE)
            self.gerador_midi.alterar_bpm(self.bpm)

    def _silenciar_notas(self, notas_tocando):
        """Desliga todas as notas que foram tocadas no beat atual."""
        for id_voz, (nota, oitava, canal) in list(notas_tocando.items()):
            self.reproducao.silenciarNota(nota, oitava, canal)
        notas_tocando.clear()
