# Início do Arquivo streamlit_app.py - Com Histórico da Sessão

import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
import docx
from docx import Document
import io
import datetime # <-- Adicionado: Import para usar data e hora

# --- Configuração e Funções ---

# 1. Carregar a chave de API do arquivo .env e configurar Google AI
load_dotenv()
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

if not GOOGLE_API_KEY:
    st.error("Erro: Chave de API do Google não encontrada no arquivo .env.")
    st.error("Por favor, adicione GOOGLE_API_KEY='sua_chave_aqui' ao seu arquivo .env")
    st.stop()

genai.configure(api_key=GOOGLE_API_KEY)

# Nome do modelo padrão para usar - **VERIFIQUE SE ESTÁ CORRETO PARA SUA CHAVE!**
default_model_name = 'models/gemini-1.5-flash' # <--- Nome do modelo definido aqui


# Função auxiliar para salvar texto (retorna dados para download)
def to_txt(text_content):
    """Converte texto para bytes em formato TXT com encoding UTF-8."""
    return text_content.encode('utf-8')

def to_docx(text_content):
    """Cria um documento DOCX na memória (BytesIO) a partir de texto."""
    document = Document()
    for paragraph in text_content.split('\n'):
        document.add_paragraph(paragraph)
    buffer = io.BytesIO()
    document.save(buffer)
    buffer.seek(0)
    return buffer.getvalue()


# Função para interagir com o modelo Gemini (geral para geração e correção)
def interagir_com_gemini(prompt, max_tokens, temperature, top_p=0.9, top_k=0):
    """Envia um prompt para o modelo Gemini e retorna a resposta."""
    try:
        model = genai.GenerativeModel(default_model_name)

        generation_config = genai.GenerationConfig(
            max_output_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            top_k=top_k
        )

        response = model.generate_content(
            prompt,
            generation_config=generation_config
        )

        return response.text

    except Exception as e:
        st.error(f"Ocorreu um erro na interação com o modelo '{default_model_name}': {e}")
        st.warning("Verifique o nome do modelo no código, sua chave de API e conexão com a internet.")
        return None


# Dicionários de opções
tipos_texto_gerar = {
    'Artigo/Texto Acadêmico': 'Artigo/Texto Acadêmico',
    'E-mail Profissional': 'E-mail Profissional',
    'Post para Redes Sociais': 'Post para Redes Sociais',
    'Conteúdo de Marketing Digital': 'Conteúdo de Marketing Digital',
    'Roteiro Simples': 'Roteiro Simples',
    'Descrição de Produto': 'Descrição de Produto'
}

tons_disponiveis = {
    'Formal': 'Formal',
    'Amigável': 'Amigável',
    'Persuasivo': 'Persuasivo',
    'Técnico': 'Técnico',
    'Criativo': 'Criativo',
    'Neutro': 'Neutro'
}

