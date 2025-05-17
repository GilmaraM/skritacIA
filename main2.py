# Início do Arquivo

import google.generativeai as genai
import os
from dotenv import load_dotenv
import docx # Importa a biblioteca python-docx
from docx import Document # Importa a classe Document

# 1. Carregar a chave de API do arquivo .env e configurar Google AI
load_dotenv()
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

# Verifica se a chave foi encontrada
if not GOOGLE_API_KEY:
    print("Erro: Chave de API do Google não encontrada no arquivo .env.")
    print("Por favor, adicione GOOGLE_API_KEY='sua_chave_aqui' ao seu arquivo .env")
    exit()

# Configura a ferramenta do Google Gemini com a sua chave
genai.configure(api_key=GOOGLE_API_KEY)

# --- NOTA: O nome do modelo foi substituído por 'models/gemini-1.5-flash'
# Certifique-se que este nome está na lista de modelos que sua chave suporta!
# ---

# Nome do modelo padrão para usar - AGORA DEFINIDO COMO 'models/gemini-1.5-flash'!
default_model_name = 'models/gemini-1.5-flash' # <--- Nome do modelo definido aqui


# Função auxiliar para salvar texto
def salvar_texto(texto_conteudo, tipo_texto):
    """Pergunta ao usuário se deseja salvar o texto e o salva em .txt ou .docx."""
    # A chamada para esta função ocorre após a exibição do texto gerado/revisado.
    # Se a pergunta de salvar não aparecer, o problema pode ser na forma
    # como o terminal lida com a entrada após exibir o texto da IA.

    salvar = input(f"\nDeseja salvar este {tipo_texto} gerado/revisado em um arquivo? (s/n): ").lower()

    if salvar == 's':
        # --- MUDANÇA AQUI: Adiciona linha vazia antes do input ---
        print()
        nome_arquivo_base = input(f"Digite o nome base para o arquivo (sem extensão): ")
        # --- FIM DA MUDANÇA ---

        if not nome_arquivo_base.strip():
            print("Nome de arquivo inválido. Salvamento cancelado.")
            return

        # --- MUDANÇA AQUI: Adiciona linha vazia antes do input ---
        print()
        formato_input = input("Escolha o formato (.txt ou .docx - em breve mais opções): ").lower()
        # --- FIM DA MUDANÇA ---

        # --- MUDANÇA AQUI: Remove o ponto inicial do formato input ---
        formato = formato_input.lstrip('.')
        # --- FIM DA MUDANÇA ---

        if formato not in ['txt', 'docx']:
            print("Formato inválido. Salvamento cancelado.")
            return

        nome_arquivo_completo = f"{nome_arquivo_base}.{formato}"

        try:
            if formato == 'txt':
                with open(nome_arquivo_completo, 'w', encoding='utf-8') as f:
                    f.write(texto_conteudo)
                print(f"Texto salvo com sucesso em {nome_arquivo_completo}")
            elif formato == 'docx':
                document = Document()
                # Adiciona o texto como parágrafos. Isso lida bem com quebras de linha.
                for paragraph in texto_conteudo.split('\n'):
                     document.add_paragraph(paragraph)
                document.save(nome_arquivo_completo)
                print(f"Texto salvo com sucesso em {nome_arquivo_completo}")

        except Exception as e:
            print(f"Erro ao salvar o arquivo: {e}")
            print(f"Verifique se você tem permissão para escrever nesta pasta.")
    else:
        # Mensagem se o usuário digitar 'n' ou outra coisa
        print("Salvamento cancelado pelo usuário.")


# 2. Função para interagir com o modelo Gemini (geral para geração e correção)
# Agora esta função recebe o prompt completo
def interagir_com_gemini(prompt, max_tokens, temperature, top_p=0.9, top_k=0):
    """Envia um prompt para o modelo Gemini e retorna a resposta."""
    try:
        model = genai.GenerativeModel(default_model_name)

        # Configuração da geração com parâmetros ajustados
        generation_config = genai.GenerationConfig(
            max_output_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p, # Adicionado para controlar foco
            top_k=top_k  # Adicionado para controlar foco
            # Nota: presence_penalty e frequency_penalty não são suportados para generate_content neste método
        )

        response = model.generate_content(
            prompt,
            generation_config=generation_config
        )

        # Retorna o texto gerado/processado pela IA
        return response.text

    except Exception as e:
        # Mensagem de erro mais detalhada
        return f"Ocorreu um erro na interação com o modelo '{default_model_name}': {e}\nVerifique o nome do modelo, sua chave de API e conexão com a internet."

