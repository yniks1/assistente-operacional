import streamlit as st
import os

# Configuração da página
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

# ---------------------------------------------------------
# 1. BASE DE CONHECIMENTO LAPIDADA
# ---------------------------------------------------------
BASE_CONHECIMENTO = [
    # REGRAS GERAIS E PRINCÍPIOS
    {
        "topico": "Urgência e Emergência",
        "palavras_chave": ["urgência", "emergência", "princípios básicos", "quem pode acionar", "veículo ativo"],
        "resposta": "Atendimento de serviços de Urgência e Emergência ocorre quando o veículo está impedido de se locomover por meios próprios e representa risco iminente.[cite: 1] Os serviços são aplicáveis a veículos ATIVOS.[cite: 1] A cobertura é para o veículo e seus ocupantes; qualquer pessoa que esteja conduzindo pode solicitar.[cite: 1]"
    },
    {
        "topico": "Planos, Fracionamento e Excedente",
        "palavras_chave": ["fracionamento", "excedente", "saldo de km", "sobra de km", "limite de quilometragem"],
        "resposta": "Ao ultrapassar o limite, o custo do deslocamento excedente será por conta do condutor, pago no ato diretamente ao prestador.[cite: 1] O fracionamento não pode ultrapassar a quilometragem total do plano.[cite: 1] O atendimento é encerrado na chegada ao destino, não restando direito a eventual saldo/sobra de quilometragem.[cite: 1]"
    },
    {
        "topico": "Fato Gerador",
        "palavras_chave": ["fato gerador", "quais são os fatos", "eventos cobertos"],
        "resposta": "São eles: Acidente/Colisão/Incêndio, Falta de Combustível, Furto de Pneu(s) ou Roda(s), Furto ou Roubo Recuperado, Incidente com Chaves, Pane Elétrica/Mecânica e Pneu(s) Avariado(s).[cite: 1]"
    },
    {
        "topico": "Serviços Não Conclusivos",
        "palavras_chave": ["assistência pneumática geral", "auxílio combustível geral", "chaveiro geral", "carga de bateria geral"],
        "resposta": "Assistência Pneumática, Auxílio Combustível, Chaveiro e Socorro Elétrico/Mecânico poderão solicitar a remoção do veículo (para borracharia, posto e chaveiro mais próximo) caso não sejam conclusivos.[cite: 1]"
    },
    {
        "topico": "Carro de Apoio (Regra Geral)",
        "palavras_chave": ["carro de apoio geral", "apoio geral"],
        "resposta": "Sempre que for questionado a respeito do carro de apoio, exiba: Para solicitação de carro de apoio é necessário fotos e videos para incluir no histórico do atendimento.[cite: 1]"
    },
    {
        "topico": "Veículos Inativos",
        "palavras_chave": ["inativo", "fora da base", "sem cobertura", "cancelado"],
        "resposta": "Não será realizado atendimento para o veículo INATIVO ou FORA DA BASE.[cite: 1] A central informará SEM COBERTURA, COBERTURA INATIVA ou SIMILAR.[cite: 1]"
    },
    {
        "topico": "Atendimento Comercial vs Fora do Comercial",
        "palavras_chave": ["horário comercial", "fora do horário", "continuação", "dia subsequente"],
        "resposta": "Dentro do horário comercial: O atendimento é conclusivo e sem direito a continuação.[cite: 1] Fora do horário comercial: Se o veículo for para a base do prestador ou domicílio, será facultada a continuação no primeiro dia subsequente.[cite: 1] Se enviado para endereço desconhecido, é conclusivo sem continuação.[cite: 1]"
    },
    {
        "topico": "Serviços Acessórios (Hotel, MTA, Guarda)",
        "palavras_chave": ["serviços acessórios", "complemento", "diária de hotel geral", "mta geral", "guarda geral"],
        "resposta": "Em caso de impossibilidade da prestação de serviço fora do horário comercial, utiliza-se Diária de Hotel, MTA ou Guarda de veículo.[cite: 1] Importante: O uso do reboque é pré-requisito.[cite: 1]"
    },

    # ATENDIMENTOS SEM COBERTURA (RESTRIÇÕES GERAIS)
    {
        "topico": "Veículo Atolado ou Sem Acesso",
        "palavras_chave": ["atolado", "sem acesso", "barro", "lama", "via não pavimentada"],
        "resposta": "Veículo atolado ou sem acesso: Negligência ou via não reconhecida exigem que o cliente providencie meios próprios para levar à via pavimentada, sem reembolso.[cite: 1]"
    },
    {
        "topico": "Desacordo com CNT / Apreendidos",
        "palavras_chave": ["cnt", "apreendido", "retido", "polícia", "blitz", "leis de trânsito"],
        "resposta": "Desacordo com CNT: Veículos retidos/apreendidos por descumprir leis de trânsito não têm cobertura.[cite: 1]"
    },
    {
        "topico": "Destombamento e Resgate Geral",
        "palavras_chave": ["destombamento geral", "resgate geral", "caiu", "ribanceira"],
        "resposta": "Destombamento/Resgate: Não estão incluídos nos planos gerais (responsabilidade de agravo, alto custo). Verificar sempre cobertura em caráter de exceção.[cite: 1]"
    },
    {
        "topico": "Veículos Carregados",
        "palavras_chave": ["carregado", "mercadoria", "carga", "peso"],
        "resposta": "Veículos carregados: Não é realizada a remoção de veículos carregados com mercadorias e objetos (salvo objetos de uso pessoal).[cite: 1]"
    },
    {
        "topico": "Busca e Apreensão / Roubo",
        "palavras_chave": ["busca e apreensão", "roubo", "furto", "recuperado"],
        "resposta": "Veículos com busca e apreensão: Não é realizada a remoção de veículos com queixa de furto ou roubo.[cite: 1]"
    },
    {
        "topico": "Oficina para Oficina",
        "palavras_chave": ["oficina para oficina", "transferir de oficina", "levar para outra oficina"],
        "resposta": "Atendimento de oficina para oficina: Em não se caracterizando condição emergencial, o plano geral não contempla prestação de serviço para veículos que já se encontrem em uma oficina.[cite: 1]"
    },
    {
        "topico": "Atividade Remunerada / Aplicativo",
        "palavras_chave": ["atividade remunerada", "uber", "aplicativo", "passageiros"],
        "resposta": "Veículos de atividade remunerada: MTA, Táxi e Hotel são facultados somente ao condutor. A responsabilidade civil dos passageiros é do cliente.[cite: 1]"
    },

    # ATENDIMENTOS ESPECÍFICOS E MÁSCARAS
    {
        "topico": "Cavalo Mecânico",
        "palavras_chave": ["cavalo mecânico", "engatado", "desatrelado"],
        "resposta": "Cavalo mecânico: O cliente deve desengatar/desatrelar e estacionar o semi-reboque com pés de apoio.[cite: 1] O prestador liberará os freios e providenciará a remoção do cavalo mecânico.[cite: 1]"
    },
    {
        "topico": "Atendimentos Frustrados / Reembolso",
        "palavras_chave": ["frustrado", "reembolso email"],
        "resposta": "Atendimentos frustrados: Se autorizado pela central, o cliente realiza por meios próprios e solicita reembolso via e-mail (reembolso@grupoassistme.com.br) enviando dados e Nota Fiscal.[cite: 1]"
    },
    {
        "topico": "Transporte de Animais",
        "palavras_chave": ["animais", "cachorro", "gato", "pet"],
        "resposta": "Atendimentos com Animais: Prestadores não são obrigados a transportar animais em MTA, Táxi ou Hotel.[cite: 1] Se não for possível seguir o atendimento, o cliente deverá seguir por meios próprios sem reembolso.[cite: 1]"
    },
    {
        "topico": "Máscaras e Comunicação",
        "palavras_chave": ["máscara sms", "falta de contato", "nova previsão", "busca de prestadores"],
        "resposta": "Sempre preencher as máscaras para: Falta de contato com o cliente, Busca de prestadores, Nova previsão de prévia, Atraso ou Cancelamento.[cite: 1]"
    },
    {
        "topico": "Valores Praticados no Mercado",
        "palavras_chave": ["valores de mercado", "preço do reboque", "veículo leve", "veículo pesado", "utilitário"],
        "resposta": "Valores de mercado: Veículos leves e motos (Saída R$170, km excedente R$3,50).[cite: 1] Utilitários/carga (Saída R$200, km excedente R$4,00).[cite: 1] Veículos Pesados (Saída R$700, km excedente R$7,00).[cite: 1]"
    },
    {
        "topico": "Nomenclatura dos Planos Especiais",
        "palavras_chave": ["bônus 1", "bônus 3", "bônus 6", "dobro", "ilimitado", "light", "livre", "vip"],
        "resposta": "Bônus 1/3/6 referem-se a remoções adicionais. Ilimitado: KM ilimitado nos fatos geradores. VIP: altas quilometragens para colisões. Light: Não possui MTA ou Hospedagem.[cite: 1]"
    },
    {
        "topico": "Veículo na Base (Madrugada)",
        "palavras_chave": ["veículo na base", "madrugada", "noturno"],
        "resposta": "Veículo para base (período noturno): Priorizando a segurança, o veículo fica na base e o cliente deve ligar no próximo dia útil (0800) para solicitar remoção final, senão pagará diárias de pátio.[cite: 1]"
    },
    {
        "topico": "Formalização de Serviços",
        "palavras_chave": ["formalização", "agendamento"],
        "resposta": "Formalização: É obrigatório abordar o serviço, endereço de origem e destino, e aguardar a confirmação do solicitante ('O Sr. confirma a Solicitação?').[cite: 1]"
    },
    {
        "topico": "Placa Mercosul",
        "palavras_chave": ["placa mercosul", "letras da placa"],
        "resposta": "Substituição: 0=A, 1=B, 2=C, 3=D, 4=E, 5=F, 6=G, 7=H, 8=I, 9=J.[cite: 1]"
    },
    {
        "topico": "Processo de Reembolso (Máscara)",
        "palavras_chave": ["máscara de reembolso", "processo de reembolso"],
        "resposta": "Reembolso: Deve-se registrar no histórico o Serviço, Valor, Passageiros, Motivo e vincular o prestador REEMBOLSO CLIENTE.[cite: 1]"
    },

    # REGRAS POR ASSOCIAÇÃO (LAPIDADAS E ATÔMICAS)
    {
        "topico": "AAVB - Remoção / Residência",
        "palavras_chave": ["reboque aavb", "remoção aavb", "residência aavb"],
        "resposta": "AAVB: Cliente poderá levar para outro endereço de residência não cadastrada e no dia seguinte será facultado o direito de continuação.[cite: 1]"
    },
    {
        "topico": "AAVB - Destombamento e Resgate",
        "palavras_chave": ["destombamento aavb", "resgate aavb"],
        "resposta": "AAVB: Necessário solicitar vídeos e fotos. A associação libera uma alçada no valor de R$200,00. O que ultrapassar é responsabilidade do cliente.[cite: 1]"
    },
    {
        "topico": "AAVB - Estrada de Terra",
        "palavras_chave": ["terra aavb", "estrada aavb"],
        "resposta": "AAVB: Cliente tem direito à remoção em estrada de terra. Deve-se notificar o supervisor para autorização. Na falta de retorno, seguir com a cobertura.[cite: 1]"
    },
    {
        "topico": "AAVM - Acidente, Colisão e Incêndio",
        "palavras_chave": ["acidente aavm", "colisão aavm", "incêndio aavm"],
        "resposta": "AAVM: Deve obrigatoriamente encaminhar para a BASE DO PRESTADOR (custo pago pela associação). Orientar o cliente a entrar em contato com o ADM para Sinistro.[cite: 1]"
    },
    {
        "topico": "AAVM - Pane Elétrica / Mecânica",
        "palavras_chave": ["pane aavm", "reboque aavm", "mecânica aavm"],
        "resposta": "AAVM (Pane): Horário comercial envia para oficina até 200km totais. Fora do comercial: base ou domicílio (alçada 200km totais). NÃO mencionar limite de 100km na ligação.[cite: 1]"
    },
    {
        "topico": "AAVM - Estrada de Terra e Resgate",
        "palavras_chave": ["terra aavm", "estrada aavm", "resgate aavm", "destombamento aavm"],
        "resposta": "AAVM: Tem direito à remoção em estrada de terra com notificação ao supervisor. Resgate: Necessário fotos/vídeos no WhatsApp para liberação.[cite: 1]"
    },
    {
        "topico": "AAVM - Táxi Urbano",
        "palavras_chave": ["táxi aavm", "taxi aavm"],
        "resposta": "AAVM: Táxi Urbano no valor de até R$100,00 limitados a 50km totais (o plano Light não possui cobertura MTA).[cite: 1]"
    },
    {
        "topico": "AAVM - MTA / Passagens Rodoviárias",
        "palavras_chave": ["mta aavm", "passagem aavm", "retorno aavm"],
        "resposta": "AAVM: MTA liberado somente para Acidente, Colisão, Incêndio, Furto ou Roubo. Valor máximo de R$350,00 (Plano Light sem cobertura).[cite: 1]"
    },
    {
        "topico": "AAVM - Hotel e Chaveiro",
        "palavras_chave": ["hotel aavm", "chaveiro aavm", "porta aavm"],
        "resposta": "AAVM: Hotel liberado para Acidente/Colisão/Incêndio/Roubo (R$500 máx).[cite: 1] Chaveiro: Cobertura padrão de R$160,00 (se ultrapassar, solicitar autorização).[cite: 1]"
    },
    {
        "topico": "ACTR - Reboque",
        "palavras_chave": ["reboque actr", "remoção actr", "oficina actr"],
        "resposta": "ACTR: Encaminhar para oficina ou destino dentro de 200km totais. Se ultrapassar, coletar dados sem objeção e colocar em análise para liberação.[cite: 1]"
    },
    {
        "topico": "ALFA BAHIA - Reboque e Estrada de Terra",
        "palavras_chave": ["reboque alfa", "remoção alfa", "terra alfa", "estrada alfa"],
        "resposta": "ALFA BAHIA: Prerrogativa de oficina mais próxima em raio de 200km totais.[cite: 1] Cliente tem direito à remoção em estrada de terra (se valor for acima do mercado, pedir autorização no WhatsApp).[cite: 1]"
    },
    {
        "topico": "ALICERCE - Reboque e Estrada de Terra",
        "palavras_chave": ["reboque alicerce", "remoção alicerce", "terra alicerce", "estrada alicerce"],
        "resposta": "ALICERCE: Oficina ou destino com limite de 300km totais. Se ultrapassar, questionar opções mais próximas e enviar para análise.[cite: 1] Estrada de terra coberta mediante autorização via WhatsApp.[cite: 1]"
    },
    {
        "topico": "ALICERCE - Pneus Avariados",
        "palavras_chave": ["pneu alicerce", "pneumática alicerce", "borracharia alicerce"],
        "resposta": "ALICERCE: Cliente não possui cobertura de reboque ou troca de pneus para Pneus Avariados. Orientar contato no ADM: (31) 2559-8004.[cite: 1]"
    },
    {
        "topico": "ALICERCE - Resgate, MTA e Táxi",
        "palavras_chave": ["resgate alicerce", "destombamento alicerce", "mta alicerce", "táxi alicerce", "taxi alicerce"],
        "resposta": "ALICERCE: Resgate até R$2.000,00 por evento.[cite: 1] MTA e Táxi limitados a R$200,00 por evento independente da quilometragem.[cite: 1]"
    },
    {
        "topico": "ABAPAV - Chaveiro",
        "palavras_chave": ["chaveiro abapav", "chave abapav"],
        "resposta": "ABAPAV: Além de abertura, fornece remoção de chaves quebradas. Na confecção de chaves, a Associação cobre deslocamento+mão de obra (cliente paga o material).[cite: 1]"
    },
    {
        "topico": "AGIBENS - Reboque e Táxi",
        "palavras_chave": ["reboque agibens", "táxi agibens", "taxi agibens"],
        "resposta": "AGIBENS: Reboque dentro de 200km totais (se passar, entra em análise).[cite: 1] Táxi Urbano de até R$50,00 (o que passar é excedente).[cite: 1]"
    },
    {
        "topico": "AGN - Reboque e Exceções Gerais",
        "palavras_chave": ["reboque agn", "apoio agn", "patins agn"],
        "resposta": "AGN: Reboque raio de 200km totais (aguardar 15 min grupo). NÃO contempla patins (repassar valor ao cliente).[cite: 1] NÃO contempla carro de apoio.[cite: 1]"
    },
    {
        "topico": "AGN - Fora do Horário Comercial (Pane)",
        "palavras_chave": ["pane agn", "combustível agn", "pneu agn", "noite agn"],
        "resposta": "AGN: Fora do comercial (Pane/Combustível/Chave/Pneu), o veículo vai para a residência no raio de 40km totais e o atendimento é CONCLUSIVO (sem continuação).[cite: 1]"
    },
    {
        "topico": "AGN - Táxi, MTA, Resgate e Hotel",
        "palavras_chave": ["táxi agn", "taxi agn", "mta agn", "resgate agn", "hotel agn"],
        "resposta": "AGN: Táxi até 50km totais.[cite: 1] MTA Passagens (só para Acidente/Colisão/Incêndio/Roubo) até R$350,00.[cite: 1] Resgate alçada de R$200,00.[cite: 1] Hotel (só para Acidente/Colisão/Incêndio/Roubo) máx R$500,00.[cite: 1]"
    },
    {
        "topico": "ABS BOM SUCESSO - Reboque e Pneus",
        "palavras_chave": ["reboque abs", "reboque bom", "pneu abs", "pneu bom"],
        "resposta": "ABS BOM SUCESSO: Reboque acima de 300km totais pede autorização no grupo.[cite: 1] Pneus avariados vão obrigatoriamente para borracharia/oficina mais próxima (cliente não escolhe endereço, se fechado fica conclusivo).[cite: 1]"
    },
    {
        "topico": "AMI - Reboque, Táxi, MTA, Resgate e Hotel",
        "palavras_chave": ["reboque ami", "apoio ami", "táxi ami", "taxi ami", "mta ami", "resgate ami", "hotel ami"],
        "resposta": "AMI: Segue regras idênticas à AGN (Reboque 200km, Táxi 50km/R$50, MTA R$350, Resgate R$200, Hotel R$500 para acidentes graves).[cite: 1] NÃO contempla patins e carro de apoio.[cite: 1] Pane fora do comercial vai para casa raio de 40km conclusivo.[cite: 1]"
    },
    {
        "topico": "AVEP - Reboque, Via de Terra e Táxi",
        "palavras_chave": ["reboque avep", "terra avep", "estrada avep", "táxi avep", "taxi avep"],
        "resposta": "AVEP: Reboque para oficina em 200km totais. Residência não cadastrada tem direito a continuação no dia útil.[cite: 1] Estrada de terra coberta.[cite: 1] Táxi até R$300,00 (75km ida/volta).[cite: 1] NÃO contempla carro de apoio.[cite: 1]"
    },
    {
        "topico": "AVEP - Destombamento, Base, MTA e Hotel",
        "palavras_chave": ["destombamento avep", "resgate avep", "base avep", "mta avep", "hotel avep"],
        "resposta": "AVEP: Resgate de R$2.500,00.[cite: 1] Veículo p/ Base: Acidente/Colisão/Incêndio a AVEP paga; Pane Elétrica/Mecânica o cliente paga a diária.[cite: 1] MTA Passagens: R$400,00.[cite: 1] Hotel: até 3 diárias de R$150,00.[cite: 1]"
    },
    {
        "topico": "AUTOCLASS, BV TRUCK, CLIKAR",
        "palavras_chave": ["reboque autoclass", "reboque bv", "reboque clikar"],
        "resposta": "Estas associações (AUTOCLASS, BV TRUCK, CLIKAR): Encaminhar para oficina ou destino dentro de 200km totais. Se ultrapassar, colocar em análise no grupo.[cite: 1]"
    },
    {
        "topico": "BR TRUCK - MTA e Resgate",
        "palavras_chave": ["mta br", "passagem br", "resgate br", "destombamento br"],
        "resposta": "BR TRUCK: MTA reembolsa passagens somente para Acidente/Colisão/Incêndio/Roubo.[cite: 1] Resgate exige envio de fotos de TODOS os ângulos no grupo.[cite: 1]"
    },
    {
        "topico": "CLICK CAR - Reboque, Táxi e Hotel",
        "palavras_chave": ["reboque click", "táxi click", "taxi click", "hotel click"],
        "resposta": "CLICK CAR: Reboque 200km totais.[cite: 1] Táxi máx R$100,00 até 100km (via reembolso).[cite: 1] Hotel limite de 1 diária de R$200,00.[cite: 1]"
    },
    {
        "topico": "CLUB CAR - Reboque, Residência, Terra e Acidente",
        "palavras_chave": ["reboque club", "residência club", "terra club", "acidente club", "colisão club"],
        "resposta": "CLUB CAR: Reboque 200km totais (aguardar 15 min grupo).[cite: 1] Residência não cadastrada: tem continuação durante o mês.[cite: 1] Terra coberta.[cite: 1] Acidente/Colisão/Incêndio: orientar direcionar para a residência e contatar o ADM no próximo dia útil.[cite: 1]"
    },
    {
        "topico": "CONFIANCE e COOPERTRAX",
        "palavras_chave": ["reboque confiance", "reboque coopertrax"],
        "resposta": "CONFIANCE / COOPERTRAX: Atendimentos que ultrapassem o raio de 200km totais devem ser colocados em análise no grupo.[cite: 1]"
    },
    {
        "topico": "COOPERVALES - Reboque, Táxi e Estrada",
        "palavras_chave": ["reboque coopervales", "táxi coopervales", "taxi coopervales", "terra coopervales"],
        "resposta": "COOPERVALES: Reboque 200km totais.[cite: 1] Táxi máx R$300,00 até 100km dist.[cite: 1] Estrada de terra coberta (se muito alto, prévia autorização).[cite: 1]"
    },
    {
        "topico": "DIGICAR - Reboque, Plantão e Roubo",
        "palavras_chave": ["reboque digicar", "plantonista digicar", "furto digicar", "roubo digicar"],
        "resposta": "DIGICAR: Reboque 200km totais.[cite: 1] Plantonistas: Euler (31 9275-4187) e Romulo (31 9168-4363).[cite: 1] NÃO POSSUI vistoria in loco.[cite: 1]"
    },
    {
        "topico": "ESTILO - Táxi, Chaveiro e Estrada de Terra",
        "palavras_chave": ["táxi estilo", "taxi estilo", "mta estilo", "chaveiro estilo", "terra estilo"],
        "resposta": "ESTILO: Táxi/MTA R$100,00 para Panes em Geral.[cite: 1] Chaveiro cobre remoção de chave quebrada da ignição/maçaneta.[cite: 1] Estrada de terra tem cobertura notificando o grupo.[cite: 1]"
    },
    {
        "topico": "EXCLUSIVA e GRAZIOTHI",
        "palavras_chave": ["reboque exclusiva", "reboque graziothi"],
        "resposta": "EXCLUSIVA / GRAZIOTHI: Oficina ou destino dentro de 200km totais.[cite: 1]"
    },
    {
        "topico": "FORTE CAR - Panes e Acidentes",
        "palavras_chave": ["reboque forte", "pane forte", "acidente forte", "colisão forte"],
        "resposta": "FORTE CAR: Reboque 200km totais.[cite: 1] Acidente/Colisão/Incêndio: Enviar para oficina em 200km totais, se não aceitar, solicitar liberação. Sem retorno, enviar para Base ou Residência (menor trajeto).[cite: 1]"
    },
    {
        "topico": "GASP / GESTORA / FÁCIL AUTO",
        "palavras_chave": ["reboque gasp", "hora gasp", "trabalhada gasp"],
        "resposta": "GASP: Toda remoção acima de 200km totais deve notificar supervisor.[cite: 1] NÃO contempla hora trabalhada ou parada (repassar ao cliente).[cite: 1]"
    },
    {
        "topico": "GO LOCK - Panes, Acidente, Táxi e MTA",
        "palavras_chave": ["reboque go", "pane go", "acidente go", "táxi go", "taxi go", "mta go"],
        "resposta": "GO LOCK: Panes 200km totais. Acidente: local seguro do plano (se base, diária é do condutor).[cite: 1] NÃO tem Carro de Apoio.[cite: 1] Táxi R$150,00.[cite: 1] Passagens R$300,00.[cite: 1] Hospedagem R$100,00 por pessoa.[cite: 1]"
    },
    {
        "topico": "IDEAL - Panes e Acidentes",
        "palavras_chave": ["pane ideal", "acidente ideal", "reboque ideal"],
        "resposta": "IDEAL: Panes para oficina 200km totais (se não aceitar, pedir para ele fazer e buscar reembolso na Ideal).[cite: 1] Acidente acima de 400km totais pede autorização no grupo.[cite: 1]"
    },
    {
        "topico": "INOVAR - Reboque, Base e Combustível",
        "palavras_chave": ["reboque inovar", "base inovar", "combustível inovar"],
        "resposta": "INOVAR: Reboque >200km totais vai pra análise. Sem contato, enviar para Residência ou Base (associação paga a diária da base).[cite: 1] Falta combustível: cliente paga gasolina 5L e o galão (aprox R$20).[cite: 1]"
    },
    {
        "topico": "INOVAR - Estrada, Carga, Resgate e MTA",
        "palavras_chave": ["terra inovar", "carga inovar", "resgate inovar", "mta inovar", "táxi inovar", "taxi inovar"],
        "resposta": "INOVAR: Veículo carregado alçada de R$200,00.[cite: 1] Resgate exige fotos/vídeos para liberação.[cite: 1] Táxi alçada de R$600,00. MTA: Por indisponibilidade de ônibus (espera >2h), libera R$600,00 para táxi/uber (NÃO informar excedente ao cliente).[cite: 1]"
    },
    {
        "topico": "INNOVE - Reboque, Resgate e Estrada",
        "palavras_chave": ["reboque innove", "resgate innove", "terra innove"],
        "resposta": "INNOVE: Reboque 200km totais (esperar 15 min no grupo).[cite: 1] Resgate alçada R$250,00.[cite: 1] Via de terra coberta mediante autorização.[cite: 1]"
    },
    {
        "topico": "LIBRE e PROAPP",
        "palavras_chave": ["reboque libre", "terra libre", "reboque proapp"],
        "resposta": "LIBRE / PROAPP: Reboque 200km totais. Libre cobre estrada de terra notificando o supervisor.[cite: 1]"
    },
    {
        "topico": "LIDERY - Reboque e Hotel",
        "palavras_chave": ["reboque lidery", "hotel lidery"],
        "resposta": "LIDERY: Pane 200km totais.[cite: 1] Hotel: 3 diárias limitadas a R$120,00 por dia (independente de ocupantes).[cite: 1]"
    },
    {
        "topico": "LIFECLUB - Táxi",
        "palavras_chave": ["táxi life", "taxi life", "lifeclub"],
        "resposta": "LIFECLUB: NÃO contempla serviço de Táxi Urbano.[cite: 1]"
    },
    {
        "topico": "MOTOR HOME - Reboque, Táxi, Destombamento",
        "palavras_chave": ["reboque motor", "táxi motor", "taxi motor", "destombamento motor", "resgate motor"],
        "resposta": "MOTOR HOME: Reboque 200km totais.[cite: 1] Táxi R$70,00 (40km totais).[cite: 1] Destombamento SÓ em via pública via reembolso (R$2500 veículo, máx R$5000 conjunto).[cite: 1] NÃO cobre resgate.[cite: 1] Permite uso de patins.[cite: 1]"
    },
    {
        "topico": "MG CAR - MTA",
        "palavras_chave": ["mta mg", "táxi mg", "taxi mg", "hotel mg"],
        "resposta": "MG CAR: MTA (Táxi/Passagens/Hotel) - Cobertura padrão, cliente tem direito.[cite: 1]"
    },
    {
        "topico": "MYPASS - Panes e Acidente",
        "palavras_chave": ["reboque mypass", "pane mypass", "acidente mypass", "análise mypass"],
        "resposta": "MYPASS: Pane 200km totais.[cite: 1] Acidente/Colisão/Incêndio segue cobertura padrão. NÃO enviar serviços em análise no grupo de relacionamento.[cite: 1]"
    },
    {
        "topico": "NACIONAL CAR - Resgate",
        "palavras_chave": ["resgate nacional", "destombamento nacional"],
        "resposta": "NACIONAL CAR: Destombamento e Resgate só sob consulta. Abrir atendimento, realizar cotações com fotos/vídeos e enviar no grupo pedindo aprovação.[cite: 1]"
    },
    {
        "topico": "NEXOOS - Reboque, Táxi e Hotel",
        "palavras_chave": ["reboque nexoos", "terra nexoos", "táxi nexoos", "taxi nexoos", "hotel nexoos"],
        "resposta": "NEXOOS: Reboque 200km totais (esperar 15 min grupo). Estrada de terra autorizada no grupo.[cite: 1] Táxi R$150,00 (200km totais).[cite: 1] Hotel 1 diária de R$100,00 por pessoa.[cite: 1]"
    },
    {
        "topico": "NÚCLEO PROTEÇÃO - Reboque, Táxi e MTA",
        "palavras_chave": ["reboque núcleo", "táxi núcleo", "taxi núcleo", "mta núcleo", "hotel núcleo"],
        "resposta": "NÚCLEO PROTEÇÃO: Reboque 200km totais.[cite: 1] Táxi R$200,00 (100km).[cite: 1] MTA passagens a partir de 100km. Hotel 1 diária R$100,00/pessoa.[cite: 1]"
    },
    {
        "topico": "PORTO SUL - Reboque e Estrada",
        "palavras_chave": ["reboque porto", "terra porto", "porto sul"],
        "resposta": "PORTO SUL: Comercial oficina 200km totais. Fora do comercial: base ou domicílio 200km totais. Cobre estrada de terra (notificar supervisor).[cite: 1]"
    },
    {
        "topico": "PRIX e PROLINE - Panes e Acidentes",
        "palavras_chave": ["reboque prix", "pane prix", "reboque proline", "pane proline", "terra proline"],
        "resposta": "PRIX / PROLINE: Panes oficina 200km totais. Acidente oficina 200km totais, se não tiver retorno, Base ou Residência.[cite: 1] Proline cobre estrada de terra notificando grupo.[cite: 1]"
    },
    {
        "topico": "PROTEGE MAIS, PORTO BRASIL, POSITIVE CAR",
        "palavras_chave": ["reboque protege", "reboque porto brasil", "reboque positive"],
        "resposta": "Estas associações (PROTEGE MAIS, PORTO BRASIL, POSITIVE CAR): Reboque 200km totais ou colocar em análise no grupo.[cite: 1]"
    },
    {
        "topico": "REAL TRUCK - Remoções e Estrada",
        "palavras_chave": ["oficina real truck", "reboque real", "residência real truck", "terra real truck"],
        "resposta": "REAL TRUCK: Permite remoção Oficina p/ Oficina se não usou reboque por Pane no mês.[cite: 1] Residência não cadastrada: direito de continuação dia útil.[cite: 1] Cobre estrada de terra.[cite: 1]"
    },
    {
        "topico": "REAL TRUCK - Resgate, Táxi e Hotel",
        "palavras_chave": ["resgate real", "destombamento real", "hotel real", "acidente real", "táxi real", "taxi real"],
        "resposta": "REAL TRUCK: Destombamento/Resgate: R$500,00.[cite: 1] Hotel: 1 diária de R$150,00/pessoa (máx R$300).[cite: 1] Acidente >1000km totais pede autorização. Táxi R$150,00 (200km totais).[cite: 1]"
    },
    {
        "topico": "SPLIT RISK e FILIAIS - Panes, Acidente e Apoio",
        "palavras_chave": ["reboque split", "pane split", "acidente split", "apoio split", "globus", "stop club", "lince", "turquim", "meo"],
        "resposta": "SPLIT RISK (E filiais MY PASS, GLOBUS, STOP CLUB, LINCE, TURQUIM, MEO): Comercial oficina 200km totais.[cite: 1] Fora comercial/Acidente: local seguro indicado (se for base do prestador, as diárias são do cliente).[cite: 1] NÃO tem carro de apoio.[cite: 1] Estrada terra: notificar grupo.[cite: 1]"
    },
    {
        "topico": "SPLIT RISK e FILIAIS - Táxi, MTA e Hotel",
        "palavras_chave": ["táxi split", "taxi split", "mta split", "hotel split"],
        "resposta": "SPLIT RISK: Táxi R$150,00.[cite: 1] Passagens R$300,00.[cite: 1] Hospedagem R$100,00 por pessoa.[cite: 1]"
    },
    {
        "topico": "SUPREMA - Pane e Acidente",
        "palavras_chave": ["pane suprema", "acidente suprema", "base suprema"],
        "resposta": "SUPREMA: Pane 200km totais.[cite: 1] Acidente vai para Base do Prestador (Associação paga diária, e o cliente contata o ADM para retirar nas primeiras 4h úteis).[cite: 1]"
    },
    {
        "topico": "SUPERA - Táxi, MTA, Hotel e Chaveiro",
        "palavras_chave": ["táxi supera", "taxi supera", "mta supera", "hotel supera", "chaveiro supera"],
        "resposta": "SUPERA: Táxi R$50,00.[cite: 1] Retorno/Continuação (MTA) R$200,00.[cite: 1] Hotel 1 diária máx R$200,00.[cite: 1] Chaveiro alçada de R$100,00.[cite: 1]"
    },
    {
        "topico": "TÁXI FORT - Base e Táxi",
        "palavras_chave": ["reboque fort", "base fort", "táxi fort", "taxi fort"],
        "resposta": "TÁXI FORT: Fora do comercial enviar p/ residência ou base do prestador (o menor).[cite: 1] Táxi SOMENTE para Acidente/Colisão/Incêndio até R$200,00 (200km totais).[cite: 1]"
    },
    {
        "topico": "TM BRASIL - Remoções, Estrada e Resgate",
        "palavras_chave": ["residência tm", "terra tm", "mineradora tm", "oficina tm", "resgate tm", "destombamento tm"],
        "resposta": "TM BRASIL: Residência não cadastrada: continuação dia seguinte.[cite: 1] Estrada de terra/mineradora: coberta.[cite: 1] Oficina p/ Oficina permite se não usou pane no mês.[cite: 1] Resgate enviar valor no grupo.[cite: 1]"
    },
    {
        "topico": "TRIAD - Reboque e Acidentes",
        "palavras_chave": ["reboque triad", "acidente triad", "base triad", "incêndio triad"],
        "resposta": "TRIAD: Reboque 200km totais.[cite: 1] Acidente/Colisão/Incêndio obrigatoriamente para a Base (Associação paga). Cliente deve contatar ADM em 48h senão paga diária. Remoção da base SÓ com autorização da associação.[cite: 1]"
    },
    {
        "topico": "UNIBRAS MHAIS (RJ)",
        "palavras_chave": ["base unibras", "base mhais"],
        "resposta": "UNIBRAS MHAIS (RJ): NÃO contempla envio para a base. Associação não paga diárias. Orientar ir para a residência.[cite: 1]"
    },
    {
        "topico": "UNIBRÁS BENEFÍCIOS (BH) e VENTURE",
        "palavras_chave": ["reboque unibrás", "pane venture", "reboque venture"],
        "resposta": "UNIBRÁS BENEFÍCIOS (BH) / VENTURE: Reboque 200km totais para oficina mais próxima (Venture apenas Pane Elétrica/Mecânica).[cite: 1]"
    },
    {
        "topico": "YOUCAR - Reboque, Estrada, Táxi e Resgate",
        "palavras_chave": ["reboque youcar", "terra youcar", "táxi youcar", "taxi youcar", "hotel youcar", "resgate youcar"],
        "resposta": "YOUCAR: Reboque 200km totais.[cite: 1] Via não reconhecida coberta pedindo autorização.[cite: 1] Táxi R$200,00 (200km totais).[cite: 1] Hotel 2 diárias de R$150,00/pessoa.[cite: 1] Resgate alçada de R$1.500,00.[cite: 1]"
    },

    # MANUAL RESIDENCIAL
    {
        "topico": "Residencial - Chaveiro",
        "palavras_chave": ["chaveiro residencial", "chave residencial"],
        "resposta": "Residencial: Chaveiro Emergencial (quebra/perda porta principal) R$150,00 (3 por ano).[cite: 1]"
    },
    {
        "topico": "Residencial - Eletricista",
        "palavras_chave": ["eletricista", "elétrico residencial"],
        "resposta": "Residencial: Eletricista (problemas elétricos) R$120,00 (3 por ano, 1 por mês).[cite: 1]"
    },
    {
        "topico": "Residencial - Encanador",
        "palavras_chave": ["encanador", "vazamento"],
        "resposta": "Residencial: Encanador (tubulação aparente) R$120,00 (3 por ano, 1 por mês).[cite: 1]"
    },
    {
        "topico": "Residencial - Vidraceiro",
        "palavras_chave": ["vidraceiro", "vidro"],
        "resposta": "Residencial: Vidraceiro (quebra vidro externo porta/janela) R$150,00 (3 por ano, 1 por mês).[cite: 1]"
    },
    {
        "topico": "Residencial - Desentupimento",
        "palavras_chave": ["desentupimento", "entupido"],
        "resposta": "Residencial: Desentupimento R$180,00 (3 por ano, 1 por mês).[cite: 1]"
    },
    {
        "topico": "Residencial - Limpeza de Ar Condicionado",
        "palavras_chave": ["ar condicionado", "limpeza ar"],
        "resposta": "Residencial: Limpeza Ar Condicionado R$180,00 (2 por ano). Na TRIAD a utilização é a cada 6 meses.[cite: 1]"
    },
    {
        "topico": "Residencial - Linha Branca ou Marrom",
        "palavras_chave": ["linha branca", "linha marrom", "eletrodoméstico"],
        "resposta": "Residencial: Linha Branca/Marrom (problema em eletrodoméstico) R$160,00 (2 por ano, 1 por mês).[cite: 1]"
    },
    {
        "topico": "Residencial - Inspeção Lar",
        "palavras_chave": ["inspeção lar", "check-up"],
        "resposta": "Residencial: Inspeção e Check-Up R$120,00 (Consultar manual para limite).[cite: 1]"
    },

    # ERROS SISTÊMICOS
    {
        "topico": "Erros Sistêmicos: Hinova (SAME)",
        "palavras_chave": ["hinova", "same", "token", "sincronização", "erro de comunicação"],
        "resposta": "Hinova/SAME: Erro de TOKEN.[cite: 1] 1- Verifique outro item do mesmo cliente (se sim vá pro 2, se não avise grupo SAME). 2- Verifique OUTRO cliente (se sim avise SAME, se não vá pro 3). 3- Sincronize itens da base (se der certo avise SAME, se errado vá pro 4). 4- Informe no grupo indisponibilidade do SGA. 5- Atendimento SÓ pode ser aberto conforme último status (ATIVO abre normal; INATIVO abre particular).[cite: 1]"
    }
]

