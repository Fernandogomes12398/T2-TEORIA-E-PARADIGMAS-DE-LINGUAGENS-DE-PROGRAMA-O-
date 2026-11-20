import json
import sys
import os
from typing import Any, Dict, FrozenSet, Optional, Tuple

# Tipos imutáveis do domínio
Horario = Tuple[str, str]
Disciplina = Tuple[str, str, int, Tuple[str, ...]]
OfertaItem = Tuple[str, FrozenSet[Horario]]

# =====================================================================
# CASCA IMPURA (Fronteira de I/O)
# =====================================================================

def carregar_json(caminho: str) -> Dict[str, Any]:
    with open(caminho, "r", encoding="utf-8") as f:
        return json.load(f)

def ler_entrada(alvo: str) -> Tuple[Dict, Dict, Dict]:
    if os.path.isdir(alvo):
        matriz = carregar_json(os.path.join(alvo, "matriz.json"))
        oferta = carregar_json(os.path.join(alvo, "oferta.json"))
        historico = carregar_json(os.path.join(alvo, "historico.json"))
        return matriz, oferta, historico
    dados = carregar_json(alvo)
    return dados["matriz"], dados["oferta"], dados["historico"]

# =====================================================================
# NÚCLEO PURO
# =====================================================================

def normalizar_matriz(dados_matriz: Dict[str, Any]) -> Tuple[Disciplina, ...]:
    return tuple(
        (
            d["codigo"],
            d["nome"],
            int(d["ch"]),
            tuple(sorted(d["prerequisitos"])),
        )
        for d in sorted(dados_matriz["disciplinas"], key=lambda x: x["codigo"])
    )

def normalizar_oferta(dados_oferta: Dict[str, Any]) -> Tuple[OfertaItem, ...]:
    return tuple(
        (
            item["codigo"],
            frozenset(item["horarios"]),  # Os horários já vêm como strings, ex: "SEG-M"
        )
        for item in sorted(dados_oferta["disciplinas"], key=lambda x: x["codigo"])
    )
def normalizar_historico(dados_hist: Dict[str, Any]) -> Tuple[FrozenSet[str], int]:
    return (frozenset(dados_hist["aprovadas"]), int(dados_hist["teto_ch"]))

# ---------------------------------------------------------------------
# Pergunta 1: Ciclo (Recursão explícita, sem reduce e sem reversed)
# ---------------------------------------------------------------------

def encontrar_ciclo(matriz: Tuple[Disciplina, ...]) -> Optional[Tuple[str, ...]]:
    mapa_prereqs = tuple((cod, prereqs) for cod, _, _, prereqs in matriz)

    def buscar_prereqs(cod: str) -> Tuple[str, ...]:
        return next((p for c, p in mapa_prereqs if c == cod), ())

    def dfs(no: str, caminho: Tuple[str, ...], visitados: FrozenSet[str]) -> Tuple[Optional[Tuple[str, ...]], FrozenSet[str]]:
        if no in caminho:
            idx = caminho.index(no)
            return (caminho[idx:] + (no,), visitados) # Retorna o caminho na ordem causal

        if no in visitados:
            return (None, visitados)

        novo_caminho = caminho + (no,)
        vizinhos = buscar_prereqs(no)

        def explorar(vzs: Tuple[str, ...], vis: FrozenSet[str]) -> Tuple[Optional[Tuple[str, ...]], FrozenSet[str]]:
            if not vzs:
                return (None, vis)
            ciclo, nova_vis = dfs(vzs[0], novo_caminho, vis)
            if ciclo is not None:
                return (ciclo, nova_vis)
            return explorar(vzs[1:], nova_vis)

        ciclo_sub, vis_final = explorar(vizinhos, visitados)
        return (ciclo_sub, vis_final | frozenset((no,)))

    def percorrer_todos(discs: Tuple[Disciplina, ...], vis: FrozenSet[str]) -> Optional[Tuple[str, ...]]:
        if not discs:
            return None
        ciclo, nova_vis = dfs(discs[0][0], (), vis)
        if ciclo is not None:
            return ciclo
        return percorrer_todos(discs[1:], nova_vis)

    return percorrer_todos(matriz, frozenset())

# ---------------------------------------------------------------------
# Perguntas 2 e 3: Liberadas e Bloqueadas
# ---------------------------------------------------------------------