# --- CSS Personalizado para o Fundo e Estilo ---
# Mantido como estava
custom_css = f"""
<style>
/* Define o fundo para preto no modo escuro/claro do Streamlit */
[data-theme="dark"], [data-theme="light"] {{
  background-color: #000000 !important;
  color: #ffffff; /* Garante que o texto padrão seja branco */
}}

/* Centraliza o conteúdo principal vertical e horizontalmente na tela */
.st-emotion-cache-eczf16 {{ /* Esta classe pode mudar com atualizações do Streamlit! */
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    min-height: 100vh; /* Ocupa pelo menos 100% da altura da viewport */
    padding: 20px; /* Adiciona um pouco de padding */
}}

/* Remove padding superior/inferior padrão do Streamlit que pode interferir */
.st-emotion-cache-1dp5vir {{ /* Esta classe pode mudar com atualizações do Streamlit! */
    padding-top: 0rem;
    padding-bottom: 0rem;
}}


/* Estilo para o título de boas-vindas */
.welcome-title {{
    font-size: 3em; /* Tamanho da fonte */
    color: #00aaff; /* Cor azul */
    text-align: center;
    margin-bottom: 10px; /* Espaço abaixo do título */
    /* Adicione sombra ou gradiente se quiser replicar o efeito visual exato */
    text-shadow: 0 0 5px #00aaff, 0 0 10px #00aaff; /* Exemplo de sombra azul */
}}

/* Estilo para o subtítulo (se houver) */
.welcome-subtitle {{
    font-size: 1.2em;
    color: #aaaaaa; /* Cor cinza claro */
    text-align: center;
    margin-bottom: 30px; /* Espaço abaixo do subtítulo */
}}


/* Estilo para o botão COMEÇAR */
.stButton > button {{
    background-image: linear-gradient(to right, #4e54c8, #8f94fb);
    color: white;
    font-size: 1.2em;
    padding: 10px 30px;
    border: none;
    border-radius: 25px;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: 0 0 10px rgba(143, 148, 251, 0.6), 0 0 20px rgba(143, 148, 251, 0.4);
    /* Centralização horizontal adicional para o botão dentro da coluna, se necessário */
    display: block;
    margin: 0 auto;
    width: fit-content;
}}

.stButton > button:hover {{
    background-image: linear-gradient(to right, #8f94fb, #4e54c8);
    box-shadow: 0 0 15px rgba(143, 148, 251, 0.8), 0 0 30px rgba(143, 148, 251, 0.6);
}}

.stButton > button:active {{
    background-image: linear-gradient(to right, #4e54c8, #8f94fb);
    box-shadow: none;
}}


/* CSS para garantir que a página de APP não fique centralizada verticalmente */
/* Precisamos identificar a classe correta para o contêiner principal da APP */
/* Este é um ajuste mais avançado e pode ser instável */
/* Como alternativa, podemos adicionar padding no topo da página APP */
/* st.write("<br>"*10, unsafe_allow_html=True) no topo da página APP */

</style>
"""

# Injeta o CSS personalizado
st.markdown(custom_css, unsafe_allow_html=True)


# --- Gerenciamento de Estado ---
# Inicializa o estado da página
if 'page' not in st.session_state:
    st.session_state.page = 'welcome'

# <-- Adicionado: Inicializa a lista do histórico da sessão se não existir
if 'history' not in st.session_state:
    st.session_state.history = []


# --- Layout da Página ---

# Mostra a Tela de Boas-Vindas
if st.session_state.page == 'welcome':
    welcome_content_container = st.container()
    with welcome_content_container:
        # Título e subtítulo
        st.markdown("<h1 class='welcome-title'>Bem-vindo(a) ao Skriva!</h1>", unsafe_allow_html=True)
        st.markdown("<p class='welcome-subtitle'>Serei seu Assistente de SKrita com IA</p>", unsafe_allow_html=True)

        # Botão para ir para o aplicativo principal
        col1, col2, col3 = st.columns([1, 3, 1])
        with col2:
            if st.button("COMEÇAR", key='start_button'):
                st.session_state.page = 'app'
                st.rerun() # Força re-execução

