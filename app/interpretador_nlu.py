import re

STATUS_VALIDOS = [
    "Pendente",
    "Em andamento",
    "Chamado Parado",
    "Chamado Retomado",
    "Chamado Finalizado"
]

def interpretar_comando(texto):
    chamado = None
    status_detectado = None

    # Expressões mais amplas para encontrar o número do chamado
    padrao_numero = re.search(r"(chamado(?: número)?(?: do)?(?: chamado)?\s*(\d+))", texto, re.IGNORECASE)
    if padrao_numero:
        chamado = int(padrao_numero.group(2))

    for status in STATUS_VALIDOS:
        if status.lower() in texto.lower():
            status_detectado = status
            break

    return chamado, status_detectado

