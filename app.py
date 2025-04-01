import os
import re
from flask import Flask, render_template, request
import fitz  # PyMuPDF para PDFs
import docx2txt
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)

DOCUMENTS_FOLDER = "documents"
documentos_texto = {}  # Armazena textos dos arquivos na memória

def extrair_texto_pdf(caminho_arquivo):
    """Extrai texto de um PDF de forma otimizada."""
    texto = []
    with fitz.open(caminho_arquivo) as doc:
        for pagina in doc:
            texto.append(pagina.get_text("text"))
    return " ".join(texto)  

def extrair_texto_docx(caminho_arquivo):
    """Extrai texto de um DOCX de forma otimizada."""
    return docx2txt.process(caminho_arquivo)

def carregar_documentos():
    """Pré-carrega o texto dos documentos na memória para buscas rápidas."""
    global documentos_texto
    documentos_texto.clear()
    
    for arquivo in os.listdir(DOCUMENTS_FOLDER):
        caminho_arquivo = os.path.join(DOCUMENTS_FOLDER, arquivo)
        if caminho_arquivo.endswith(".pdf"):
            documentos_texto[arquivo] = extrair_texto_pdf(caminho_arquivo).lower()
        elif caminho_arquivo.endswith(".docx"):
            documentos_texto[arquivo] = extrair_texto_docx(caminho_arquivo).lower()

def contar_ocorrencias(termo):
    """Conta ocorrências do termo de forma mais eficiente com regex."""
    termo_regex = r"\b" + re.escape(termo.lower()) + r"\b"  
    contagem = {arquivo: len(re.findall(termo_regex, texto)) for arquivo, texto in documentos_texto.items()}
    return {k: v for k, v in contagem.items() if v > 0}  

def gerar_grafico(dados):
    """Gera gráfico de barras e retorna como imagem base64."""
    fig, ax = plt.subplots(figsize=(6, 4))
    nomes = list(dados.keys())
    valores = list(dados.values())

    ax.barh(nomes, valores, color="blue")
    ax.set_xlabel("Quantidade")
    ax.set_title("Frequência do termo por documento")

    buffer = io.BytesIO()
    plt.savefig(buffer, format="png", bbox_inches="tight")
    buffer.seek(0)
    grafico_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    plt.close(fig)

    return grafico_base64

@app.route("/", methods=["GET", "POST"])
def index():
    resultados = {}
    grafico_base64 = None
    termo_busca = ""

    if request.method == "POST":
        termo_busca = request.form.get("termo", "").strip()
        if termo_busca:
            resultados = contar_ocorrencias(termo_busca)

            if resultados:
                grafico_base64 = gerar_grafico(resultados)

    return render_template("index.html", resultados=resultados, grafico_base64=grafico_base64, termo=termo_busca)

if __name__ == "__main__":
    carregar_documentos()  # Carrega os documentos ao iniciar o app
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
