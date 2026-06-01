"""
Constantes musicais e de MIDI compartilhadas entre Voz (configuração) e
Partitura (tokenização). Centralizá-las aqui evita um import circular entre os
dois módulos.
"""

# Configuração cíclica das vozes (baseada em id_voz % TAMANHO_CICLO_VOZ)
OITAVA_TETO_CICLO = 6
OITAVA_MIN_BASE_CICLO = 3
TAMANHO_CICLO_VOZ = 4

VOLUME_TETO_CICLO = 100
VOLUME_DECREMENTO_CICLO = 20

CANAIS_MIDI_TOTAL = 16

# Instrumentos MIDI mapeados
INSTRUMENTO_PIANO = 0
INSTRUMENTO_ORGAN = 20
INSTRUMENTO_HARPSICHORD = 6
INSTRUMENTO_BASSOON = 70
INSTRUMENTO_HARMONICA = 22
INSTRUMENTO_TUBULAR_BELLS = 14
INSTRUMENTO_CHURCH_ORGAN = 19
INSTRUMENTO_BAGPIPE = 109

# Instrumentos atribuídos ciclicamente às vozes:
# V0=Piano, V1=Organ, V2=Harpsichord, V3=Bassoon, V4=Piano, ...
INSTRUMENTOS_CICLICOS = [
    INSTRUMENTO_PIANO,
    INSTRUMENTO_ORGAN,
    INSTRUMENTO_HARPSICHORD,
    INSTRUMENTO_BASSOON,
]

# Símbolo de instrumento inicial (início da linha) -> número MIDI
MAPA_INST_INICIAL = {
    '!': INSTRUMENTO_HARMONICA,
    ';': INSTRUMENTO_TUBULAR_BELLS,
    ',': INSTRUMENTO_CHURCH_ORGAN,
}

# Conjuntos de caracteres usados na tokenização
NOTAS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'Mb']
PAUSAS = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
VOGAIS = ['O', 'I', 'U', 'o', 'i', 'u']
