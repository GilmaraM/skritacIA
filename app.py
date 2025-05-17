# Início do Arquivo

import google.generativeai as genai
import os
from dotenv import load_dotenv
import docx
from docx import Document
import streamlit as st
from io import BytesIO
import sqlite3 # Importa a biblioteca SQLite
from datetime import datetime # Para registrar a data/hora


# --- Configuração SQLite para Histórico ---
DATABASE_NAME = 'gerai_history.db'

def init_db():
    """Inicializa o banco de dados SQLite e cria a tabela de histórico se não existir."""
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                operation_type TEXT, -- 'gerar' ou 'corrigir'
                model_used TEXT,
                input_text TEXT, -- Tema para gerar, Texto original para corrigir
                output_text TEXT, -- Texto gerado/revisado
                text_type TEXT, -- Tipo de texto (Artigo, Email, etc.) - para gerar
                tone TEXT -- Tom (Formal, Amigável, etc.)
                -- Poderiam adicionar mais colunas conforme necessário (ex: max_tokens, temperature)
            )
        ''')
        conn.commit()
        conn.close()
    except Exception as e:
        st.error(f"Erro ao inicializar o banco de dados: {e}")

def save_interaction(operation_type, model_used, input_text, output_text, text_type=None, tone=None):
    """Salva uma interação no banco de dados."""
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S') # Formato YYYY-MM-DD HH:MM:SS

        cursor.execute('''
            INSERT INTO interactions (timestamp, operation_type, model_used, input_text, output_text, text_type, tone)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (timestamp, operation_type, model_used, input_text, output_text, text_type, tone))

        conn.commit()
        conn.close()
        # st.success("Interação salva no histórico!") # Mensagem opcional de sucesso
    except Exception as e:
        st.error(f"Erro ao salvar interação no histórico: {e}")

def load_interactions(limit=20):
    """Carrega as interações mais recentes do banco de dados."""
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        # Ordena por timestamp em ordem decrescente (mais recente primeiro)
        cursor.execute('SELECT * FROM interactions ORDER BY timestamp DESC LIMIT ?', (limit,))
        interactions = cursor.fetchall() # Pega todos os resultados
        conn.close()
        return interactions
    except Exception as e:
        st.error(f"Erro ao carregar histórico: {e}")
        return [] # Retorna lista vazia em caso de erro

# Inicializa o banco de dados quando o script Streamlit inicia
init_db()
# --- Fim Configuração SQLite ---


# --- Configuração da API Google AI ---
load_dotenv()
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

# Verifica se a chave foi encontrada
if not GOOGLE_API_KEY:
    st.error("Erro: Chave de API do Google não encontrada no arquivo .env.")
    st.info("Por favor, adicione GOOGLE_API_KEY='sua_chave_aqui' ao seu arquivo .env na raiz do projeto.")
    st.stop() # Para a execução do script Streamlit aqui

# Configura a ferramenta do Google Gemini com a sua chave
genai.configure(api_key=GOOGLE_API_KEY)

# Nome do modelo padrão para usar - **SUBSTITUA PELO NOME CORRETO DA SUA LISTA!**
# Ex: 'models/gemini-1.5-flash' ou 'models/gemini-1.5-pro'
default_model_name = 'models/gemini-1.5-flash' # <--- VERIFIQUE/SUBSTITUA ESTE NOME SE NECESSÁRIO

# Mostra o modelo usado na barra lateral (opcional)
st.sidebar.info(f"Modelo usado: {default_model_name}")
# --- Fim Configuração da API ---


# Função auxiliar para interagir com o modelo Gemini
# Esta função agora VAI LEVANTAR exceções em caso de erro, para que o chamador possa capturá-las.
def interagir_com_gemini(prompt, max_tokens, temperature, top_p=0.9, top_k=0):
    """Envia um prompt para o modelo Gemini e retorna a resposta. Levanta exceção em caso de erro."""
    model = genai.GenerativeModel(default_model_name)

    generation_config = genai.GenerationConfig(
        max_output_tokens=max_tokens,
        temperature=temperature,
        top_p=top_p,
        top_k=top_k
    )

    # AQUI: removemos o try...except interno. Deixamos a exceção "caminhar" para o chamador.
    response = model.generate_content(
        prompt,
        generation_config=generation_config
    )

    return response.text

# Função auxiliar para preparar DOCX para download
def to_docx_buffer(text_content):
    """Cria um documento DOCX na memória a partir de um texto."""
    document = Document()
    for paragraph in text_content.split('\n'):
         document.add_paragraph(paragraph)
    buffer = BytesIO()
    document.save(buffer)
    buffer.seek(0)
    return buffer


