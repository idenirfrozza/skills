# Projeto: Laudo Condiscs

**Descrição:** Use o arquivo escaneado com os dados preenchidos a mão e siga as instruções.

## Instruções do projeto

Esse bot recebe um arquivo em pdf e Recriar o mesmo arquivo mantendo a estrutura original, apenas trocar as escritas humanas feito a mão e no mesmo lugar colocar uma fonte que imita letra manuscrita com a mesma informação das escritas humanas impressos do formulário, deve manter o mesmo layout, mesmas cores e tamanhos e também cuidar para que fundo, quando removido as escritas a mão, fique com a mesma textura de cores, que visualmente não apresente que a escrita a mão tenha sido removida e depois salve novamente em arquivo em formato pdf com o nome que deve a data e hora atual (AAAAMMDDHHMM) + "Dimensional e Qualidade"

## Arquivos desta pasta

| Arquivo | Para que serve |
|---|---|
| `SKILL.md` | Skill completa: passo a passo, convenções de leitura do manuscrito, estrutura do formulário e regras de desvio |
| `laudo_process.py` | Apaga o manuscrito, reconstrói fundo e linhas, pinta destaques em amarelo e reescreve com fonte manuscrita |
| `lines.py` | Localiza as linhas horizontais e verticais da tabela |
| `crop.py` | Recorte com grade de coordenadas para leitura e posicionamento |
| `checa_desvios.py` | Função de checagem de valores contra nominal e tolerância |
| `exemplo_campos_p0.py` | Exemplo de arquivo de campos da página da tabela |

## Uso rápido

```bash
pdfimages -png entrada.pdf img/p
python3 laudo_process.py img/p-000.png campos_p0.py out0.png destaques_p0.json
img2pdf --imgsize 72dpi p0.jpg p1.jpg -o "AAAAMMDDHHMM Dimensional e Qualidade.pdf"
```

Dependências: `opencv-python`, `numpy`, `Pillow`, `pypdf`, `img2pdf`, `poppler-utils` (pdfimages) e a fonte `NothingYouCouldDo-Regular.ttf` (caminho configurável pela variável `HAND_FONT`).
