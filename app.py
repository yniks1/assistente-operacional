import streamlit as st
import os
import warnings 

warnings.filterwarnings("ignore", category=DeprecationWarning)

from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document

# 1. Carrega as variáveis de ambiente
load_dotenv()

# 2. Configura a página da nossa interface
st.set_page_config(page_title="Assistente Operacional", page_icon="🤖")

# # Títulos centralizados e com a cor branca
st.markdown("<h1 style='text-align: center; color: white;'>🤖 Assistente Operacional</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: white;'>Tire suas dúvidas sobre acionamentos operacionais em tempo real.</p>", unsafe_allow_html=True)

# --- CSS CUSTOMIZADO ---
estilo_painel_chat = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* TRUQUE: Pinta de Verde Escuro o container inteiro que tiver a nossa âncora dentro */
    div[data-testid="stVerticalBlock"]:has(#caixa-verde-chat) {
        background-color: #023d38 !important; 
        padding: 30px !important;
        border-radius: 16px !important;
        box-shadow: 0px 8px 30px rgba(0, 0, 0, 0.5) !important;
        margin-top: 20px !important;
        margin-bottom: 30px !important;
    }
    
    /* Balão do Usuário (Lilás bem suave) */
    div[data-testid="stChatMessage"]:nth-child(odd) {
        background-color: #e2d9f3 !important;
        border-radius: 12px !important;
        padding: 15px !important;
        border: none !important;
    }
    
    /* Balão do Assistente (Branco/Creme) */
    div[data-testid="stChatMessage"]:nth-child(even) {
        background-color: #fbfbf6 !important;
        border-radius: 12px !important;
        padding: 15px !important;
        border: none !important;
    }

    /* CORREÇÃO: FORÇA O TEXTO E ÍCONES DENTRO DOS BALÕES A SEREM ESCUROS */
    div[data-testid="stChatMessage"] * {
        color: #1e1e1e !important;
    }

    /* Caixa de digitação fixada no rodapé */
    div[data-testid="stChatInput"] {
        border: 2px solid #023d38 !important;
        background-color: #111111 !important; 
        border-radius: 16px !important; /* Arredonda os cantos */
        overflow: hidden !important; /* Corta as rebarbas quadradas dos cantos */
    }
    </style>
"""
st.markdown(estilo_painel_chat, unsafe_allow_html=True)

# 3. Função para ler o arquivo de texto e criar a base de conhecimento
@st.cache_resource
def preparar_base_de_dados():
    caminho_arquivo = "manual.txt"
    if not os.path.exists(caminho_arquivo):
        raise FileNotFoundError(f"O arquivo '{caminho_arquivo}' não foi encontrado.")
        
    with open(caminho_arquivo, "r", encoding="utf-8") as f:
        texto_manual = f.read()
    
    docs = [Document(page_content=texto_manual, metadata={"source": caminho_arquivo})]
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(docs)
    
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    vectorstore = FAISS.from_documents(documents=splits, embedding=embeddings)
    return vectorstore.as_retriever(search_kwargs={"k": 4})

# 4. Carregar a base de dados
try:
    retriever = preparar_base_de_dados()
except Exception as e:
    st.error(f"⚠️ Erro ao carregar as informações: {e}")
    st.stop()

# 5. Configurar a IA do Google (LLM)
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.2)
system_prompt = (
    "Você é um assistente operacional rigoroso e preciso do setor de acionamento.\n"
    "Use APENAS os trechos das regras fornecidas abaixo.\n\n"
    "DIRETRIZES DE RESPOSTA:\n"
    "1. RIGOR NO MANUAL: Se uma regra não estiver explicitamente autorizada, trate como NÃO CONTEMPLADO.\n"
    "2. PROIBIÇÃO DE INVENÇÃO: Nunca deduza. Se omisso, oriente consultar a supervisão.\n"
    "3. EXCEÇÕES: Siga estritamente restrições do manual.\n"
    "4. TOM: Profissional, direto e focado na segurança operacional.\n\n"
    "Trechos do manual:\n{context}"
)
prompt = ChatPromptTemplate.from_messages([("system", system_prompt), ("human", "{input}")])

def formatar_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

rag_chain = {"context": retriever | formatar_docs, "input": RunnablePassthrough()} | prompt | llm | StrOutputParser()

# 7. Interface de Chat

if "messages" not in st.session_state:
    st.session_state.messages = []

# CRIA A CAIXA VERDE DO CHAT E COLOCA A ÂNCORA INVISÍVEL
caixa_chat = st.container()
caixa_chat.markdown("<div id='caixa-verde-chat'></div>", unsafe_allow_html=True)

# Exibe o histórico DENTRO da caixa verde
with caixa_chat:
    for message in st.session_state.messages:
        avatar_do_historico = "👤" if message["role"] == "user" else "🤖"
        with st.chat_message(message["role"], avatar=avatar_do_historico):
            st.markdown(message["content"])

# O campo de digitação fica fixado no rodapé (padrão do Streamlit)
if pergunta := st.chat_input("Qual é a sua dúvida operacional ou regra de associação?"):
    
    st.session_state.messages.append({"role": "user", "content": pergunta})
    
    # Exibe a pergunta NOVA dentro da caixa verde
    with caixa_chat:
        with st.chat_message("user", avatar="👤"):
            st.markdown(pergunta)

    # Exibe e processa a resposta NOVA dentro da caixa verde
    with caixa_chat:
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Pesquisando no manual de atendimento..."):
                try:
                    resposta = rag_chain.invoke(pergunta)
                    st.markdown(resposta)
                    st.session_state.messages.append({"role": "assistant", "content": resposta})
                except Exception as e:
                    st.error(f"Erro ao processar a resposta da IA: {e}")
