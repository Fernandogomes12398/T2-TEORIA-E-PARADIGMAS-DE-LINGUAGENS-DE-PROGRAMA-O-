import json, os, random

N_DISC = 200
N_OFERTA = 16
DIAS = ["SEG", "TER", "QUA", "QUI", "SEX"]
TURNOS = ["M", "T"]

def gerar(seed=42):
    random.seed(seed)
    matriz = []
    for i in range(N_DISC):
        codigo = f"XX{i:04d}"
        prereqs = []
        if i > 0 and random.random() < 0.5:
            n_pr = random.choice([1, 1, 1, 2])
            candidatos = list(range(i))
            random.shuffle(candidatos)
            for j in candidatos[:n_pr]:
                prereqs.append(f"XX{j:04d}")
        matriz.append({"codigo": codigo, "nome": f"Disc {i}", "ch": random.choice([30, 60, 60, 60]), "prerequisitos": prereqs})

    escolhidas = random.sample(range(N_DISC), N_OFERTA)
    oferta = []
    for idx in escolhidas:
        n_h = random.choice([1, 2, 2, 2])
        horarios = []
        usados = set()
        while len(horarios) < n_h:
            par = f"{random.choice(DIAS)}-{random.choice(TURNOS)}"
            if par not in usados:
                usados.add(par)
                horarios.append(par)
        oferta.append({"codigo": matriz[idx]["codigo"], "horarios": horarios})

    aprovadas = []
    for i in range(N_DISC):
        if random.random() < 0.5:
            aprovadas.append(f"XX{i:04d}")

    return matriz, oferta, {"aprovadas": aprovadas, "teto_ch": 240}

if __name__ == "__main__":
    base = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(base, "ampliada")
    os.makedirs(out, exist_ok=True)
    matriz, oferta, historico = gerar()
    with open(os.path.join(out, "matriz.json"), "w") as f:
        json.dump({"disciplinas": matriz}, f, indent=2)
    with open(os.path.join(out, "oferta.json"), "w") as f:
        json.dump({"disciplinas": oferta}, f, indent=2)
    with open(os.path.join(out, "historico.json"), "w") as f:
        json.dump(historico, f, indent=2)
    print(f"gerado em {out}: {len(matriz)} disciplinas, {len(oferta)} na oferta")