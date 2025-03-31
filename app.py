from flask import Flask, render_template, request, jsonify
import os
import fitz  # PyMuPDF para PDFs
import docx2txt
import matplotlib.pyplot as plt
import base64
from io import BytesIO

app = Flask(__name__)
DOCUMENTS_FOLDER = "documents"

def extract_text_from_pdf(pdf_path):
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text()
    return text

def extract_text_from_docx(docx_path):
    return docx2txt.process(docx_path)

def search_term_in_documents(term):
    results = {}
    term_lower = term.lower()
    for filename in os.listdir(DOCUMENTS_FOLDER):
        file_path = os.path.join(DOCUMENTS_FOLDER, filename)
        if filename.endswith(".pdf"):
            text = extract_text_from_pdf(file_path)
        elif filename.endswith(".docx"):
            text = extract_text_from_docx(file_path)
        else:
            continue
        
        words = text.split()
        occurrences = sum(1 for word in words if word.lower() == term_lower)
        snippets = [text[max(0, i - 250): i + 250] for i in range(len(text)) if text[i:i+len(term)].lower() == term_lower]
        
        if occurrences > 0:
            results[filename] = {"count": occurrences, "snippets": snippets}
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
    
    file_path = os.path.join(DOCUMENTS_FOLDER, filename)
    
    if filename.endswith(".pdf"):
        text = extract_text_from_pdf(file_path)
    elif filename.endswith(".docx"):
        text = extract_text_from_docx(file_path)
    else:
        return jsonify({"error": "Formato não suportado"}), 400
    
    snippets = [text[max(0, i - 250): i + 250] for i in range(len(text)) if text[i:i+len(term)].lower() == term.lower()]
    
    return jsonify({"snippets": snippets})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
