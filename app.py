from flask import Flask, render_template, request, jsonify
import os
import fitz  # PyMuPDF para PDFs
import docx2txt
import matplotlib.pyplot as plt
import base64
from io import BytesIO
import re
import threading

app = Flask(__name__)
DOCUMENTS_FOLDER = "documents"
text_cache = {}

def extract_text_from_pdf(pdf_path):
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text()
    return text

def extract_text_from_docx(docx_path):
    return docx2txt.process(docx_path)

def load_documents():
    global text_cache
    text_cache = {}
    
    filenames = os.listdir(DOCUMENTS_FOLDER)

    # Separar o arquivo "Escritos" dos demais
    escritos_file = [f for f in filenames if f.lower().startswith("escritos")]
    other_files = [f for f in filenames if not f.lower().startswith("escritos")]

    # Ordenar os demais arquivos numericamente (S1, S2, ..., S27)
    sorted_files = sorted(other_files, key=lambda x: int(re.search(r'\d+', x).group()))

    # Adicionar "Escritos" no final
    filenames = sorted_files + escritos_file  

    for filename in filenames:
        file_path = os.path.join(DOCUMENTS_FOLDER, filename)
        if filename.endswith(".pdf"):
            text_cache[filename] = extract_text_from_pdf(file_path)
        elif filename.endswith(".docx"):
            text_cache[filename] = extract_text_from_docx(file_path)

def search_term_in_documents(term):
    results = {}
    term_pattern = re.compile(rf'\b{re.escape(term)}\b', re.IGNORECASE)
    
    def search_in_text(filename, text):
        occurrences = len(term_pattern.findall(text))
        snippets = [text[max(0, m.start() - 250): m.end() + 250] for m in term_pattern.finditer(text)]
        if occurrences > 0:
            results[filename] = {"count": occurrences, "snippets": snippets}
    
    threads = []
    for filename, text in text_cache.items():
        thread = threading.Thread(target=search_in_text, args=(filename, text))
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()
    
    return results

def generate_chart(data):
    plt.figure(figsize=(6, 4))  # Ajustando tamanho do gráfico
    filenames = list(data.keys())
    counts = [data[doc]["count"] for doc in filenames]
    
    plt.barh(filenames, counts, color='royalblue')
    plt.xlabel("Ocorrências")
    plt.ylabel("Documentos")
    plt.title("Frequência do termo por documento")
    
    for index, value in enumerate(counts):
        plt.text(value, index, str(value), va='center')
    
    plt.tight_layout()
    
    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    return base64.b64encode(img.getvalue()).decode()

@app.route("/", methods=["GET", "POST"])
def index():
    term = request.form.get("term", "")
    results = search_term_in_documents(term) if term else {}
    chart_data = generate_chart(results) if results else None
    return render_template("index.html", term=term, results=results, chart_data=chart_data)

@app.route("/snippets", methods=["POST"])
def get_snippets():
    data = request.json
    filename = data.get("filename")
    term = data.get("term")
    
    if not filename or not term:
        return jsonify({"error": "Dados inválidos"}), 400
    
    text = text_cache.get(filename, "")
    term_pattern = re.compile(rf'\b{re.escape(term)}\b', re.IGNORECASE)
    snippets = [text[max(0, m.start() - 250): m.end() + 250] for m in term_pattern.finditer(text)]
    
    return jsonify({"snippets": snippets})

if __name__ == "__main__":
    load_documents()
    app.run(debug=True)