# ---------------------------------------------------------
# 2. FUNÇÃO DE BUSCA (ATUALIZADA E MAIS INTELIGENTE)
# ---------------------------------------------------------
def buscar_no_manual(pergunta):
    # Transforma a pergunta em letras minúsculas para facilitar a busca
    pergunta_formatada = pergunta.lower()
    
    # Lógica aprimorada: agora ele confere se TODAS as palavras chaves separadas por espaço estão na frase!
    # Isso permite que você digite "reboque aavm" ou "qual a regra de reboque na associação aavm" e ele encontre!
    for item in BASE_CONHECIMENTO:
        for regra_busca in item["palavras_chave"]:
            termos = regra_busca.split()
            if all(termo in pergunta_formatada for termo in termos):
                return item["resposta"]
    
    # Se não encontrar nenhuma palavra-chave
    return "⚠️ NÃO CONTEMPLADO. Siga a cobertura padrão da Central de Atendimento e verifique com a supervisão."


# ---------------------------------------------------------
# 3. LÓGICA DO CHAT (Interface do Streamlit)
# ---------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

caixa_chat = st.container()
caixa_chat.markdown("<div id='caixa-chat-ancora'></div>", unsafe_allow_html=True)

with caixa_chat:
    for message in st.session_state.messages:
        avatar = "👤" if message["role"] == "user" else "🤖"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

if pergunta := st.chat_input("Qual é a sua dúvida operacional ou regra de acionamento?"):
    
    st.session_state.messages.append({"role": "user", "content": pergunta})
    with caixa_chat:
        with st.chat_message("user", avatar="👤"):
            st.markdown(pergunta)
            
    with caixa_chat:
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Buscando regras operacionais..."):
                
                resposta = buscar_no_manual(pergunta)
                
                st.markdown(resposta)
                st.session_state.messages.append({"role": "assistant", "content": resposta})