# --- Lógica da Interface Streamlit ---
st.title("GerAI - Seu Assistente de Escrita com IA") # Título principal

# --- Opções de Operação (Gerar ou Corrigir) ---
# Usamos st.sidebar para colocar as opções na barra lateral
operacao = st.sidebar.radio("O que gostaria de fazer?", ["Gerar um novo texto", "Corrigir/Aprimorar um texto existente", "Ver Histórico"]) # Adicionado opção Histórico

# --- Se a operação escolhida for Gerar Texto ---
if operacao == "Gerar um novo texto":
    st.header("Gerar Novo Texto") # Título da seção

    # --- Inputs para Geração ---
    tipos_texto_gerar = { # Usamos chaves numéricas, mas o selectbox usa os valores como labels
        '1': 'Artigo/Texto Acadêmico',
        '2': 'E-mail Profissional',
        '3': 'Post para Redes Sociais (Ideias e Sugestões)',
        '4': 'Conteúdo de Marketing Digital (Ideias, sugestões, descrição de Produto)',
        '5': 'Roteiro Simples (Viagens entre outros)',
        '6': 'Descrição de Produto'
    }
    # Obtemos o nome da opção selecionada diretamente pelo valor do dicionário
    tipo_selecionado_label = st.selectbox("Escolha o tipo de texto a gerar:", list(tipos_texto_gerar.values()))
    # Encontramos a chave numérica correspondente (útil para salvar no DB se necessário, ou apenas o label)
    tipo_selecionado_key = list(tipos_texto_gerar.keys())[list(tipos_texto_gerar.values()).index(tipo_selecionado_label)]


    tons_disponiveis = {
        '1': 'Formal', '2': 'Amigável', '3': 'Persuasivo',
        '4': 'Técnico', '5': 'Criativo', '6': 'Neutro'
    }
    # Obtemos o nome do tom selecionado
    tom_selecionado_label = st.selectbox("Escolha o tom para o texto:", list(tons_disponiveis.values()))
    # Encontramos a chave numérica correspondente (opcional)
    tom_selecionado_key = list(tons_disponiveis.keys())[list(tons_disponiveis.values()).index(tom_selecionado_label)]


    tema = st.text_input("Certo, qual tema/assunto deve ter o seu texto?")

    # --- Botão para acionar a geração ---
    if st.button("Gerar Texto"):
        if not tema:
            st.warning("Por favor, digite um tema/assunto.")
        else:
            # --- Lógica de construção do prompt e chamada da API ---
            prompt_base = f"""Crie um texto completo e bem estruturado do tipo "{tipo_selecionado_label}" sobre o tema/assunto: "{tema}"
            Use um tom "{tom_selecionado_label}".
            Não use gírias, palavrões ou termos complexos demais a menos que o tema ou o tom técnico exijam e sejam explicados.
            Responda em formato Markdown.
            """
            # Ajustes de parâmetros padrão para geração
            temp = 0.7
            max_tok = 1000 # Limite padrão para geração
            top_p_val = 0.9
            top_k_val = 0

            # Adiciona instruções e ajusta parâmetros específicos baseados no tipo de texto
            if tipo_selecionado_label == 'Artigo/Texto Acadêmico':
                 prompt_base += "\nInclua introdução, desenvolvimento com argumentos e exemplos relevantes, e conclusão. Mantenha a formalidade e objetividade."
                 temp = 0.6
                 max_tok = 1800
                 top_p_val = 0.95
                 top_k_val = 50
            elif tipo_selecionado_label == 'E-mail Profissional':
                 prompt_base += "\nFormate a resposta como um e-mail profissional pronto para envio, com linhas para Assunto: e Corpo:."
                 temp = 0.5
                 max_tok = 800
                 top_p_val = 0.9
                 top_k_val = 0
            elif 'Post para Redes Sociais' in tipo_selecionado_label:
                 prompt_base += "\nSeja conciso (máximo 280 caracteres se for Twitter, ajuste para outras redes), use linguagem engajadora e inclua hashtags relevantes ao tema."
                 temp = 0.8
                 max_tok = 400
                 top_p_val = 0.9
                 top_k_val = 0
            elif 'Marketing Digital' in tipo_selecionado_label:
                 prompt_base += "\nFoque nos benefícios, crie urgência ou desejo e inclua uma chamada para ação (call to action) clara relevante ao tema/produto/serviço."
                 temp = 0.9
                 max_tok = 1000
                 top_p_val = 0.9
                 top_k_val = 0
            elif 'Roteiro Simples' in tipo_selecionado_label:
                 prompt_base += "\nFormate como um roteiro básico, com indicação de cenas, diálogos e ações."
                 temp = 0.8
                 max_tok = 1200
                 top_p_val = 0.95
                 top_k_val = 50
            elif tipo_selecionado_label == 'Descrição de Produto':
                 prompt_base += "\nDescreva as características e benefícios do produto de forma atraente para um público comprador."
                 temp = 0.7
                 max_tok = 600
                 top_p_val = 0.9
                 top_k_val = 0

            # --- CHAMADA PARA A API COM TRATAMENTO DE ERRO MELHORADO ---
            texto_gerado = None # Inicializa a variável
            try:
                with st.spinner("Gerando texto..."):
                     texto_gerado = interagir_com_gemini(prompt_base, max_tok, temp, top_p_val, top_k_val)
                # Se a API retornar uma mensagem de erro (começando com "Ocorreu um erro..."), mostre como erro
                if texto_gerado and texto_gerado.startswith("Ocorreu um erro"):
                     st.error(texto_gerado)
                     texto_gerado = None # Limpa o texto gerado se for uma mensagem de erro
                elif texto_gerado: # Se não for erro e tiver texto
                    st.subheader("Texto Gerado:")
                    st.write(texto_gerado) # Exibe o texto gerado

                    # Salva no histórico
                    save_interaction('gerar', default_model_name, tema, texto_gerado, tipo_selecionado_label, tom_selecionado_label)

            except Exception as e: # Captura qualquer outro erro durante a chamada ou processamento
                st.error(f"Ocorreu um erro inesperado durante a geração: {e}")


            # --- Botões de Download ---
            if texto_gerado: # Só mostra os botões se tiver texto gerado com sucesso
                 st.markdown("---") # Linha separadora
                 st.subheader("Salvar Texto")

                 # Download TXT
                 nome_sugerido_txt = f"gerai_{tipo_selecionado_label.replace(' ', '_').replace('/', '-')}_gerado.txt"
                 st.download_button(
                     label="Download como TXT",
                     data=texto_gerado,
                     file_name=nome_sugerido_txt,
                     mime="text/plain"
                 )

                 # Download DOCX
                 try:
                     docx_buffer = to_docx_buffer(texto_gerado)
                     nome_sugerido_docx = f"gerai_{tipo_selecionado_label.replace(' ', '_').replace('/', '-')}_gerado.docx"
                     st.download_button(
                         label="Download como DOCX",
                         data=docx_buffer,
                         file_name=nome_sugerido_docx,
                         mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                     )
                 except Exception as e:
                      st.error(f"Erro ao preparar DOCX para download: {e}")


