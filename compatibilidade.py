def _tipo(peca):
    return str(peca.get("tipo") or "").lower()


def _primeira(itens, texto):
    for item in itens:
        peca = item.get("pecas") or item
        if texto in _tipo(peca):
            return peca
    return None


def verificar_compatibilidade(itens):
    avisos = []

    cpu = _primeira(itens, "processador")
    placa_mae = _primeira(itens, "placa-mãe") or _primeira(itens, "placa-mae")
    ram = _primeira(itens, "memória ram") or _primeira(itens, "memoria ram")
    gpu = _primeira(itens, "placa de vídeo") or _primeira(itens, "placa de video")
    fonte = _primeira(itens, "fonte")
    gabinete = _primeira(itens, "gabinete")

    if cpu and placa_mae:
        socket_cpu = str(cpu.get("socket") or "").strip().upper()
        socket_mb = str(placa_mae.get("socket") or "").strip().upper()

        if socket_cpu and socket_mb:
            if socket_cpu == socket_mb:
                avisos.append(("ok", f"CPU e placa-mãe usam socket {socket_cpu}."))
            else:
                avisos.append((
                    "erro",
                    f"CPU usa {socket_cpu}, mas a placa-mãe usa {socket_mb}.",
                ))

    if ram and placa_mae:
        ram_tipo = str(ram.get("memoria_tipo") or "").strip().upper()
        mb_tipo = str(placa_mae.get("memoria_tipo") or "").strip().upper()

        if ram_tipo and mb_tipo:
            if ram_tipo == mb_tipo:
                avisos.append(("ok", f"RAM e placa-mãe usam {ram_tipo}."))
            else:
                avisos.append((
                    "erro",
                    f"A memória é {ram_tipo}, mas a placa-mãe exige {mb_tipo}.",
                ))

    if gpu and gabinete:
        gpu_mm = gpu.get("comprimento_mm")
        max_mm = gabinete.get("gpu_max_mm")

        if gpu_mm and max_mm:
            if float(gpu_mm) <= float(max_mm):
                avisos.append((
                    "ok",
                    f"A GPU ({float(gpu_mm):.0f} mm) cabe no gabinete "
                    f"({float(max_mm):.0f} mm disponíveis).",
                ))
            else:
                avisos.append((
                    "erro",
                    f"A GPU tem {float(gpu_mm):.0f} mm e o gabinete aceita "
                    f"até {float(max_mm):.0f} mm.",
                ))

    if gpu and fonte:
        recomendado = gpu.get("psu_recomendada_w")
        potencia = fonte.get("potencia_w")

        if recomendado and potencia:
            if float(potencia) >= float(recomendado):
                avisos.append((
                    "ok",
                    f"Fonte de {float(potencia):.0f} W atende a recomendação "
                    f"de {float(recomendado):.0f} W da GPU.",
                ))
            else:
                avisos.append((
                    "erro",
                    f"A GPU recomenda {float(recomendado):.0f} W, mas a fonte "
                    f"tem {float(potencia):.0f} W.",
                ))

    if placa_mae and gabinete:
        formato = str(placa_mae.get("formato") or "").strip().upper()
        suportados = str(gabinete.get("formatos_suportados") or "").upper()

        if formato and suportados:
            if formato in suportados:
                avisos.append(("ok", f"O gabinete suporta placa-mãe {formato}."))
            else:
                avisos.append((
                    "aviso",
                    f"Não encontrei {formato} nos formatos suportados pelo gabinete.",
                ))

    if not avisos:
        avisos.append((
            "aviso",
            "Faltam dados técnicos para validar compatibilidade. "
            "Preencha socket, tipo de memória, potência e dimensões nas peças.",
        ))

    return avisos
