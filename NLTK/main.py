import glob
import os
import re
import shutil
import time

import nltk
import pdfplumber
from nltk.stem import RSLPStemmer
from nltk.tokenize import word_tokenize
from PyPDF2 import PdfReader

# Baixar recursos necessários do NLTK
nltk.download("punkt")
nltk.download("punkt_tab")
nltk.download("rslp")

def criarpdf_TXT(nomePDF: str, textoCompleto: str):
    pasta_pdftxt = "pdfsTXT"
    os.makedirs(pasta_pdftxt, exist_ok=True)
    
    nome_txt = os.path.splitext(os.path.basename(nomePDF))[0] + ".txt"
    caminho_txt = os.path.join(pasta_pdftxt, nome_txt)

    with open(caminho_txt, "w", encoding="utf-8") as f:
        f.write(textoCompleto)
    
    print(f"TXT das bulas criado: {caminho_txt}")

def escrever_txt(nome_pdf: str, texto: str):
    """
    Cria um arquivo .txt com o conteúdo extraído da seção e salva na pasta 'comparativo'.
    """
    pasta_comparativo = "comparativo"
    os.makedirs(pasta_comparativo, exist_ok=True)
    
    nome_txt = os.path.splitext(os.path.basename(nome_pdf))[0] + ".txt"
    caminho_txt = os.path.join(pasta_comparativo, nome_txt)

    with open(caminho_txt, "w", encoding="utf-8") as f:
        f.write(texto)
    
    print(f"TXT criado: {caminho_txt}")


def extract_section_body(file_path: str, section_title_pattern: str) -> str or None:
    """
    Extrai o texto da seção específica (ex: 'indicações') de um PDF.
    Usa regex simples para detectar começo/fim da seção.
    """
    try:
        with pdfplumber.open(file_path) as pdf: 
            full_text = "" 
            for page in pdf.pages: 
                page_text = page.extract_text() 
                if page_text: 
                    full_text += page_text + "\n"
            
        # Corrige caracteres estranhos
        #full_text = full_text.replace("˙", "ç")
        criarpdf_TXT(file_path,full_text)
        
        # Regex: pega tudo a partir da seção até o próximo título (linha em CAPS ou fim do texto)
        pattern = re.compile(rf"({section_title_pattern})(.*?)(\n[A-Z][^\n]*:|\Z)", re.IGNORECASE | re.DOTALL)
     
        match = pattern.search(full_text)
        
        if match:
            return match.group(1).strip()+" " +match.group(2).strip()
        else:
            print(f"Seção '{section_title_pattern}' não encontrada em {file_path}")
            return None

    except Exception as e:
        print(f"Erro lendo {file_path}: {e}")
        return None


if __name__ == "__main__":
    print("Inicio: "+time.strftime("%H:%M:%S"))
    pasta_entrada = "pdfs"
    title_regex = r"indicações"
    palavras_chave = ["diabete", "diabetes"]
    palavras_chave2 = ["hipertensão", "hipertensões"]

    # Cria as pastas necessárias
    os.makedirs("diabetes", exist_ok=True)
    os.makedirs("hipertensao", exist_ok=True)
    os.makedirs("outros", exist_ok=True)
    os.makedirs("comparativo", exist_ok=True)
    os.makedirs("falha", exist_ok=True)
    os.makedirs("pdfsTXT", exist_ok=True)

    arquivos = glob.glob(os.path.join(pasta_entrada, "*.pdf"))

    if not arquivos:
        print(f"Nenhum PDF encontrado em: {pasta_entrada}")
    else:
        stemmer = RSLPStemmer()

        for document_path in arquivos:
            print(f"\nProcessando: {document_path}")
            texto_secao = extract_section_body(document_path, title_regex)

            if texto_secao:
                # Cria TXT comparativo
                escrever_txt(document_path, texto_secao)

                # Tokenização em português
                tokens = word_tokenize(texto_secao.lower(), language="portuguese")

                # Stemming (raízes das palavras)
                stems = [stemmer.stem(tok) for tok in tokens if tok.isalpha()]

                print("🔹 Tokens:", tokens[:20])
                print("🔹 Stems:", stems[:20])

                # Também reduz palavras-chave
                stems_chave = [stemmer.stem(p.lower()) for p in palavras_chave]
                stems_chave2 = [stemmer.stem(p.lower()) for p in palavras_chave2]

                if any(stem in stems for stem in stems_chave):
                    destino = "diabetes"
                elif any(stem in stems for stem in stems_chave2):
                    destino = "hipertensao"
                else:
                    destino = "outros"
            else:
                destino = "falha"

            # Move PDF para a pasta correta
            novo_caminho = os.path.join(destino, os.path.basename(document_path))
            shutil.move(document_path, novo_caminho)
            print(f"Movido para: {novo_caminho}")

    print("Fim: "+time.strftime("%H:%M:%S"))