# --- Se a operação escolhida for Corrigir Texto ---
elif operacao == "Corrigir/Aprimorar um texto existente":
    st.header("Corrigir/Aprimorar Texto") # Título da seção

    # --- Inputs para Correção ---
    texto_original = st.text_area("Cole o texto aqui:", height=200)

    tons_disponiveis_correcao = { # Usamos os mesmos tons
        '1': 'Formal', '2': 'Amigável', '3': 'Persuasivo',
        '4': 'Técnico', '5': 'Criativo', '6': 'Neutro'
    }
    # Obtemos o nome do tom selecionado
    tom_selecionado_correcao_label = st.selectbox("Escolha o tom para a revisão/sugestões:", list(tons_disponiveis_correcao.values()))
    # Encontramos a chave numérica correspondente (opcional)
    tom_selecionado_correcao_key = list(tons_disponiveis_correcao.keys())[list(tons_disponiveis_correcao.values()).index(tom_selecionado_correcao_label)]


    # --- Botão para acionar a correção ---
    if st.button("Corrigir Texto"):
        if not texto_original:
            st.warning("Por favor, cole o texto para corrigir.")
        else:
             # --- Lógica de construção do prompt e chamada da API ---
             prompt_correcao = f"""Por favor, revise e aprimore o seguinte texto.
             Use um tom {tom_selecionado_correcao_label} na revisão e nas sugestões.
             Corrija erros de ortografia, gramática, pontuação e dê sugestões para melhorar a clareza, a coesão e a fluidez. Mantenha o significado original do texto.
             Não use gírias, palavrões ou termos complexos demais a menos que o texto original já os contenha e seja necessário revisá-los.
             Forneça o texto revisado e, em uma seção separada marcada como "Sugestões:", liste as sugestões de melhoria em tópicos numerados.
             Responda em formato Markdown.

             Texto a revisar:
             {texto_original}

             Texto revisado:
             """
             # Parâmetros para correção
             temp = 0.5
             max_tok = 1500
             top_p_val = 0.9
             top_k_val = 0

             # --- CHAMADA PARA A API COM TRATAMENTO DE ERRO MELHORADO ---
             texto_revisado_completo = None # Inicializa
             try:
                 with st.spinner("Corrigindo texto..."):
                      texto_revisado_completo = interagir_com_gemini(prompt_correcao, max_tok, temp, top_p_val, top_k_val)
                 # Se a API retornar uma mensagem de erro
                 if texto_revisado_completo and texto_revisado_completo.startswith("Ocorreu um erro"):
                      st.error(texto_revisado_completo)
                      texto_revisado_completo = None # Limpa o resultado se for erro
                 elif texto_revisado_completo: # Se não for erro e tiver texto
                     st.subheader("Texto Revisado e Sugestões:")
                     st.write(texto_revisado_completo) # st.write exibe o resultado

                     # Salva no histórico
                     save_interaction('corrigir', default_model_name, texto_original[:200] + '...' if len(texto_original) > 200 else texto_original, texto_revisado_completo, None, tom_selecionado_correcao_label) # Salva input truncado se for muito longo

             except Exception as e: # Captura qualquer outro erro
                 st.error(f"Ocorreu um erro inesperado durante a correção: {e}")


             # --- Botões de Download ---
             if texto_revisado_completo: # Só mostra botões se tiver texto gerado com sucesso
                  st.markdown("---") # Linha separadora
                  st.subheader("Salvar Texto Revisado")

                  # Download TXT
                  nome_sugerido_txt = f"gerai_revisado_{tom_selecionado_correcao_label.replace(' ', '_').replace('/', '-')}.txt"
                  st.download_button(
                      label="Download como TXT",
                      data=texto_revisado_completo,
                      file_name=nome_sugerido_txt,
                      mime="text/plain"
                  )

                  # Download DOCX
                  try:
                      docx_buffer = to_docx_buffer(texto_revisado_completo)
                      nome_sugerido_docx = f"gerai_revisado_{tom_selecionado_correcao_label.replace(' ', '_').replace('/', '-')}.docx"
                      st.download_button(
                          label="Download como DOCX",
                          data=docx_buffer,
                          file_name=nome_sugerido_docx,
                          mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                      )
                  except Exception as e:
                       st.error(f"Erro ao preparar DOCX para download: {e}")


