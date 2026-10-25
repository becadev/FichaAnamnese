def calcular_total(itens):
    total = 0
    for item in itens:
        if item.ativo:
            total += item.valor * item.quantidade
    desconto = total * 0.1
    return total - desconto
