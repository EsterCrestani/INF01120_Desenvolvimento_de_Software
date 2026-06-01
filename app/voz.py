from app.partitura import Partitura
from app.constantes_musicais import (
    OITAVA_TETO_CICLO,
    OITAVA_MIN_BASE_CICLO,
    TAMANHO_CICLO_VOZ,
    VOLUME_TETO_CICLO,
    VOLUME_DECREMENTO_CICLO,
    CANAIS_MIDI_TOTAL,
    INSTRUMENTOS_CICLICOS,
    MAPA_INST_INICIAL,
)


class Voz:
    """
    Agrega a configuração de uma voz (oitava, volume, instrumento, canal e
    atraso inicial) e possui uma Partitura com a sequência de tokens.

    A configuração base é derivada ciclicamente do id_voz; o prefixo da linha
    (instrumento inicial `! ; ,` e atraso `[n]`) é interpretado aqui, pois é
    configuração da voz — a tokenização do conteúdo musical fica na Partitura.
    """

    def __init__(self, id_voz: int, linha_texto: str):
        self.id_voz = id_voz

        # Oitavas: V0=6, V1=5, V2=4, V3=3, V4=6, ...
        self.oitava_base = OITAVA_TETO_CICLO - (id_voz % TAMANHO_CICLO_VOZ)
        if self.oitava_base < OITAVA_MIN_BASE_CICLO:
            self.oitava_base = OITAVA_TETO_CICLO  # default seguro (6, 5, 4, 3 está correto)

        # Volume: V0=100, V1=80, V2=60, V3=40
        self.volume_base = max(VOLUME_TETO_CICLO - (id_voz % TAMANHO_CICLO_VOZ) * VOLUME_DECREMENTO_CICLO, 0)

        # Instrumentos: V0=Piano(0), V1=Organ(20), V2=Harpsichord(6), V3=Bassoon(70)
        self.instrumento_base = INSTRUMENTOS_CICLICOS[id_voz % TAMANHO_CICLO_VOZ]

        self.canal = id_voz % CANAIS_MIDI_TOTAL  # MIDI suporta canais de 0 a 15

        # Interpreta o prefixo (instrumento inicial + atraso) e separa o conteúdo musical
        self.atraso_inicial, linha_musical = self._parse_inicio(linha_texto)

        # A Partitura varre o conteúdo musical e guarda a lista de tokens
        self.partitura = Partitura(linha_musical)

        self.reiniciar_estado()

    def reiniciar_estado(self):
        self.oitava_atual = self.oitava_base
        self.volume_atual = self.volume_base
        self.instrumento_atual = self.instrumento_base
        self.nota_atual = None
        self.partitura.reiniciar()

    def preparar_para_tocar(self, reproducao, gerador_midi):
        """
        Reinicia o estado da voz e registra seu instrumento inicial nas saídas
        de áudio e MIDI, deixando-a pronta para ser executada pelo Maestro.
        """
        self.reiniciar_estado()
        reproducao.set_instrumento_no_canal(self.instrumento_atual, self.canal)
        gerador_midi.registrar_instrumento(self.id_voz, self.canal, self.instrumento_atual)

    def _parse_inicio(self, texto: str) -> tuple[int, str]:
        """
        Analisa o início da linha para extrair, em ordem:
          1. Caractere de instrumento inicial (!, ;, ,)
          2. Atraso [n]

        Atualiza self.instrumento_base e retorna (atraso, conteudo_musical),
        onde conteudo_musical é a parte da linha após o prefixo.
        """
        pos = 0

        # Ignora espaços iniciais
        while pos < len(texto) and texto[pos] == ' ':
            pos += 1

        # Caractere de instrumento inicial?
        if pos < len(texto) and texto[pos] in MAPA_INST_INICIAL:
            self.instrumento_base = MAPA_INST_INICIAL[texto[pos]]
            pos += 1
            # Pula espaço(s) após o símbolo
            while pos < len(texto) and texto[pos] == ' ':
                pos += 1

        # Atraso [n]?
        atraso = 0
        if pos < len(texto) and texto[pos] == '[':
            fim = texto.find(']', pos)
            if fim != -1:
                try:
                    atraso = int(texto[pos + 1:fim])
                    pos = fim + 1
                except ValueError:
                    pass

        # Pula espaço após o atraso
        while pos < len(texto) and texto[pos] == ' ':
            pos += 1

        return atraso, texto[pos:]

    def has_next(self) -> bool:
        return self.partitura.has_next()
