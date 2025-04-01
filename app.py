import os
import re
import io
import matplotlib.pyplot as plt
import PyPDF2
import docx2txt
from flask import Flask, render_template, request, jsonify, send_file

app = Flask(__name__)
DOCUMENTS_FOLDER = "documents"

# Função para processar os arquivos sob demanda
def search_term_in_file(file_path, search_term):
    term_pattern = re.compile(rf'\b{re.escape(search_term)}\b', re.IGNORECASE)
    occurrences = 0
    snippets = []
    
    if file_path.endswith(".pdf"):
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    for match in term_pattern.finditer(text):
                        start = max(0, match.start() - 250)
                        end = min(len(text), match.end() + 250)
                        snippet = text[start:end].strip()
                        snippets.append(snippet)
                        occurrences += 1
    
    elif file_path.endswith(".docx"):
        text = docx2txt.process(file_path)
        for match in term_pattern.finditer(text):
            start = max(0, match.start() - 250)
            end = min(len(text), match.end() + 250)
            snippet = text[start:end].strip()
            snippets.append(snippet)
            occurrences += 1
    
    return occurrences, snippets

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/search", methods=["POST"])
def search():
    search_term = request.form["search_term"].strip()
    
    if not search_term:
        return jsonify({"error": "Digite um termo antes de buscar."})
    
    results = []
    for file_name in sorted(os.listdir(DOCUMENTS_FOLDER), key=lambda x: (x[:2].isdigit(), x)):
        file_path = os.path.join(DOCUMENTS_FOLDER, file_name)
        occurrences, snippets = search_term_in_file(file_path, search_term)
        if occurrences > 0:
            results.append({"file": file_name, "count": occurrences, "snippets": snippets})
    
    if not results:
        return jsonify({"error": "Nenhuma ocorrência encontrada."})
    
    return jsonify(results)

@app.route("/generate_graph", methods=["POST"])
def generate_graph():
    data = request.json
    if not data:
        return jsonify({"error": "Dados inválidos."})
    
    labels = [item["file"] for item in data]
    values = [item["count"] for item in data]
    
    plt.figure(figsize=(6, 4))
    plt.barh(labels, values, color='royalblue')
    plt.xlabel("Ocorrências")
    plt.ylabel("Arquivos")
    plt.title("Frequência do termo por documento")
    plt.gca().invert_yaxis()
    plt.xticks(fontsize=8)
    plt.yticks(fontsize=8)
    plt.tight_layout()
    
    img = io.BytesIO()
    plt.savefig(img, format='png')
    plt.close()
    img.seek(0)
    return send_file(img, mimetype='image/png')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
