# 🎵 Gerador de Sequências Musicais

> Trabalho Prático — INF01120 Desenvolvimento de Software  
> **Fase 2: Orquestrador Polifônico de Fugas**

Sistema que converte sequências de texto em música polifônica (estilo fuga de Bach) em tempo real, exportando também um arquivo `.mid` ao final da reprodução.

---

## 📋 Pré-requisitos

- Python 3.12+
- [UV](https://docs.astral.sh/uv/) (gerenciador de dependências) **ou** pip

---

## ⚙️ Instalação

**Com UV (recomendado):**
```bash
uv sync
```

**Com pip (alternativa):**
```bash
pip install pygame mido customtkinter
```

---

## ▶️ Executar o programa

```bash
python main.py
```

A interface gráfica abrirá com o fluxo de 5 telas:
1. **Tela Inicial** — Botão "Começar" e modal de informações
2. **Entrada** — Carregue um `.txt` ou digite a sequência
3. **Configurações** — Ajuste instrumento, oitava, BPM e volume por voz
4. **Tocando** — Estado em tempo real de cada voz (nota, oitava, instrumento, volume)
5. **Final** — Caminho do arquivo `.mid` gerado em `saida/`

---

## 🧪 Executar os testes

```bash
python -m pytest tests/teste_fuga.py tests/teste_maestro.py -v
```

**Resultado esperado: 7 passed**

| Teste | Descrição |
|---|---|
| `test_voz_inicializacao` | Parâmetros cíclicos de Voz (oitava, volume, instrumento, atraso) |
| `test_voz_tokenizacao` | Tokenização de notas, tokens duplos (`Mb`) e mudança de instrumento |
| `test_partitura_leitura` | Divisão do texto em múltiplas vozes com atraso `[n]` |
| `test_gerador_midi` | Geração do arquivo `.mid` pelo Maestro |
| `test_maestro_preparacao` | Estado inicial do Maestro após `preparar()` |
| `test_maestro_tocar_parar` | Controle de flag `tocando` |
| `test_maestro_alteracao_bpm` | Processamento de tokens `>` e `<` altera BPM corretamente |

> ⚠️ **Não execute os testes com** `python tests/teste_fuga.py` — use sempre `python -m pytest` para que o Python resolva os imports do pacote `app/` corretamente.

**Teste de áudio manual (requer caixa de som):**
```bash
python -m tests.testeReproducao
```

---

## 🗺️ Legenda de Mapeamento de Caracteres

| Caractere(s) | Efeito |
|---|---|
| `A` a `G` (maiúsc.) | Notas musicais Lá a Sol |
| `H` | Si bemol |
| `Mb` | Mi bemol |
| `a` a `h` (minúsc.) | Silêncio / Pausa |
| `!` | Instrumento → Harmonica (MIDI 22) |
| `;` | Instrumento → Tubular Bells (MIDI 14) |
| `,` | Instrumento → Church Organ (MIDI 19) |
| `O`, `I`, `U` | Instrumento → Gaita de Foles / Bagpipe (MIDI 109) |
| Espaço | Dobra o volume da voz atual |
| `?` | Sobe a oitava da voz |
| `V` | Desce a oitava da voz |
| `>` | Aumenta BPM global em 10 |
| `<` | Diminui BPM global em 10 |
| `[n]` no início da linha | Atraso de *n* beats antes desta voz começar |
| Outras letras/símbolos | Repetem a nota anterior (ou geram silêncio) |

**Exemplo de entrada com 4 vozes:**
```
! A B C D E C B A ? A B C E G [2]G G G a
; [4]C C D E F E D C ? D E F A C B A G a a G
, [8]G A B C D D C B A B C D E F G ? G a
, [2]E E F G A B C B A G F E D C B A ? A B C D E D C B A a a
```

---

## 🏗️ Arquitetura

```
app/
├── interface.py        # Interface gráfica (CustomTkinter) — 5 telas
├── maestro.py          # Orquestrador polifônico (loop musical + threads)
├── partitura.py        # Divide o texto em objetos Voz
├── voz.py              # Estado individual de cada voz + tokenizador
├── reproducao_audio.py # Comunicação com pygame.midi
├── gerador_midi.py     # Exportação para arquivo .mid (mido)
└── gerenciador_arquivo.py  # Leitura/escrita de arquivos TXT
tests/
├── teste_maestro.py    # Testes da classe Maestro (Arthur)
├── teste_fuga.py       # Testes de integração Voz/Partitura/MIDI
└── testeReproducao.py  # Teste manual de áudio (Isaac)
```

---

## 👥 Divisão de Responsabilidades

| Integrante | Responsabilidade |
|---|---|
| Arthur | Classe `Maestro`, `teste_maestro.py` |
| Ester | Interface gráfica, Classe `Voz`, `Partitura` |
| Isaac | `ReproducaoAudio`, `testeReproducao.py` |
