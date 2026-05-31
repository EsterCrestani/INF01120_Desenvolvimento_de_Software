import mido
from mido import Message, MidiFile, MidiTrack, MetaMessage

class GeradorMIDI:
    def __init__(self, bpm_inicial: int = 120):
        self.mid = MidiFile(type=1) # Formato 1: Múltiplas trilhas simultâneas
        self.tracks = {}
        self.tempos_absolutos = {}
        self.bpm_atual = bpm_inicial
        
        # Track 0 geralmente usada para metadados (Tempo, etc)
        self.meta_track = MidiTrack()
        self.mid.tracks.append(self.meta_track)
        tempo = mido.bpm2tempo(self.bpm_atual)
        self.meta_track.append(MetaMessage('set_tempo', tempo=tempo, time=0))

    def _obter_track(self, id_voz: int) -> MidiTrack:
        if id_voz not in self.tracks:
            track = MidiTrack()
            self.mid.tracks.append(track)
            self.tracks[id_voz] = track
            self.tempos_absolutos[id_voz] = 0
        return self.tracks[id_voz]

    def _calcular_nota_midi(self, nota_char: str, oitava: int) -> int:
        mapa_notas = {
            'C': 0, 'D': 2, 'E': 4, 'F': 5, 
            'G': 7, 'A': 9, 'B': 11, 'H': 10, 'MB': 3
        }
        nota_upper = nota_char.upper()
        if nota_upper not in mapa_notas:
            return -1
        nota_base = mapa_notas[nota_upper]
        return max(0, min((oitava + 1) * 12 + nota_base, 127))

    def registrar_instrumento(self, id_voz: int, canal: int, instrumento: int):
        track = self._obter_track(id_voz)
        # Instrument change is instantaneous (time=0)
        track.append(Message('program_change', program=instrumento, channel=canal, time=0))

    def registrar_nota(self, id_voz: int, canal: int, nota: str, oitava: int, volume: int, duracao_beats: float):
        track = self._obter_track(id_voz)
        nota_midi = self._calcular_nota_midi(nota, oitava)
        
        if nota_midi != -1:
            # Em Mido, time é delta em ticks. 
            # Assumiremos 480 ticks por beat (padrão mido).
            ticks_por_beat = self.mid.ticks_per_beat
            duracao_ticks = int(duracao_beats * ticks_por_beat)
            
            # Note On (sem atraso antes da nota começar)
            track.append(Message('note_on', note=nota_midi, velocity=volume, channel=canal, time=0))
            # Note Off (ocorre após duracao_ticks)
            track.append(Message('note_off', note=nota_midi, velocity=0, channel=canal, time=duracao_ticks))
            
            self.tempos_absolutos[id_voz] += duracao_ticks

    def registrar_pausa(self, id_voz: int, duracao_beats: float):
        track = self._obter_track(id_voz)
        ticks_por_beat = self.mid.ticks_per_beat
        duracao_ticks = int(duracao_beats * ticks_por_beat)
        
        # Para registrar pausa em MIDI com delta time, podemos inserir uma mensagem inofensiva 
        # ou apenas somar ao tempo do próximo evento. No Mido, é mais fácil só manter controle 
        # e aplicar no 'time' da PRÓXIMA mensagem. Mas para simplificar, inserimos um Note Off inofensivo.
        track.append(Message('note_off', note=0, velocity=0, channel=0, time=duracao_ticks))
        self.tempos_absolutos[id_voz] += duracao_ticks

    def alterar_bpm(self, novo_bpm: int):
        self.bpm_atual = max(10, novo_bpm)
        tempo = mido.bpm2tempo(self.bpm_atual)
        # Adiciona a mudança de andamento na meta_track (usaremos time=0 por simplicidade, 
        # mas numa implementação perfeita deveríamos calcular o delta time global)
        self.meta_track.append(MetaMessage('set_tempo', tempo=tempo, time=0))

    def salvar(self, caminho_arquivo: str):
        self.mid.save(caminho_arquivo)