# --- Se a operação escolhida for Ver Histórico ---
elif operacao == "Ver Histórico":
    st.header("Histórico de Interações")

    # Carrega as interações do DB (pode ajustar o limite)
    interacoes = load_interactions(limit=50)

    if not interacoes:
        st.info("Nenhuma interação encontrada no histórico ainda.")
    else:
        # Exibe as interações
        # st.dataframe(interacoes) # Uma forma rápida, mas mostra todas as colunas e formato DB

        # Formato mais amigável para exibir histórico
        for i, interaction in enumerate(interacoes):
            # Desempacota os dados da linha do DB
            id, timestamp, op_type, model_used, input_text, output_text, text_type, tone = interaction

            # Cria um expander para cada interação para organizar
            header_text = f"#{id} - {timestamp} - {op_type.capitalize()}" # Ex: #1 - 2023-10-27 10:30:00 - Gerar

            # Adiciona informações extras no cabeçalho do expander
            if op_type == 'gerar':
                header_text += f" ({text_type}, {tone})"
            elif op_type == 'corrigir':
                 header_text += f" (Correção, {tone})"

            with st.expander(header_text):
                 st.write(f"**Modelo Usado:** {model_used}")
                 st.write(f"**Tipo:** {text_type if text_type else 'Correção'}") # Exibe tipo ou 'Correção'
                 st.write(f"**Tom:** {tone}")
                 st.write(f"**Input:**")
                 st.info(input_text) # Exibe input em caixa azul

                 st.write(f"**Output:**")
                 st.success(output_text) # Exibe output em caixa verde

                 # Opcional: Botões de download para cada item do histórico
                 # st.download_button(...) # Poderia adicionar botões aqui


# --- Nota de rodapé opcional ---
# st.sidebar.markdown("---")
# st.sidebar.info("Desenvolvido com 🤖 e Streamlit")