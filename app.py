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

load_dotenv()

st.set_page_config(page_title="Assistente Operacional", page_icon="🤖", layout="centered")

st.markdown("""
    <h1 style='text-align: center; color: white; font-size: 2.4rem; margin-bottom: 4px;'>
        🤖 Assistente <span style='color: #a855f7;'>Operacional</span>
    </h1>
    <p style='text-align: center; color: #9ca3af; font-size: 1rem; margin-bottom: 30px;'>
        Tire suas dúvidas sobre acionamentos operacionais em tempo real.
    </p>
""", unsafe_allow_html=True)

st.markdown("""
    <style>
    /* Fundo preto geral */
    .stApp {
        background-color: #0a0a0a !important;
    }

    #MainMenu, footer, header { visibility: hidden; }

    /* Painel central do chat */
    div[data-testid="stVerticalBlock"]:has(#caixa-chat-ancora) {
        background-color: #111827 !important;
        border: 1px solid #1f2937 !important;
        border-radius: 20px !important;
        padding: 24px !important;
        margin: 0 auto 30px auto !important;
        max-width: 760px !important;
        box-shadow: 0 8px 40px rgba(0,0,0,0.6) !important;
    }

    /* Balão do usuário — roxo escuro */
    div[data-testid="stChatMessage"]:nth-child(odd) {
        background-color: #2d1f4e !important;
        border: 1px solid #6d28d9 !important;
        border-radius: 14px !important;
        padding: 14px 18px !important;
        margin-bottom: 10px !important;
    }

    /* Balão do assistente — cinza escuro */
    div[data-testid="stChatMessage"]:nth-child(even) {
        background-color: #1c1c2e !important;
        border: 1px solid #2d2d44 !important;
        border-radius: 14px !important;
        padding: 14px 18px !important;
        margin-bottom: 10px !important;
    }

    /* Texto dentro dos balões */
    div[data-testid="stChatMessage"] * {
        color: #e5e7eb !important;
    }

    /* Caixa de input */
    div[data-testid="stChatInput"] {
        background-color: #111827 !important;
        border: 1px solid #374151 !important;
        border-radius: 16px !important;
        overflow: hidden !important;
        max-width: 760px !important;
        margin: 0 auto !important;
    }

    div[data-testid="stChatInput"] textarea {
        color: #e5e7eb !important;
        background-color: transparent !important;
    }

    div[data-testid="stChatInput"] textarea::placeholder {
        color: #6b7280 !important;
    }
    </style>
""", unsafe_allow_html=True)


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


try:
    retriever = preparar_base_de_dados()
except Exception as e:
    mensagem_erro = str(e)
    # Verifica se o erro na criação dos embeddings é sobre cota excedida
    if "429" in mensagem_erro or "RESOURCE_EXHAUSTED" in mensagem_erro:
        st.warning("O assistente se encontra em manutenção no momento, tente novamente mais tarde.")
    else:
        st.error(f"⚠️ Erro ao carregar as informações: {e}")
    st.stop()

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.2)
system_prompt = (
    "Você é um assistente operacional rigoroso e preciso do setor de acionamento.\n"
    "Use APENAS os trechos das regras fornecidas abaixo.\n\n"
    "DIRETRIZES DE RESPOSTA:\n"
    "1. RIGOR NO MANUAL: Se uma regra não estiver explicitamente autorizada, trate como NÃO CONTEMPLADO e exiba a mensagem Siga cobertura padrão da Central de Atendimento e verifique com a supervisão.\n"
    "2. PROIBIÇÃO DE INVENÇÃO: Nunca deduza. Se omisso, oriente consultar a supervisão.\n"
    "3. EXCEÇÕES: Siga estritamente restrições do manual.\n"
    "4. TOM: Profissional, amigável, direto e focado na segurança operacional.\n"
    "5. CARRO DE APOIO: Para solicitação do serviço de carro de apoio, é ncessário fotos ou vídeo do local para inclusão no histórico de atendimento.\n\n"
    "Trechos do manual:\n{context}"
)
prompt = ChatPromptTemplate.from_messages([("system", system_prompt), ("human", "{input}")])

def formatar_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

rag_chain = {"context": retriever | formatar_docs, "input": RunnablePassthrough()} | prompt | llm | StrOutputParser()

if "messages" not in st.session_state:
    st.session_state.messages = []

caixa_chat = st.container()
caixa_chat.markdown("<div id='caixa-chat-ancora'></div>", unsafe_allow_html=True)

with caixa_chat:
    for message in st.session_state.messages:
        avatar = "👤" if message["role"] == "user" else "🤖"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

if pergunta := st.chat_input("Qual é a sua dúvida operacional ou regra de associação?"):
    st.session_state.messages.append({"role": "user", "content": pergunta})
    with caixa_chat:
        with st.chat_message("user", avatar="👤"):
            st.markdown(pergunta)
    with caixa_chat:
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Pesquisando no manual de atendimento..."):
                try:
                    resposta = rag_chain.invoke(pergunta)
                    st.markdown(resposta)
                    st.session_state.messages.append({"role": "assistant", "content": resposta})
                except Exception as e:
                    mensagem_erro = str(e)
                    # Verifica se o erro na hora de gerar a resposta é sobre cota excedida
                    if "429" in mensagem_erro or "RESOURCE_EXHAUSTED" in mensagem_erro:
                        st.warning("O assistente se encontra em manutenção no momento, tente novamente mais tarde.")
                    else:
                        st.error(f"Erro ao processar a resposta da IA: {e}")
