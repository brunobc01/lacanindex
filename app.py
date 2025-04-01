import os
import re
import matplotlib.pyplot as plt
import PyPDF2
import docx2txt
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

documents_folder = "documents"

def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text() + " "
    return text

def extract_text_from_docx(docx_path):
    return docx2txt.process(docx_path)

def search_term_in_text(text, term):
    pattern = re.compile(r"\b" + re.escape(term) + r"\b", re.IGNORECASE)
    matches = pattern.finditer(text)
    return [(match.start(), match.end()) for match in matches]

def get_text_snippet(text, start, end, snippet_size=500):
    snippet_start = max(0, start - snippet_size // 2)
    snippet_end = min(len(text), end + snippet_size // 2)
    return text[snippet_start:snippet_end]

def ordenar_documentos(nome):
    """Função para ordenar os documentos corretamente"""
    if nome.lower() == "escritos":
        return (2, nome)  # Escritos sempre por último
    else:
        numeros = [int(s) for s in nome.split() if s.isdigit()]
        return (1, numeros[0] if numeros else float("inf"))

@app.route("/", methods=["GET", "POST"])
def index():
    resultados = {}
    total_ocorrencias = 0
    termo = ""

    if request.method == "POST":
        termo = request.form["termo"].strip()
        if termo:
            for filename in os.listdir(documents_folder):
                file_path = os.path.join(documents_folder, filename)
                if filename.endswith(".pdf"):
                    text = extract_text_from_pdf(file_path)
                elif filename.endswith(".docx"):
                    text = extract_text_from_docx(file_path)
                else:
                    continue
                
                matches = search_term_in_text(text, termo)
                if matches:
                    total_ocorrencias += len(matches)
                    snippets = [get_text_snippet(text, start, end) for start, end in matches]
                    resultados[filename] = {"count": len(matches), "snippets": snippets}
            
            # Ordenação dos resultados
            resultados = dict(sorted(resultados.items(), key=lambda x: ordenar_documentos(x[0])))
            
            # Geração do gráfico
            if resultados:
                filenames = list(resultados.keys())
                occurrences = [resultados[doc]["count"] for doc in filenames]
                plt.figure(figsize=(8, 4))
                plt.barh(filenames, occurrences, color="darkblue")
                plt.xlabel("Frequência do termo")
                plt.ylabel("Documentos")
                plt.title(f"Ocorrências de '{termo}' nos documentos")
                for index, value in enumerate(occurrences):
                    plt.text(value, index, str(value))
                plt.tight_layout()
                plt.savefig("static/graph.png")
                plt.close()
    
    return render_template("index.html", resultados=resultados, termo=termo, total_ocorrencias=total_ocorrencias)

@app.route("/get_snippets", methods=["POST"])
def get_snippets():
    data = request.get_json()
    filename = data.get("filename")
    termo = data.get("termo")

    if not filename or not termo:
        return jsonify({"error": "Parâmetros inválidos."})
    
    file_path = os.path.join(documents_folder, filename)
    if filename.endswith(".pdf"):
        text = extract_text_from_pdf(file_path)
    elif filename.endswith(".docx"):
        text = extract_text_from_docx(file_path)
    else:
        return jsonify({"error": "Formato de arquivo não suportado."})
    
    matches = search_term_in_text(text, termo)
    snippets = [get_text_snippet(text, start, end) for start, end in matches]
    return jsonify({"snippets": snippets})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)
