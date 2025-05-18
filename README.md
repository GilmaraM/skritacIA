# Skriva ✍️

[![Licença: MIT](https://img.shields.io/badge/Licen%C3%A7a-MIT-yellow.svg)](https://opensource.org/licenses/MIT) <!-- Opcional: Badge de Licença -->
[![Feito com Streamlit](https://static.streamlit.io/badges/streamlit_badge_md_white.svg)](https://streamlit.io) <!-- Opcional: Badge Streamlit -->

## Sobre o Projeto ✨

Este é um **Assistente de Escrita com Inteligência Artificial** desenvolvido em Python utilizando o framework Streamlit para a interface gráfica e a API do Google Gemini para as funcionalidades de geração e aprimoramento de texto.

Cansado da página em branco? Diga adeus ao bloqueio criativo e olá à produtividade! 💡
O projeto foi criado para auxiliar usuários (estudantes, profissionais ou criadores de conteúdo) na criação e revisão de diversos tipos de texto, de forma rápida e eficaz.
Skrita não é apenas um corretor ortográfico, é seu parceiro de escrita completo. Imagine ter um assistente pessoal que: Gera e organiza suas ideias com Refinamento, Edição e Adaptação de Estilo com Criatividade sem Limites. 
 Obs: Construído para expandir sua criatividade, não para substituí-la!


## Funcionalidades

*   **Geração de Texto:** Crie diferentes tipos de texto (Artigos Acadêmicos, E-mails, Posts para Redes Sociais, Conteúdo de Marketing, Roteiros, Descrições de Produto) com opções de tom (Formal, Amigável, Persuasivo, Técnico, Criativo, Neutro) baseado em um tema/assunto.
*   **Correção e Aprimoramento:** Cole um texto existente para que a IA o revise (ortografia, gramática, fluidez) e sugira melhorias, mantendo o significado original.
*   **Controle de Parâmetros:** Ajuste parâmetros da IA como limite de tokens e temperatura para influenciar o tamanho e a criatividade das respostas.
*   **Salvar:** Baixe os textos gerados ou revisados nos formatos `.txt` ou `.docx`.
*   **Histórico da Sessão:** Visualize os textos gerados e corrigidos durante a sessão atual do aplicativo.
*   **Interface Amigável:** Interface web simples e intuitiva criada com Streamlit.

## Tecnologias Utilizadas

*   Python
*   Streamlit
*   Google Generative AI SDK
*   python-dotenv
*   python-docx

## Como Rodar Localmente

Para rodar este projeto no seu computador:

1.  Clone este repositório:
    ```bash
    git clone https://github.com/GilmaraM/skritacIA.git
    cd skritacIA # Navegue até a pasta do projeto
    ```
2.  Crie e ative um ambiente virtual (recomendado Python 3.8+):
    ```bash
    python -m venv .venv
    # No Windows:
    .\.venv\Scripts\activate
    # No macOS/Linux:
    source .venv/bin/activate
    ```
3.  Instale as dependências:
    ```bash
    pip install -r requirements.txt
    ```
4.  Obtenha sua chave de API do Google AI Studio (ou Vertex AI) e crie um arquivo `.env` na raiz do projeto com o seguinte conteúdo:
    ```dotenv
    GOOGLE_API_KEY='SUA_CHAVE_REAL_AQUI'
    ```
    **Não compartilhe este arquivo publicamente!**
5.  Execute o aplicativo Streamlit:
    ```bash
    streamlit run streamlit_app.py
    ```
O aplicativo será aberto no seu navegador (geralmente em `http://localhost:8501`).

## Deploy (Streamlit Community Cloud)

Este aplicativo pode ser facilmente implantado gratuitamente na [Streamlit Community Cloud](https://streamlit.io/cloud).

1.  O código já está no GitHub.
2.  Crie uma conta ou faça login na [Streamlit Community Cloud](https://share.streamlit.io/).
3.  Crie um novo aplicativo apontando para este repositório GitHub (`https://github.com/GilmaraM/skritacIA.git`), branch `main`, e arquivo principal `streamlit_app.py`.
4.  **Importante:** Na seção "Advanced settings" -> "Secrets", adicione sua chave de API do Google Gemini no seguinte formato:
    ```
    [secrets]
    GOOGLE_API_KEY = "SUA_CHAVE_REAL_AQUI"
    ```
5.  Clique em "Deploy!".

## Contato

Se tiver dúvidas, sugestões ou problemas, sinta-se à vontade para entrar em contato com o criador:

E-mail: scribble.suport.flow@gmail.com

## Licença

Este projeto está licenciado sob a Licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes. 

---

*Desenvolvido com 💙 e IA.*
