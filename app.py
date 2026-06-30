import streamlit as st
import os

# Configuração da página (Mantida exatamente como a sua)
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
# 1. NOVA BASE DE CONHECIMENTO (Substitui o manual.txt)
# ---------------------------------------------------------
# Aqui você vai cadastrar todas as regras do seu manual.
# Adicionei a regra do Carro de Apoio que estava no seu prompt original.
BASE_CONHECIMENTO = [
    {
        "topico": "Princípios Básicos da Assistência",
        "palavras_chave": ["princípios básicos", "urgência", "emergência", "quem pode acionar", "direito ao serviço", "veículo ativo"],
        "resposta": "Atendimento de serviços de Urgência e Emergência: O veículo está impedido de se locomover por meios próprios e sua locomoção representa risco iminente ao condutor, passageiros ou demais entes do trânsito.[cite: 1] A assistência veicular 24 horas, não deve ser confudida com serviço de conveniência ou comodidade.[cite: 1] Os serviços são aplicáveis a veículos de passeio, motocicletas, utilitários e pesados, desde que o veículo esteja devidamente cadastrado na base da assistência 24 horas – ATIVO.[cite: 1] A cobertura é para o veículo e seus ocupantes, assim, qualquer pessoa que esteja conduzindo o veículo pode solicitar atendimento.[cite: 1]"
    },
    {
        "topico": "Planos e Fracionamento",
        "palavras_chave": ["planos", "limite de quilometragem", "fracionamento", "saldo de km", "sobra de km"],
        "resposta": "Plano de assistência veicular é um conjunto de serviços com limites de quilometragem e quantidade de utilização.[cite: 1] Ao ultrapassar o limite, o custo do deslocamento excedente será por conta do condutor, e deverá ser pago no ato diretamente ao prestador.[cite: 1] Em casos de fracionamento, não poderá ultrapassar a quilometragem total do plano contratado.[cite: 1] O atendimento é dado como encerrado na chegada ao destino, não restando direito a utilização de eventual saldo/sobra de quilometragem quando a distância for inferior ao limite.[cite: 1]"
    },
    {
        "topico": "Fato Gerador",
        "palavras_chave": ["fato gerador", "quais são os fatos", "motivo do atendimento"],
        "resposta": "É o evento externo que causa a paralização do veículo.[cite: 1] São eles: Acidente/Colisão/Incêndio, Falta de Combustível, Furto de Pneu(s) ou Roda(s), Furto ou Roubo Recuperado, Incidente com Chaves, Pane Elétrica ou Mecânica e Pneu(s) Avariado(s).[cite: 1]"
    },
    {
        "topico": "Regras Gerais dos Serviços da Assistência",
        "palavras_chave": ["serviços da assistência", "assistência pneumática", "troca de pneu", "auxílio combustível", "chaveiro", "abertura de porta", "carga de bateria", "socorro elétrico"],
        "resposta": "Os serviços de Assistência Pneumática (troca de pneus), Auxílio Combustível (envio de até 5 litros), Chaveiro (abertura de portas) e Socorro Elétrico/Mecânico (carga de bateria) poderão solicitar a remoção do veículo caso não sejam conclusivos.[cite: 1] Nesses casos, o veículo será removido, respectivamente, para a borracharia, posto e chaveiro mais próximo.[cite: 1]"
    },
    {
        "topico": "Carro de Apoio",
        "palavras_chave": ["carro de apoio", "apoio", "carro extra"],
        "resposta": "Sempre que for questionado a respeito do carro de apoio e não tiver nenhuma informação no manual, exiba a seguinte mensagem: Para solicitação de carro de apoio é necessário fotos e videos para incluir no histórico do atendimento.[cite: 1]"
    },
    {
        "topico": "Veículos Inativos",
        "palavras_chave": ["inativo", "fora da base", "sem cobertura", "cancelado"],
        "resposta": "Não será realizado atendimento para o veículo que estiver INATIVO ou FORA DA BASE de cadastro da central de atendimento.[cite: 1] A central informará que o veículo está SEM COBERTURA, COBERTURA INATIVA ou SIMILAR.[cite: 1]"
    },
    {
        "topico": "Atendimentos Dentro e Fora do Horário Comercial",
        "palavras_chave": ["horário comercial", "fora do horário", "continuação de atendimento", "dia subsequente"],
        "resposta": "Dentro do horário comercial: Ao chegar no destino, o atendimento é conclusivo e o cliente não terá direito a continuação ou um novo atendimento pelo mesmo fato gerador.[cite: 1] Fora do horário comercial: Se o veículo foi enviado para a base do prestador ou domicílio, será facultada a continuação no primeiro dia subsequente.[cite: 1] Se enviado para endereço desconhecido, é dado como conclusivo sem direito a continuação.[cite: 1] A continuidade ocorre se o destino não estiver mais aberto, o condutor não souber o endereço, ou indisponibilidade de prestador para média/longa distância fora do horário.[cite: 1]"
    },
    {
        "topico": "Serviços Acessórios e Complementos",
        "palavras_chave": ["serviços acessórios", "complemento", "diária de hotel", "mta", "guarda de veículo"],
        "resposta": "Em impossibilidade de remoção imediata fora do horário comercial, existem ferramentas para proporcionar segurança: Diária de Hotel, MTA (Meio de Transporte Alternativo) e Guarda de veículo.[cite: 1] Importante: Uso do reboque é pré-requisito.[cite: 1]"
    },
    {
        "topico": "Atendimentos sem Cobertura (Restrições Gerais)",
        "palavras_chave": ["sem cobertura", "não cobre", "atolado", "sem acesso", "estrada de terra", "cnt", "apreendido", "destombamento geral", "resgate geral", "carregado", "mercadoria", "busca e apreensão", "oficina para oficina", "atividade remunerada", "táxi para passageiro"],
        "resposta": "Veículo atolado ou sem acesso: Negligência ou via não reconhecida exigem que o cliente providencie meios próprios para levar à via pavimentada, sem reembolso.[cite: 1] Desacordo com CNT: Veículos retidos/apreendidos por descumprir leis de trânsito não têm cobertura.[cite: 1] Destombamento/Resgate: Não incluídos nos planos gerais (verificar exceções).[cite: 1] Veículos carregados: Não se remove com mercadorias (salvo uso pessoal).[cite: 1] Busca e apreensão/furto/roubo: Não é realizada remoção.[cite: 1] Oficina para oficina: Não contemplado, pois não é emergencial.[cite: 1] Atividade remunerada: MTA, Táxi e Hotel são facultados somente ao condutor, a responsabilidade dos passageiros é do cliente.[cite: 1]"
    },
    {
        "topico": "Atendimentos Específicos: Cavalo Mecânico, Animais e Frustrados",
        "palavras_chave": ["cavalo mecânico", "engatado", "desatrelado", "reembolso", "atendimento frustrado", "animais", "cachorro", "gato"],
        "resposta": "Cavalo mecânico: O cliente deve desengatar/desatrelar e estacionar com pés de apoio; o prestador tracionará o cavalo e providenciará a remoção.[cite: 1] Atendimentos frustrados: Se a central não acionar prestador e autorizar, o cliente realiza por meios próprios e pede reembolso via e-mail (reembolso@grupoassistme.com.br) com dados e nota fiscal.[cite: 1] Animais: Prestadores não são obrigados a transportar animais em MTA/Táxi/Hotel; tenta-se prosseguir, mas se impossível, o cliente segue por meios próprios sem reembolso.[cite: 1]"
    },
    {
        "topico": "Comunicação e Máscaras (SMS, Previsões e Valores)",
        "palavras_chave": ["sms", "falta de contato", "busca de prestadores", "nova previsão", "valores praticados", "preço do reboque", "veículo leve", "veículo pesado", "utilitário"],
        "resposta": "Máscaras devem ser preenchidas para Falta de Contato, Busca de Prestadores, Nova Prévia, Atraso ou Cancelamento.[cite: 1] Valores praticados no mercado: Veículo Leve (Saída R$170,00, km excedente R$3,50), Utilitários (Saída R$200,00, km excedente R$4,00) e Pesados (Saída R$700,00, km excedente R$7,00).[cite: 1]"
    },
    {
        "topico": "Veículos para Base e Formalização",
        "palavras_chave": ["veículo para base", "base do prestador", "madrugada", "noturno", "formalização", "agendamento"],
        "resposta": "Se o veículo for para a base durante a madrugada para segurança, o cliente deve ligar no próximo dia útil para solicitar a remoção, sob pena de pagar diárias. Pode usufruir de Hotel se o plano cobrir.[cite: 1] É obrigatório formalizar o serviço informando o endereço de origem e destino, aguardando o 'De acordo' do solicitante, inclusive em agendamentos.[cite: 1]"
    },
    {
        "topico": "Placa Mercosul e Máscara de Reembolso",
        "palavras_chave": ["placa mercosul", "letras da placa", "processo de reembolso", "máscara de reembolso"],
        "resposta": "Substituição Placa Mercosul: 0=A, 1=B, 2=C, 3=D, 4=E, 5=F, 6=G, 7=H, 8=I, 9=J.[cite: 1] Reembolso: Deve registrar serviço com valor, passageiros e motivo, vinculando o prestador REEMBOLSO CLIENTE.[cite: 1]"
    },
    {
        "topico": "Associação AAVB",
        "palavras_chave": ["aavb", "reboque aavb", "destombamento aavb", "estrada de terra aavb"],
        "resposta": "AAVB - Remoção para endereço de residência não cadastrada tem direito a continuação.[cite: 1] Resgate e destombamento: Necessário fotos/vídeos; libera alçada de R$200,00 e o excedente é do cliente.[cite: 1] Estrada de terra: Cliente tem direito, coletar e notificar supervisor; sem retorno, seguir cobertura.[cite: 1]"
    },
    {
        "topico": "Associação AAVM",
        "palavras_chave": ["aavm", "reboque aavm", "estrada de terra aavm", "pane aavm", "táxi aavm", "mta aavm", "hotel aavm"],
        "resposta": "AAVM - Acidente/Colisão/Incêndio: Obrigatoriamente para a Base do Prestador (custo da associação) e orientar contato com ADM.[cite: 1] Pane Elétrica/Mecânica: Comercial envia para oficina mais próxima até 200km totais; Fora do Comercial envia para base ou domicílio (alçada 200km totais), sem mencionar limite de 100km na ligação.[cite: 1] Estrada de terra: Tem direito com autorização.[cite: 1] Resgate: Requer fotos/vídeos.[cite: 1] Táxi Urbano: R$100,00 limitados a 50km totais (plano Light não tem MTA).[cite: 1] Retorno/Continuação (Acidente/Colisão/Incêndio/Furto/Roubo): R$350,00 para passagens.[cite: 1] Resgate: Alçada de R$200,00.[cite: 1] Hotel (mesmos fatos geradores graves): R$500,00.[cite: 1] Chaveiro: Cobertura padrão R$160,00.[cite: 1]"
    },
    {
        "topico": "Associação ACTR",
        "palavras_chave": ["actr", "reboque actr"],
        "resposta": "ACTR - Todos os fatos geradores: Encaminhar para oficina ou destino dentro de 200km de deslocamento totais.[cite: 1] Se ultrapassar, colocar em análise sem apresentar objeções.[cite: 1]"
    },
    {
        "topico": "Associação ALFA BAHIA",
        "palavras_chave": ["alfa bahia", "reboque alfa bahia", "estrada de terra alfa bahia"],
        "resposta": "ALFA BAHIA - Estrada de terra: Tem direito à remoção; se valores acima do mercado, pedir autorização.[cite: 1] Todos os fatos: Prerrogativa de oficina mais próxima em raio de 200km totais; se cliente não aceitar, pedir liberação no grupo.[cite: 1]"
    },
    {
        "topico": "Associação ALICERCE",
        "palavras_chave": ["alicerce", "reboque alicerce", "pneu alicerce", "destombamento alicerce", "mta alicerce"],
        "resposta": "ALICERCE - Reboque: Encaminhar para oficina ou destino com limite de 300km totais; se ultrapassar, questionar opções, verificar outro recurso e colocar em análise.[cite: 1] Estrada de terra: Tem direito mediante autorização do supervisor.[cite: 1] Assistência Pneumática: Não possui cobertura para Pneus Avariados; orientar ligar no (31) 2559-8004.[cite: 1] Destombamento/Resgate: Até R$2.000,00 por evento.[cite: 1] MTA Urbano/Retorno: Limite total de R$200,00 por evento.[cite: 1]"
    },
    {
        "topico": "Associações ABAPAV, AGIBENS e AGN",
        "palavras_chave": ["abapav", "chaveiro abapav", "agibens", "reboque agibens", "táxi agibens", "agn", "reboque agn", "táxi agn", "mta agn", "resgate agn", "hotel agn"],
        "resposta": "ABAPAV - Chaveiro: Fornece remoção de chaves quebradas e mão de obra de confecção (cliente paga o material).[cite: 1] AGIBENS - Reboque 200km totais e Táxi Urbano de até R$50,00.[cite: 1] AGN - Reboque 200km totais (se passar, pedir autorização e aguardar 15 min). Não contempla patins nem carro de apoio.[cite: 1] Pane/Combustível/Chave/Pneu fora do comercial: residência até 40km totais (conclusivo).[cite: 1] Táxi: R$50,00 até 50km totais.[cite: 1] MTA (Acidente/Colisão/Incêndio/Roubo): R$350,00 passagens.[cite: 1] Resgate: R$200,00.[cite: 1] Hotel (Acidente/Colisão/Incêndio/Roubo): R$500,00.[cite: 1]"
    },
    {
        "topico": "Associações ABS BOM SUCESSO, AMI, AVEP",
        "palavras_chave": ["abs", "bom sucesso", "ami", "reboque ami", "avep", "reboque avep", "táxi avep", "hotel avep", "base avep"],
        "resposta": "ABS BOM SUCESSO - Reboque acima de 300km totais exige autorização.[cite: 1] Pneus avariados vão para borracharia sem escolha de destino.[cite: 1] AMI - Mesmas regras da AGN para reboque (200km), táxi (50km/R$50), MTA (R$350), Resgate (R$200) e Hotel (R$500). Não tem carro de apoio.[cite: 1] AVEP - Reboque 200km totais para oficina. Residência não cadastrada tem direito a continuação no dia útil.[cite: 1] Via não reconhecida coberta.[cite: 1] Táxi até R$300,00 (150km totais).[cite: 1] Resgate R$2.500,00.[cite: 1] Base: AVEP paga diária para Acidente/Colisão/Incêndio; Pane cliente paga.[cite: 1] MTA Passagens: R$400,00. Hotel: 3 diárias de R$150,00.[cite: 1] Sem carro de apoio.[cite: 1]"
    },
    {
        "topico": "Associações AUTOCLASS, BR TRUCK, BV TRUCK, CLICK CAR, CLIKAR",
        "palavras_chave": ["autoclass", "br truck", "resgate br truck", "bv truck", "click car", "táxi click car", "hotel click car", "clikar"],
        "resposta": "AUTOCLASS e BV TRUCK - Oficina/Destino dentro de 200km totais, acima disso colocar em análise.[cite: 1] BR TRUCK - MTA Retorno/Continuação reembolsa passagens apenas para Acidente/Colisão/Incêndio/Roubo. Resgate exige fotos de todos os ângulos para autorização.[cite: 1] CLICK CAR e CLIKAR - Oficina em 200km totais, se não aceitar, pedir liberação no grupo.[cite: 1] CLICK CAR tem Táxi até R$100,00 (100km via reembolso) e Hotel de 1 diária (R$200,00).[cite: 1]"
    },
    {
        "topico": "Associações CLUB CAR, CONFIANCE, COOPERVALES, COOPERTRAX",
        "palavras_chave": ["club car", "reboque club car", "confiance", "coopervales", "táxi coopervales", "coopertrax"],
        "resposta": "CLUB CAR - Reboque 200km totais (aguardar 15 min no grupo). Levar para residência não cadastrada garante continuação durante o mês.[cite: 1] Acidente/Colisão/Incêndio vai para residência e cliente contata ADM.[cite: 1] CONFIANCE e COOPERTRAX - Reboque acima de 200km totais pedir liberação.[cite: 1] COOPERVALES - Reboque 200km totais, Táxi até R$300,00 e cobre via não reconhecida.[cite: 1]"
    },
    {
        "topico": "Associações DIGICAR, ESTILO, EXCLUSIVA, FORTE CAR",
        "palavras_chave": ["digicar", "plantonista digicar", "estilo", "táxi estilo", "chaveiro estilo", "exclusiva", "forte car", "reboque forte car"],
        "resposta": "DIGICAR - Reboque 200km totais; plantonistas Euler (31)9275-4187 e Romulo (31)9168-4363, não possui vistoria in loco.[cite: 1] ESTILO - Táxi/MTA de R$100,00 para Panes. Chaveiro cobre remoção de chave quebrada. Cobre estrada de terra.[cite: 1] EXCLUSIVA - Reboque 200km totais.[cite: 1] FORTE CAR - Panes: Oficina em 200km totais; Acidente/Colisão/Incêndio: Oficina em 200km totais ou Base/Residência se não tiver retorno do grupo.[cite: 1]"
    },
    {
        "topico": "Associações GASP, GRAZIOTHI, GO LOCK, IDEAL",
        "palavras_chave": ["gasp", "gestora", "fácil auto", "hora trabalhada", "graziothi", "go lock", "reboque go lock", "táxi go lock", "ideal", "reboque ideal"],
        "resposta": "GASP - Reboque acima de 200km totais precisa notificar supervisor; não contempla hora trabalhada/parada.[cite: 1] GRAZIOTHI - Reboque 200km totais ou análise.[cite: 1] GO LOCK - Panes: Oficina em 200km totais; Acidente/Colisão/Incêndio: Local seguro pelo plano (se base, diária é do condutor).[cite: 1] Sem carro de apoio.[cite: 1] Táxi R$150,00, Passagens R$300,00, Hospedagem R$100,00.[cite: 1] IDEAL - Panes: Oficina em 200km totais (se não aceitar, reembolso no ADM). Acidente: Acima de 400km totais pede autorização no grupo.[cite: 1]"
    },
    {
        "topico": "Associação INOVAR",
        "palavras_chave": ["inovar", "reboque inovar", "combustível inovar", "táxi inovar", "mta inovar", "passagens inovar"],
        "resposta": "INOVAR - Acima de 200km totais colocar em análise; sem retorno, enviar para Residência ou Base.[cite: 1] Falta de combustível: Cliente paga gasolina 5L e o galão (R$20,00).[cite: 1] Veículo carregado tem alçada de R$200,00.[cite: 1] Resgate exige fotos/vídeos no grupo.[cite: 1] Táxi Urbano tem alçada de R$600,00; MTA (Retorno/Continuação) libera R$600,00 para outro meio se não tiver ônibus num raio de 2h de espera (não informar excedente ao cliente).[cite: 1]"
    },
    {
        "topico": "Associações INNOVE, LIBRE, LIDERY, LIFECLUB",
        "palavras_chave": ["innove", "reboque innove", "resgate innove", "libre", "lidery", "hotel lidery", "lifeclub", "táxi lifeclub"],
        "resposta": "INNOVE - Reboque 200km totais (esperar 15 min), Resgate alçada de R$250,00, cobre via não reconhecida.[cite: 1] LIBRE - Reboque 200km totais e cobre estrada de terra com notificação.[cite: 1] LIDERY - Pane elétrica/mecânica vai para oficina até 200km totais; Hotel tem 3 diárias limitadas a R$120,00 total por dia.[cite: 1] LIFECLUB - Não contempla serviço de táxi.[cite: 1]"
    },
    {
        "topico": "Associações MOTOR HOME, MG CAR, MYPASS",
        "palavras_chave": ["motor home", "reboque motor home", "táxi motor home", "destombamento motor home", "mg car", "mypass"],
        "resposta": "MOTOR HOME - Oficina/Destino em 200km totais; Táxi até R$70,00 (40km totais).[cite: 1] Destombamento em via pública via reembolso (R$2.500 veículo ou R$5.000 conjunto), não cobre resgate; permite patins e residencial é 100% reembolso.[cite: 1] MG CAR - Tem cobertura padrão de MTA/Táxi/Hotel.[cite: 1] MYPASS - Panes vai para oficina em 200km totais; Acidente padrão do plano; Não enviar serviços em análise no grupo da My Pass.[cite: 1]"
    },
    {
        "topico": "Associações NACIONAL CAR, NEXOOS, NÚCLEO PROTEÇÃO",
        "palavras_chave": ["nacional car", "nexoos", "hotel nexoos", "núcleo proteção", "táxi núcleo"],
        "resposta": "NACIONAL CAR - Resgate sob consulta no grupo com fotos/vídeos.[cite: 1] NEXOOS - Reboque 200km totais (15 min espera), Táxi R$150,00, Hotel 1 diária R$100,00.[cite: 1] NÚCLEO PROTEÇÃO - Reboque 200km totais, Táxi até R$200,00, MTA passagens a partir de 100km e 1 diária de Hotel R$100,00.[cite: 1]"
    },
    {
        "topico": "Associações PORTO SUL, PRIX, PROAPP, PROLINE",
        "palavras_chave": ["porto sul", "prix", "proapp", "proline", "reboque proline"],
        "resposta": "PORTO SUL - Comercial oficina 200km totais; Fora do comercial base ou domicílio 200km totais; cobre estrada de terra.[cite: 1] PRIX e PROLINE - Panes para oficina 200km totais; Acidente para oficina 200km totais ou Base/Residência se não tiver retorno do grupo. Proline cobre via não reconhecida.[cite: 1] PROAPP - Reboque 200km totais ou liberação no grupo.[cite: 1]"
    },
    {
        "topico": "Associações PROTEGE MAIS, PORTO BRASIL, POSITIVE CAR, REAL TRUCK",
        "palavras_chave": ["protege mais", "porto brasil", "positive car", "real truck", "oficina para oficina", "hotel real truck"],
        "resposta": "PROTEGE MAIS, PORTO BRASIL e POSITIVE CAR - Reboque 200km totais (100 ida e volta) ou liberação no grupo.[cite: 1] REAL TRUCK - Permite remoção Oficina para Oficina se não usou reboque por Pane no mês.[cite: 1] Resgate alçada de R$500,00.[cite: 1] Hotel 1 diária de R$150,00 por pessoa (máx R$300). Acidente acima de 1000km pede autorização; Táxi até R$150,00.[cite: 1]"
    },
    {
        "topico": "Associações SPLIT RISK e Filiais",
        "palavras_chave": ["split risk", "globus seguros", "stop club", "lince seguros", "turquim seguros", "meo seguros"],
        "resposta": "SPLIT RISK e filiais (MY PASS, GLOBUS, LINCE, TURQUIM, MEO) - Panes no comercial vão para oficina em 200km totais; fora do comercial vão para local seguro do plano (se base, diária é do cliente).[cite: 1] Sem carro de apoio.[cite: 1] Táxi R$150,00, Passagens R$300,00, Hospedagem R$100,00.[cite: 1] Cobre estrada de terra notificando supervisor.[cite: 1]"
    },
    {
        "topico": "Associações SUPREMA, SUPERA, TÁXI FORT, TM BRASIL",
        "palavras_chave": ["suprema", "base suprema", "supera", "táxi supera", "chaveiro supera", "táxi fort", "tm brasil", "mineradora"],
        "resposta": "SUPREMA - Pane 200km totais; Acidente vai para Base do Prestador (associação paga diária), cliente contata ADM para retirar nas primeiras 4 horas úteis.[cite: 1] SUPERA - Táxi R$50,00, Retorno/Continuação R$200,00, Hotel R$200,00, Chaveiro R$100,00.[cite: 1] TÁXI FORT - Fora do comercial vai para base ou residência; Táxi somente para Acidente/Colisão/Incêndio até R$200,00 (200km totais).[cite: 1] TM BRASIL - Permite Oficina para Oficina se não usou reboque por Pane; cobre estrada de terra/mineradora.[cite: 1]"
    },
    {
        "topico": "Associações TRIAD, UNIBRAS, VENTURE, YOUCAR",
        "palavras_chave": ["triad", "base triad", "unibras mhais", "rio de janeiro", "unibrás benefícios", "belo horizonte", "venture", "youcar"],
        "resposta": "TRIAD - Reboque 200km totais. Acidente vai para Base do Prestador (associação paga diária) e cliente deve contatar ADM em 48h. Liberação da base só com autorização da associação.[cite: 1] UNIBRAS MHAIS (RJ) - Não contempla envio para base.[cite: 1] UNIBRÁS (BH) e VENTURE (apenas Pane) - Reboque 200km totais.[cite: 1] YOUCAR - Reboque 200km totais, Táxi R$200,00, Hotel 2 diárias de R$150,00, Resgate alçada de R$1.500,00 e cobre via não reconhecida.[cite: 1]"
    },
    {
        "topico": "Manual Residencial",
        "palavras_chave": ["residencial", "chaveiro residencial", "eletricista", "encanador", "vidraceiro", "desentupimento", "ar condicionado", "linha branca"],
        "resposta": "Chaveiro Emergencial: R$150,00 (3 por ano).[cite: 1] Eletricista: R$120,00 (3 por ano/1 por mês).[cite: 1] Encanador (tubulação aparente): R$120,00 (3 por ano/1 por mês).[cite: 1] Vidraceiro: R$150,00 (3 por ano/1 por mês).[cite: 1] Desentupimento: R$180,00 (3 por ano/1 por mês).[cite: 1] Limpeza de Ar Condicionado: R$180,00 (2 por ano, TRIAD a cada 6 meses).[cite: 1] Linha Branca/Marrom: R$160,00 (2 por ano/1 por mês).[cite: 1] Inspeção e Check-up Lar: R$120,00.[cite: 1]"
    },
    {
        "topico": "Erros Sistêmicos: Comunicação com a Hinova (SAME)",
        "palavras_chave": ["hinova", "same", "erro de comunicação", "token", "sincronização"],
        "resposta": "A mensagem indica que o TOKEN do cliente com a Hinova não está funcionando.[cite: 1] Passo 1: Verifique se outro item do mesmo cliente apresenta erro (Se sim, passo 2; Se não, avise suporte SAME).[cite: 1] Passo 2: Verifique outro cliente (Se sim, avise suporte; Se não, passo 3).[cite: 1] Passo 3: Tente sincronizar os itens da base (Se der certo, avise suporte; Se errado, passo 4).[cite: 1] Passo 4: Informe no grupo que há indisponibilidade na consulta do SGA.[cite: 1] Passo 5: O atendimento só pode ser aberto conforme último status (ATIVO abre normal; INATIVO abre particular).[cite: 1]"
    }
]

