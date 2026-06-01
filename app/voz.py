# Constantes de Configuração de Voz e MIDI
OITAVA_MAXIMA = 9
OITAVA_MINIMA = 0
OITAVA_TETO_CICLO = 6
OITAVA_MIN_BASE_CICLO = 3
TAMANHO_CICLO_VOZ = 4

VOLUME_MAXIMO = 127
VOLUME_TETO_CICLO = 100
VOLUME_DECREMENTO_CICLO = 20

CANAIS_MIDI_TOTAL = 16

# Instrumentos MIDI Mapeados
INSTRUMENTO_PIANO = 0
INSTRUMENTO_ORGAN = 20
INSTRUMENTO_HARPSICHORD = 6
INSTRUMENTO_BASSOON = 70
INSTRUMENTO_HARMONICA = 22
INSTRUMENTO_TUBULAR_BELLS = 14
INSTRUMENTO_CHURCH_ORGAN = 19
INSTRUMENTO_BAGPIPE = 109

INSTRUMENTOS_CICLICOS = [
    INSTRUMENTO_PIANO,
    INSTRUMENTO_ORGAN,
    INSTRUMENTO_HARPSICHORD,
    INSTRUMENTO_BASSOON
]

MAPA_INST_INICIAL = {
    '!': INSTRUMENTO_HARMONICA,
    ';': INSTRUMENTO_TUBULAR_BELLS,
    ',': INSTRUMENTO_CHURCH_ORGAN
}

class Voz:
    def __init__(self, id_voz: int, linha_texto: str):
        self.id_voz = id_voz
        self.linha_texto = linha_texto
        
        # Atributos cíclicos ou baseados no ID da voz
        # Oitavas: V0=6, V1=5, V2=4, V3=3, V4=6, ...
        self.oitava_base = OITAVA_TETO_CICLO - (id_voz % TAMANHO_CICLO_VOZ)
        if self.oitava_base < OITAVA_MIN_BASE_CICLO:
            self.oitava_base = OITAVA_TETO_CICLO # Caso a conta dê errado, default seguro. Mas 6, 5, 4, 3 está correto.

        # Volume: V0=100, V1=80, V2=60, V3=40
        self.volume_base = max(VOLUME_TETO_CICLO - (id_voz % TAMANHO_CICLO_VOZ) * VOLUME_DECREMENTO_CICLO, 0)
        
        # Instrumentos: V0=Piano(0), V1=Organ(20), V2=Harpsichord(6), V3=Bassoon(70)
        self.instrumento_base = INSTRUMENTOS_CICLICOS[id_voz % TAMANHO_CICLO_VOZ]
        
        self.canal = id_voz % CANAIS_MIDI_TOTAL # MIDI suporta canais de 0 a 15

        self.reiniciar_estado()
        
    def reiniciar_estado(self):
        self.oitava_atual = self.oitava_base
        self.volume_atual = self.volume_base
        self.instrumento_atual = self.instrumento_base
        self.indice_leitura = 0
        self.nota_anterior = None
        self.atraso_inicial = self._parse_inicio()
        
    def _parse_inicio(self) -> int:
        """
        Analisa o início da linha para extrair, em ordem:
          1. Caractere de instrumento inicial (!, ;, ,)
          2. Atraso [n]
        Atualiza self.instrumento_atual e self.indice_leitura.
        """
        texto = self.linha_texto
        pos = 0

        # Ignora espaços iniciais
        while pos < len(texto) and texto[pos] == ' ':
            pos += 1

        # Caractere de instrumento inicial?
        if pos < len(texto) and texto[pos] in MAPA_INST_INICIAL:
            novo_inst = MAPA_INST_INICIAL[texto[pos]]
            self.instrumento_base  = novo_inst
            self.instrumento_atual = novo_inst
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

        self.indice_leitura = pos
        return atraso

    def has_next(self) -> bool:
        return self.indice_leitura < len(self.linha_texto)
        
    def ler_proximo_token(self) -> dict:
        """
        Lê e retorna o próximo token da linha.
        Retorna um dicionário com o tipo de evento e seus parâmetros.
        """
        if not self.has_next():
            return None
            
        char = self.linha_texto[self.indice_leitura]
        
        # Verificar tokens duplos como 'Mb'
        if char == 'M' and self.indice_leitura + 1 < len(self.linha_texto) and self.linha_texto[self.indice_leitura+1] == 'b':
            char = 'Mb'
            self.indice_leitura += 2
        else:
            self.indice_leitura += 1

        token = {'tipo': 'UNKNOWN', 'char': char}
        
        # Notas
        if char in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'Mb']:
            token['tipo'] = 'NOTA'
            self.nota_anterior = char
        # Pausas (a-h e outras lógicas trataremos depois ou na Partitura)
        elif char in ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']:
            token['tipo'] = 'PAUSA'
        # Mudança de Instrumento
        elif char == '!':
            token['tipo'] = 'INSTRUMENTO'
            token['valor'] = INSTRUMENTO_HARMONICA
            self.instrumento_atual = INSTRUMENTO_HARMONICA
        elif char == ';':
            token['tipo'] = 'INSTRUMENTO'
            token['valor'] = INSTRUMENTO_TUBULAR_BELLS
            self.instrumento_atual = INSTRUMENTO_TUBULAR_BELLS
        elif char == ',':
            token['tipo'] = 'INSTRUMENTO'
            token['valor'] = INSTRUMENTO_CHURCH_ORGAN
            self.instrumento_atual = INSTRUMENTO_CHURCH_ORGAN
        # Controle de Oitava
        elif char == '?':
            token['tipo'] = 'OITAVA_UP'
            self.oitava_atual = min(self.oitava_atual + 1, OITAVA_MAXIMA)
        elif char == 'V':
            token['tipo'] = 'OITAVA_DOWN'
            self.oitava_atual = max(self.oitava_atual - 1, OITAVA_MINIMA)
        # Controle de Volume
        elif char == ' ':
            token['tipo'] = 'VOLUME_DOUBLE'
            self.volume_atual = min(self.volume_atual * 2, VOLUME_MAXIMO)
        # Controle de BPM Global (afeta todas as vozes, mas emitimos como evento)
        elif char == '>':
            token['tipo'] = 'BPM_UP'
        elif char == '<':
            token['tipo'] = 'BPM_DOWN'
        # Vogais -> Gaita de Foles (MIDI 109 = Bagpipe)
        elif char in ['O', 'I', 'U', 'o', 'i', 'u']:
            token['tipo'] = 'INSTRUMENTO'
            token['valor'] = INSTRUMENTO_BAGPIPE
            self.instrumento_atual = INSTRUMENTO_BAGPIPE
        # Regra de repetição (consoantes e outros não classificados)
        else:
            if char.isalpha() or char.isdigit() or not char.isspace():
                if self.nota_anterior:
                    token['tipo'] = 'NOTA'
                    token['char'] = self.nota_anterior
                else:
                    token['tipo'] = 'PAUSA'
            else:
                token['tipo'] = 'IGNORE'
                
        return token