# Mostra a Tela do Aplicativo Principal
elif st.session_state.page == 'app':
    # --- Conteúdo do Aplicativo Principal ---

    # Nota: st.sidebar está desativado nesta versão

    st.title("Vamos começar?") # Mantém o título na página principal
    st.markdown("Use a inteligência artificial para gerar ou aprimorar seus textos.")

    # Usando abas para escolher a operação
    tab_gerar, tab_corrigir = st.tabs(["🚀 Gerar Novo Texto", "✨ Corrigir/Aprimorar Texto Existente"])

    # --- Seção Gerar ---
    with tab_gerar:
        col_tipo, col_tom = st.columns(2)
        with col_tipo:
            tipo_selecionado = st.selectbox("Tipo de Texto:", list(tipos_texto_gerar.keys()))
        with col_tom:
            tom_selecionado = st.selectbox("Tom:", list(tons_disponiveis.keys()))

        tema = st.text_input(f"Tema/Assunto para o '{tipo_selecionado}':")

        if st.button("Gerar Texto", key='btn_gerar'):
            if not tema:
                st.warning("Por favor, digite um tema/assunto.")
            else:
                prompt_geracao = f"""Crie um texto completo e bem estruturado do tipo "{tipo_selecionado}" sobre o tema/assunto: "{tema}"
                Use um tom "{tom_selecionado}".
                Não use gírias, palavrões ou termos complexos demais a menos que o tema ou o tom técnico exijam e sejam explicados.
                Responda em formato Markdown.
                """
                temp = 0.7
                max_tok = 1000
                top_p_val = 0.9
                top_k_val = 0

                if tipo_selecionado == 'Artigo/Texto Acadêmico':
                     prompt_geracao += "\nInclua introdução, desenvolvimento com argumentos e exemplos relevantes, e conclusão. Mantenha a formalidade e objetividade."
                     temp = 0.6
                     max_tok = 1800
                     top_p_val = 0.95
                     top_k_val = 50
                elif tipo_selecionado == 'E-mail Profissional':
                     prompt_geracao += "\nFormate a resposta como um e-mail profissional pronto para envio, com linhas para Assunto: e Corpo:."
                     temp = 0.5
                     max_tok = 800
                     top_p_val = 0.9
                     top_k_val = 0
                elif tipo_selecionado == 'Post para Redes Sociais':
                     prompt_geracao += "\nSeja conciso (máximo 280 caracteres se for Twitter, ajuste para outras redes), use linguagem engajadora e inclua hashtags relevantes ao tema."
                     temp = 0.8
                     max_tok = 400
                     top_p_val = 0.9
                     top_k_val = 0
                elif tipo_selecionado == 'Conteúdo de Marketing Digital':
                     prompt_geracao += "\nFoque nos benefícios, crie urgência ou desejo e inclua uma chamada para ação (call to action) clara relevante ao tema/produto/serviço."
                     temp = 0.9
                     max_tok = 1000
                     top_p_val = 0.9
                     top_k_val = 0
                elif tipo_selecionado == 'Roteiro Simples':
                     prompt_geracao += "\nFormate como um roteiro básico, com indicação de cenas, diálogos e ações."
                     temp = 0.8
                     max_tok = 1200
                     top_p_val = 0.95
                     top_k_val = 50
                elif tipo_selecionado == 'Descrição de Produto':
                     prompt_geracao += "\nDescreva as características e benefícios do produto de forma atraente para um público comprador."
                     temp = 0.7
                     max_tok = 600
                     top_p_val = 0.9
                     top_k_val = 0

                with st.spinner("Gerando texto..."):
                    texto_novo = interagir_com_gemini(prompt_geracao, max_tok, temp, top_p_val, top_k_val)

                if texto_novo:
                    st.subheader("📝 Texto Gerado:")
                    st.markdown(texto_novo)

                    # <-- Adicionado: Adiciona ao histórico da sessão na Geração
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    st.session_state.history.append({
                        'type': 'Gerado',
                        'timestamp': timestamp,
                        'content': texto_novo,
                        'details': f'Tema: {tema}, Tipo: {tipo_selecionado}, Tom: {tom_selecionado}'
                    })
                    # Adiciona timestamp às chaves dos botões para evitar conflitos se gerar rápido
                    dl_key_txt = f'dl_txt_gerar_{timestamp}'
                    dl_key_docx = f'dl_docx_gerar_{timestamp}'


                    st.subheader("💾 Salvar Texto:")
                    col_txt_gerar, col_docx_gerar = st.columns(2)
                    with col_txt_gerar:
                        st.download_button(
                            label="📥 Baixar como TXT",
                            data=to_txt(texto_novo),
                            file_name=f"{tema[:50].replace(' ', '_')}_gerado.txt",
                            mime="text/plain",
                            key=dl_key_txt # Usando a chave única
                        )
                    with col_docx_gerar:
                        try:
                            docx_data = to_docx(texto_novo)
                            st.download_button(
                                label="📥 Baixar como DOCX",
                                data=docx_data,
                                file_name=f"{tema[:50].replace(' ', '_')}_gerado.docx",
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                key=dl_key_docx # Usando a chave única
                            )
                        except Exception as e:
                             st.warning(f"Não foi possível gerar DOCX para download: {e}")


    # --- Seção Corrigir ---
    with tab_corrigir:
        texto_original = st.text_area("Cole o texto que você quer corrigir aqui:", height=300)
        tom_selecionado_correcao = st.selectbox("Tom para a revisão/sugestões:", list(tons_disponiveis.keys()), index=0)

        if st.button("Corrigir Texto", key='btn_corrigir'):
            if not texto_original:
                st.warning("Por favor, cole o texto para corrigir.")
            else:
                prompt_correcao = f"""Por favor, revise e aprimore o seguinte texto.
                Use um tom {tom_selecionado_correcao} na revisão e nas sugestões.
                Corrija erros de ortografia, gramática, pontuação e dê sugestões para melhorar a clareza, a coesão e a fluidez. Mantenha o significado original do texto.
                Não use gírias, palavrões ou termos complexos demais a menos que o texto original já os contenha e seja necessário revisá-los.
                Forneça o texto revisado e, em uma seção separada marcada como "Sugestões:", liste as sugestões de melhoria em tópicos numerados.
                Responda em formato Markdown.

                Texto a revisar:
                {texto_original}

                Texto revisado:
                """
                temp = 0.5
                max_tok = 1500
                top_p_val = 0.9
                top_k_val = 0

                with st.spinner("Corrigindo e aprimorando texto..."):
                     texto_revisado_completo = interagir_com_gemini(prompt_correcao, max_tok, temp, top_p_val, top_k_val)

                if texto_revisado_completo:
                    st.subheader("✨ Texto Revisado e Sugestões:")
                    st.markdown(texto_revisado_completo)

                    # <-- Adicionado: Adiciona ao histórico da sessão na Correção
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    st.session_state.history.append({
                        'type': 'Corrigido',
                        'timestamp': timestamp,
                        'content': texto_revisado_completo,
                        'details': f'Tom: {tom_selecionado_correcao}'
                    })
                    # Adiciona timestamp às chaves dos botões para evitar conflitos
                    dl_key_txt_corr = f'dl_txt_corrigir_{timestamp}'
                    dl_key_docx_corr = f'dl_docx_corrigir_{timestamp}'


                    st.subheader("💾 Salvar Texto Revisado:")
                    col_txt_corrigir, col_docx_corrigir = st.columns(2)
                    with col_txt_corrigir:
                         st.download_button(
                             label="📥 Baixar como TXT",
                             data=to_txt(texto_revisado_completo),
                             file_name=f"texto_revisado.txt",
                             mime="text/plain",
                             key=dl_key_txt_corr # Usando a chave única
                         )
                    with col_docx_corrigir:
                        try:
                             docx_data = to_docx(texto_revisado_completo)
                             st.download_button(
                                 label="📥 Baixar como DOCX",
                                 data=docx_data,
                                 file_name=f"texto_revisado.docx",
                                 mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                  key=dl_key_docx_corr # Usando a chave única
                             )
                        except Exception as e:
                             st.warning(f"Não foi possível gerar DOCX para download: {e}")


    # <-- Adicionado: Seção Histórico da Sessão -->
    st.markdown("---") # Separador visual antes do histórico
    with st.expander("Histórico da Sessão 🕒"):
        if not st.session_state.history:
            st.info("O histórico da sessão está vazio. Gere ou corrija alguns textos!")
        else:
            # Exibe os itens do histórico (do mais recente para o mais antigo)
            for i, item in enumerate(reversed(st.session_state.history)):
                st.markdown(f"**{len(st.session_state.history) - i}. {item['type']}** ({item['timestamp']}) - *{item['details']}*")
                # Você pode escolher como exibir o conteúdo:
                # st.text(item['content'][:200] + '...') # Exibe as primeiras 200 chars
                # Ou exibe o conteúdo completo:
                # st.markdown(item['content']) # <- Descomente esta linha para mostrar o conteúdo completo
                st.markdown("---") # Separador entre itens do histórico (opcional)


            # Botão para limpar o histórico
            if st.button("Limpar Histórico da Sessão"):
                st.session_state.history = [] # Limpa a lista
                st.rerun() # Força a atualização da página para mostrar o histórico vazio
    # <-- Fim da Seção Histórico da Sessão -->


    # --- Seção de Ajuda (Usando Expander) - Aparece na tela 'app' ---
    with st.expander("Precisa de Ajuda? 💡"):
        st.write("""
        Olá! Sou seu assistente de escrita com IA. Se você tiver alguma dúvida sobre como usar esta ferramenta, sugestões de melhoria, ou encontrar algum problema, por favor, entre em contato.

        Ficarei feliz em ajudar. 😊

        **Contato com o Criador:**
        E-mail: **scribble.suport.flow@gmail.com** #
        """
        )

    # --- Informação do modelo no final - Aparece na tela 'app' ---
    st.markdown("---") # Linha separadora visual
    st.caption(f"Modelo AI usado: {default_model_name}")


# --- Fim do Arquivo streamlit_app.py ---