# ---------------------------------------------------------
# 2. FUNÇÃO DE BUSCA (Substitui o LangChain e a IA)
# ---------------------------------------------------------
def buscar_no_manual(pergunta):
    # Transforma a pergunta em letras minúsculas para facilitar a busca
    pergunta_formatada = pergunta.lower()
    
    # Procura na nossa base de conhecimento
    for item in BASE_CONHECIMENTO:
        for palavra in item["palavras_chave"]:
            if palavra in pergunta_formatada:
                return item["resposta"]
    
    # Se não encontrar nenhuma palavra-chave, retorna a regra padrão do seu sistema
    return "⚠️ NÃO CONTEMPLADO. Siga a cobertura padrão da Central de Atendimento e verifique com a supervisão."


# ---------------------------------------------------------
# 3. LÓGICA DO CHAT (Interface do Streamlit)
# ---------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

caixa_chat = st.container()
caixa_chat.markdown("<div id='caixa-chat-ancora'></div>", unsafe_allow_html=True)

# Desenha as mensagens antigas na tela
with caixa_chat:
    for message in st.session_state.messages:
        avatar = "👤" if message["role"] == "user" else "🤖"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

# Recebe a nova pergunta do usuário
if pergunta := st.chat_input("Qual é a sua dúvida operacional ou regra de acionamento?"):
    
    # Exibe a pergunta do usuário
    st.session_state.messages.append({"role": "user", "content": pergunta})
    with caixa_chat:
        with st.chat_message("user", avatar="👤"):
            st.markdown(pergunta)
            
    # Gera e exibe a resposta do assistente
    with caixa_chat:
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Buscando regras operacionais..."):
                
                # Chama a nova função de busca em vez de chamar a IA
                resposta = buscar_no_manual(pergunta)
                
                st.markdown(resposta)
                st.session_state.messages.append({"role": "assistant", "content": resposta})
