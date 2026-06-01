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

# Título minimalista e limpo
st.markdown("<h2 style='text-align: center; color: white; margin-bottom: 50px;'>Como posso te ajudar hoje?</h2>", unsafe_allow_html=True)

# --- CSS CUSTOMIZADO PARA O VISUAL MINIMALISTA ESCURO ---
estilo_minimalista = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Fundo da página escuro */
    .stApp {
        background-color: #121212;
    }
    
    /* Balão do Usuário (Cinza Escuro) */
    div[data-testid="stChatMessage"]:nth-child(odd) {
        background-color: #212121 !important;
        color: #ffffff !important;
        border-radius: 20px !important;
        padding: 15px 20px !important;
        border: none !important;
        margin-bottom: 10px !important;
    }
    
    /* Balão do Assistente (Transparente e sem bordas) */
    div[data-testid="stChatMessage"]:nth-child(even) {
        background-color: transparent !important;
        color: #ffffff !important;
        padding: 15px 20px !important;
        border: none !important;
        margin-bottom: 10px !important;
    }

    /* Força o texto dentro dos balões a ser branco */
    div[data-testid="stChatMessage"] * {
        color: #ffffff !important;
    }

    /* Caixa de digitação arredondada estilo pílula */
    div[data-testid="stChatInput"] {
        border: 1px solid #333333 !important;
        background-color: #212121 !important; 
        border-radius: 25px !important; 
        overflow: hidden !important;
    }
    
    /* Cor do texto digitado na caixa */
    div[data-testid="stChatInput"] textarea {
        color: #ffffff !important;
    }
    </style>
"""
st.markdown(estilo_minimalista, unsafe_allow_html=True)

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

# Exibe o histórico de forma solta e fluida
for message in st.session_state.messages:
    avatar_do_historico = "👤" if message["role"] == "user" else "✨"
    with st.chat_message(message["role"], avatar=avatar_do_historico):
        st.markdown(message["content"])

# O campo de digitação fica fixado no rodapé
if pergunta := st.chat_input("Qual é a sua dúvida operacional ou regra de associação?"):
    
    # Exibe a pergunta do usuário
    st.session_state.messages.append({"role": "user", "content": pergunta})
    with st.chat_message("user", avatar="👤"):
        st.markdown(pergunta)

    # Exibe e processa a resposta da IA com um ícone de brilho ✨
    with st.chat_message("assistant", avatar="✨"):
        with st.spinner("Pesquisando..."):
            try:
                resposta = rag_chain.invoke(pergunta)
                st.markdown(resposta)
                st.session_state.messages.append({"role": "assistant", "content": resposta})
            except Exception as e:
                st.error(f"Erro ao processar a resposta da IA: {e}")
