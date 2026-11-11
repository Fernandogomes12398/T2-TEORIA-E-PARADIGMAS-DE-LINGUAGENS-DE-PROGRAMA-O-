import json, sys
from itertools import combinations

def load(p):
    with open(p) as f:
        return json.load(f)

def tem_ciclo(disciplinas):
    for d in disciplinas:
        if d["codigo"] in d.get("prerequisitos", []):
            return [d["codigo"], d["codigo"]]
    return None

def main():
    dados = load(sys.argv[1])
    matriz = dados["matriz"]["disciplinas"]
    oferta = dados["oferta"]["disciplinas"]
    hist = dados["historico"]
    aprovadas = set(hist["aprovadas"])
    teto = hist["teto_ch"]

    ciclo = tem_ciclo(matriz)
    if ciclo:
        print(json.dumps({"ciclo": ciclo, "liberadas": None, "bloqueadas": None, "grades_maximas": None}))
        return

    liberadas = []
    bloqueadas = []
    for o in oferta:
        if o["codigo"] in aprovadas:
            continue
        d = next(x for x in matriz if x["codigo"] == o["codigo"])
        faltam = [p for p in d["prerequisitos"] if p not in aprovadas]
        if not faltam:
            liberadas.append(o["codigo"])
        else:
            bloqueadas.append({"codigo": o["codigo"], "faltam": faltam})

    liberadas.sort()
    bloqueadas.sort(key=lambda x: x["codigo"])

    melhor = []
    for r in range(len(liberadas), 0, -1):
        for combo in combinations(liberadas, r):
            soma = sum(next(x for x in matriz if x["codigo"] == c)["ch"] for c in combo)
            if soma <= teto:
                melhor.append(list(combo))
        if melhor:
            break
    if not melhor:
        melhor = [[]]
    melhor.sort()

    print(json.dumps({
        "ciclo": None,
        "liberadas": liberadas,
        "bloqueadas": bloqueadas,
        "grades_maximas": melhor,
    }, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()