import datetime
import glob
import os
import re
import shutil
from datetime import datetime

import pandas as pd
import spacy
from spacy_layout import spaCyLayout


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
    
    

def extract_section_body(file_path: str, lemma_titulo: str) -> dict or None:
    """
    Extrai todo o conteúdo (texto e tabelas) de uma seção específica de um documento.
    """
    nlp_pt = spacy.load("pt_core_news_sm")
    nlp_layout = spacy.blank("pt")
    layout = spaCyLayout(nlp_layout)


    try:
        doc = layout(file_path)

        section_body_text = []
        section_body_tables = []
        
        in_target_section = False

        for span in doc.spans["layout"]:

            titulo_extraido = span.text
            titulo_corrigido = titulo_extraido.replace("˙","ç")
            doc_titulo_extraido = nlp_pt(titulo_corrigido)
            lemmas_titulo = [token.lemma_.lower() for token in doc_titulo_extraido]


            if span.label_ == "section_header" and :
                in_target_section = True
                print(f"Seção '{titulo_corrigido}' encontrada. Extraindo conteúdo...")
                continue

            if in_target_section:
                if span.label_ == "section_header" and not ():
                    print(f"Fim da seção '{titulo_corrigido}'. Interrompendo a extração.")
                    break

                if span.label_ == "text":
                    section_body_text.append(titulo_corrigido)
                
                if span.label_ == "list_item":
                    section_body_text.append(titulo_corrigido)
                
                if span.label_ == "table":
                    if hasattr(span._, 'data') and span._.data is not None:
                        section_body_tables.append(span._.data)
                    else:
                        print(f"Aviso: Tabela encontrada mas sem dados extraídos do span: '{titulo_corrigido}'.")

        if not in_target_section:
            print(f"Seção com o padrão não encontrada no arquivo: {file_path}")
            return None
        else:
            return {
                "text": "\n".join(section_body_text),
                "tables": section_body_tables
            }
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")
    
if __name__ == "__main__":
    current_datetime = datetime.now()
    current_time = current_datetime.time()

    nlp_pt = spacy.load("pt_core_news_sm")
    pasta_entrada = "pdfs"
    lemma_titulo = nlp_pt("indicações")
    palavras_chave = ["diabete","diabetes"]
    palavras_chave2 = ["hipertensão","hipertensões"]
    
    

    # Cria todas as pastas necessárias
    os.makedirs("diabetes", exist_ok=True)
    os.makedirs("outros", exist_ok=True)
    os.makedirs("hipertensao", exist_ok=True)
    os.makedirs("comparativo", exist_ok=True)
    os.makedirs("falha", exist_ok=True)

    arquivos = glob.glob(os.path.join(pasta_entrada, "*.pdf"))


    if not arquivos:
        print(f"Nenhum PDF encontrado em: {pasta_entrada}")
    else:
        for document_path in arquivos:
            
            extracted_content = extract_section_body(document_path, lemma_titulo)

            if extracted_content:
                texto_secao = extracted_content["text"] or ""

                # Cria o arquivo TXT com a seção extraída
                escrever_txt(document_path, texto_secao)

                # Processa o texto com spaCy para extrair lemas
                doc_pt = nlp_pt(texto_secao)
                lemmas_texto = [token.lemma_.lower() for token in doc_pt]

                if any(palavra.lower() in lemmas_texto for palavra in palavras_chave):
                    destino = "diabetes"
                elif any(palavra.lower() in lemmas_texto for palavra in palavras_chave2):
                    destino = "hipertensao"
                else:
                    destino = "outros"
            else:
                # Se a seção não for encontrada, move para a pasta 'falha'
                destino = "falha"

            # Move o arquivo PDF
            novo_caminho = os.path.join(destino, os.path.basename(document_path))
            shutil.move(document_path, novo_caminho)

    current_datetime = datetime.now()
    current_time = current_datetime.time()
    print(current_time)