# 3. Lógica principal e Interface (CLI)
def main():
    # --- MUDANÇA AQUI: Nova mensagem de boas-vindas ---
    print("Bem-vindo(a) ao GerAI, seu Assistente de Escrita com IA!")
    # --- FIM DA MUDANÇA ---
    # --- REMOVIDO: print(f"Usando o modelo: {default_model_name}") ---

    # Opções de tipo de texto para gerar (atualizadas com texto adicional)
    tipos_texto_gerar = {
        '1': 'Artigo/Texto Acadêmico',
        '2': 'E-mail Profissional',
        '3': 'Post para Redes Sociais (Ideias e Sugestões)', # <-- ATUALIZADO
        '4': 'Conteúdo de Marketing Digital (Ideias, sugestões, descrição de Produto)', # <-- ATUALIZADO
        '5': 'Roteiro Simples (Viagens entre outros)', # <-- ATUALIZADO
        '6': 'Descrição de Produto'
    }

    # Opções de tom para gerar e corrigir
    tons_disponiveis = {
        '1': 'Formal',
        '2': 'Amigável',
        '3': 'Persuasivo',
        '4': 'Técnico',
        '5': 'Criativo',
        '6': 'Neutro'
    }


    while True:
        # --- Nova mensagem do menu ---
        print("\nO que gostaria de fazer?")
        # --- FIM DA MUDANÇA ---

        # --- Adiciona uma linha vazia ANTES das opções ---
        print()
        # --- FIM DA MUDANÇA ---

        print("1. Gerar um novo texto")
        print("2. Corrigir/Aprimorar um texto existente")
        print("3. Sair")

        # --- Adiciona uma linha vazia ANTES do input ---
        print()
        escolha_operacao = input("Digite o número da sua escolha: ")
        # --- FIM DA MUDANÇA ---

        if escolha_operacao == '1': # Gerar texto
            # --- MUDANÇA AQUI: Nova formatação e espaços para opções de tipo ---
            print("\nEscolha o tipo de texto a gerar: ")
            print() # Espaço
            for key, value in tipos_texto_gerar.items():
                print(f"{key}. {value}")
            print() # Espaço
            escolha_tipo = input("Digite o número do tipo: ")
            # --- FIM DA MUDANÇA ---
            tipo_selecionado = tipos_texto_gerar.get(escolha_tipo)

            if not tipo_selecionado:
                print("Opção de tipo inválida. Voltando ao menu principal.")
                continue

            # --- MUDANÇA AQUI: Nova formatação e espaços para opções de tom ---
            print("\nEscolha o tom para o texto: ")
            print() # Espaço
            for key, value in tons_disponiveis.items():
                print(f"{key}. {value}")
            print() # Espaço
            escolha_tom = input("Digite o número do tom: ")
            # --- FIM DA MUDANÇA ---
            tom_selecionado = tons_disponiveis.get(escolha_tom)

            if not tom_selecionado:
                 print("Opção de tom inválida. Voltando ao menu principal.")
                 continue

            # --- MUDANÇA AQUI: Novo texto para o input do tema ---
            tema = input(f"Certo, qual tema/assunto deve ter o seu texto? ")
            # --- FIM DA MUDANÇA ---
            if not tema.strip():
                print("Por favor, digite um tema/assunto.")
                continue

            # --- Construção do prompt de geração dinâmica ---
            prompt_geracao = f"""Crie um texto completo e bem estruturado do tipo "{tipo_selecionado}" sobre o tema/assunto: "{tema}"
            Use um tom "{tom_selecionado}".
            Não use gírias, palavrões ou termos complexos demais a menos que o tema ou o tom técnico exijam e sejam explicados.
            Responda em formato Markdown.
            """
            # Ajustes de parâmetros padrão para geração
            temp = 0.7
            max_tok = 1000 # Limite padrão para geração
            top_p_val = 0.9
            top_k_val = 0

            # Adiciona instruções e ajusta parâmetros específicos baseados no tipo de texto
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
            elif 'Post para Redes Sociais' in tipo_selecionado: # Verifica se contém a frase
                 prompt_geracao += "\nSeja conciso (máximo 280 caracteres se for Twitter, ajuste para outras redes), use linguagem engajadora e inclua hashtags relevantes ao tema."
                 temp = 0.8
                 max_tok = 400
                 top_p_val = 0.9
                 top_k_val = 0
            elif 'Marketing Digital' in tipo_selecionado: # Verifica se contém a frase
                 prompt_geracao += "\nFoque nos benefícios, crie urgência ou desejo e inclua uma chamada para ação (call to action) clara relevante ao tema/produto/serviço."
                 temp = 0.9
                 max_tok = 1000
                 top_p_val = 0.9
                 top_k_val = 0
            elif 'Roteiro Simples' in tipo_selecionado: # Verifica se contém a frase
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
            # Note: Os parâmetros top_p e top_k definidos inicialmente
            # são usados como padrão se não forem sobrescritos aqui.


            print("\nGerando texto...") # Pequeno ajuste aqui para "Gerando texto..."
            # Chama a função genérica de interação com Gemini
            # Passa o prompt construído e os parâmetros de geração (ou defaults)
            texto_novo = interagir_com_gemini(prompt_geracao, max_tok, temp, top_p_val, top_k_val)

            print("\n--- Texto Gerado ---")
            print(texto_novo) # Imprime o texto gerado
            print("--------------------\n")

            # --- Chamada para salvar o texto gerado ---
            salvar_texto(texto_novo, tipo_selecionado)
            # --- FIM DA CHAMADA ---


        elif escolha_operacao == '2': # Corrigir texto
            print("Por favor, cole o texto que você quer corrigir.")
            # --- Mensagem de instrução de finalização ---
            print("Para finalizar a entrada, pressione Enter duas vezes.")
            # --- FIM DA MUDANÇA ---
            linhas_texto = []
            # Lógica de leitura de várias linhas. Espera uma linha vazia.
            # Pressionar Enter duas vezes *cria* a linha vazia.
            while True:
                try:
                    linha = input()
                    if not linha: # Uma linha vazia quebra o loop
                        break
                    # Adiciona a linha lida, removendo espaços em branco do início/fim
                    linhas_texto.append(linha.strip())
                except EOFError: # Permite finalizar com Ctrl+D ou Ctrl+Z
                     break

            texto_original = "\n".join(linhas_texto) # Junta as linhas em um único texto

            if not texto_original.strip(): # Verifica se algum texto foi realmente inserido
                print("Nenhum texto foi inserido para correção.")
                continue

            # --- MUDANÇA AQUI: Nova formatação e espaços para opções de tom ---
            print(f"\nEscolha o tom para a revisão/sugestões: ")
            print() # Espaço
            for key, value in tons_disponiveis.items():
                print(f"{key}. {value}")
            print() # Espaço
            escolha_tom_correcao = input("Digite o número do tom: ")
            # --- FIM DA MUDANÇA ---
            tom_selecionado_correcao = tons_disponiveis.get(escolha_tom_correcao, 'Formal') # Default para Formal

            # --- Construção do prompt de correção ---
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
            # Parâmetros para correção (geralmente menos criativo)
            temp = 0.5
            max_tok = 1500 # Limite um pouco maior para o texto revisado + sugestões
            top_p_val = 0.9
            top_k_val = 0


            print("\nCorrigindo e aprimoramento texto...") # Pequeno ajuste para "aprimoramento"
            # Chama a função genérica de interação com Gemini
            texto_revisado_completo = interagir_com_gemini(prompt_correcao, max_tok, temp, top_p_val, top_k_val)

            print("\n--- Texto Revisado e Sugestões ---")
            print(texto_revisado_completo) # Imprime o resultado completo (revisão + sugestões)
            print("-----------------------------------\n")

            # --- Chamada para salvar o texto revisado ---
            salvar_texto(texto_revisado_completo, "texto revisado")
            # --- FIM DA CHAMADA ---


        elif escolha_operacao == '3': # Sair
            # --- Nova mensagem de saída ---
            print("Obrigado por usar o GerAI. Até mais!")
            # --- FIM DA MUDANÇA ---
            break # Sai do loop principal

        else:
            # --- Correção do erro de digitação ---
            print("Opção inválida. Por favor, tente novamente.")
            # --- FIM DA MUDANÇA ---

# Esta parte garante que a função main() seja chamada apenas quando você
# executar este arquivo diretamente.
if __name__ == "__main__":
    main()