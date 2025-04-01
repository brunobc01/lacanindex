import os
from flask import Flask, render_template, request
import fitz  # PyMuPDF para PDFs
import docx2txt
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)

DOCUMENTS_FOLDER = "documents"

def extrair_texto_pdf(caminho_arquivo):
    """Extrai texto de um arquivo PDF e libera memória após leitura."""
    texto = ""
    with fitz.open(caminho_arquivo) as doc:
        for pagina in doc:
            texto += pagina.get_text()
    return texto  

def extrair_texto_docx(caminho_arquivo):
    """Extrai texto de um arquivo DOCX e libera memória."""
    texto = docx2txt.process(caminho_arquivo)
    return texto  

def contar_ocorrencias(termo, caminho_arquivo):
    """Conta quantas vezes um termo aparece no arquivo sem armazenar texto na memória."""
    if caminho_arquivo.endswith(".pdf"):
        texto = extrair_texto_pdf(caminho_arquivo)
    elif caminho_arquivo.endswith(".docx"):
        texto = extrair_texto_docx(caminho_arquivo)
    else:
        return 0
    
    ocorrencias = texto.lower().split().count(termo.lower())  
    return ocorrencias

def gerar_grafico(dados):
    """Gera gráfico e retorna como imagem base64 (sem salvar no disco)."""
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
            for arquivo in os.listdir(DOCUMENTS_FOLDER):
                caminho_arquivo = os.path.join(DOCUMENTS_FOLDER, arquivo)
                if caminho_arquivo.endswith((".pdf", ".docx")):
                    ocorrencias = contar_ocorrencias(termo_busca, caminho_arquivo)
                    if ocorrencias > 0:
                        resultados[arquivo] = ocorrencias

            if resultados:
                grafico_base64 = gerar_grafico(resultados)

    return render_template("index.html", resultados=resultados, grafico_base64=grafico_base64, termo=termo_busca)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Usa a porta do ambiente no Render
    app.run(host="0.0.0.0", port=port)