def classificar_oferta(
    matriz: Tuple[Disciplina, ...],
    oferta: Tuple[OfertaItem, ...],
    aprovadas: FrozenSet[str],
) -> Tuple[Tuple[str, ...], Tuple[Tuple[str, Tuple[str, ...]], ...]]:
    codigos_ofertados = frozenset(cod for cod, _ in oferta)

    candidatas = tuple(
        disc for disc in matriz
        if disc[0] in codigos_ofertados and disc[0] not in aprovadas
    )

    def faltantes_de(disc: Disciplina) -> Tuple[str, ...]:
        return tuple(sorted(p for p in disc[3] if p not in aprovadas))

    liberadas = tuple(sorted(disc[0] for disc in candidatas if not faltantes_de(disc)))

    bloqueadas = tuple(
        (disc[0], faltantes_de(disc))
        for disc in candidatas
        if faltantes_de(disc)
    )

    return (liberadas, bloqueadas)

# ---------------------------------------------------------------------
# Pergunta 4: Maior grade (Com poda para não explodir)
# ---------------------------------------------------------------------

def encontrar_grades_maximas(
    matriz: Tuple[Disciplina, ...],
    oferta: Tuple[OfertaItem, ...],
    liberadas: Tuple[str, ...],
    teto_ch: int,
) -> Tuple[Tuple[str, ...], ...]:
    set_liberadas = frozenset(liberadas)
    
    itens = tuple(
        (cod, next(ch for c, _, ch, _ in matriz if c == cod), next(hrs for c, hrs in oferta if c == cod))
        for cod in sorted(liberadas)
    )

    def gerar_validas(
        restantes: Tuple[Tuple[str, int, FrozenSet[Horario]], ...],
        grade_atual: Tuple[str, ...],
        ch_atual: int,
        horarios_ocupados: FrozenSet[Horario],
        melhor_tam: int
    ) -> Tuple[Tuple[Tuple[str, ...], ...], int]:
        
        # Poda: se a grade atual + o que resta não bate o recorde, aborta
        if len(grade_atual) + len(restantes) < melhor_tam:
            return ((), melhor_tam)

        if not restantes:
            if len(grade_atual) > melhor_tam:
                return ((grade_atual,), len(grade_atual))
            elif len(grade_atual) == melhor_tam:
                return ((grade_atual,), melhor_tam)
            return ((), melhor_tam)

        (cod, ch, hrs), cauda = restantes[0], restantes[1:]
        
        # Ramo 1: Incluir (se couber e não conflitar)
        pode_incluir = (ch_atual + ch <= teto_ch) and horarios_ocupados.isdisjoint(hrs)
        v_com, m_com = ((), melhor_tam)
        if pode_incluir:
            v_com, m_com = gerar_validas(cauda, grade_atual + (cod,), ch_atual + ch, horarios_ocupados | hrs, melhor_tam)
        
        # Ramo 2: Pular
        v_sem, m_sem = gerar_validas(cauda, grade_atual, ch_atual, horarios_ocupados, m_com)

        return (v_com + v_sem, m_sem)

    validas, _ = gerar_validas(itens, (), 0, frozenset(), 0)
    
    if not validas:
        return ((),)
    
    return tuple(sorted(validas))

# ---------------------------------------------------------------------
# Orquestração pura
# ---------------------------------------------------------------------

def resolver(dados_matriz: Dict, dados_oferta: Dict, dados_hist: Dict) -> Dict[str, Any]:
    matriz = normalizar_matriz(dados_matriz)
    ciclo = encontrar_ciclo(matriz)

    if ciclo is not None:
        return {
            "ciclo": list(ciclo),
            "liberadas": None,
            "bloqueadas": None,
            "grades_maximas": None,
        }

    oferta = normalizar_oferta(dados_oferta)
    aprovadas, teto_ch = normalizar_historico(dados_hist)

    liberadas, bloqueadas = classificar_oferta(matriz, oferta, aprovadas)
    grades_maximas = encontrar_grades_maximas(matriz, oferta, liberadas, teto_ch)

    return {
        "ciclo": None,
        "liberadas": list(liberadas),
        "bloqueadas": [
            {"codigo": cod, "faltam": list(faltam)} for cod, faltam in bloqueadas
        ],
        "grades_maximas": [list(g) for g in grades_maximas],
    }

def main() -> None:
    if len(sys.argv) != 2:
        sys.stderr.write("Uso: python3 main.py <diretorio_dados | arquivo_caso>\n")
        sys.exit(1)

    dados_matriz, dados_oferta, dados_hist = ler_entrada(sys.argv[1])
    resultado = resolver(dados_matriz, dados_oferta, dados_hist)
    print(json.dumps(resultado, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()