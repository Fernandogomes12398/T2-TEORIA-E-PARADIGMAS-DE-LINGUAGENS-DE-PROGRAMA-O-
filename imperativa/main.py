import json
import sys
import os

def ordenar_lista(lst):
    n = len(lst)
    i = 1
    while i < n:
        chave = lst[i]
        j = i - 1
        while j >= 0 and lst[j] > chave:
            lst[j + 1] = lst[j]
            j = j - 1
        lst[j + 1] = chave
        i = i + 1
    return lst

def contem(lst, x):
    i = 0
    while i < len(lst):
        if lst[i] == x:
            return True
        i = i + 1
    return False

def copiar_lista(lst):
    nova = []
    i = 0
    while i < len(lst):
        nova.append(lst[i])
        i = i + 1
    return nova

def ch_of(matriz, codigo):
    i = 0
    while i < len(matriz):
        if matriz[i]["codigo"] == codigo:
            return matriz[i]["ch"]
        i = i + 1
    return 0

def prereqs_de(matriz, codigo):
    i = 0
    while i < len(matriz):
        if matriz[i]["codigo"] == codigo:
            return matriz[i]["prerequisitos"]
        i = i + 1
    return []

def carregar_json(caminho):
    with open(caminho, "r", encoding="utf-8") as f:
        return json.load(f)

def ler_entrada(alvo):
    if os.path.isdir(alvo):
        matriz = carregar_json(os.path.join(alvo, "matriz.json"))["disciplinas"]
        oferta = carregar_json(os.path.join(alvo, "oferta.json"))["disciplinas"]
        historico = carregar_json(os.path.join(alvo, "historico.json"))
        return matriz, oferta, historico
    dados = carregar_json(alvo)
    return dados["matriz"]["disciplinas"], dados["oferta"]["disciplinas"], dados["historico"]

def detectar_ciclo(matriz):
    n = len(matriz)
    cor = []
    i = 0
    while i < n:
        cor.append(0)
        i = i + 1
    caminho = []

    def dfs(idx):
        cor[idx] = 1
        caminho.append(matriz[idx]["codigo"])
        prereqs = matriz[idx]["prerequisitos"]
        k = 0
        while k < len(prereqs):
            pr = prereqs[k]
            j = 0
            alvo = -1
            while j < n:
                if matriz[j]["codigo"] == pr:
                    alvo = j
                    break
                j = j + 1
            if alvo != -1:
                if cor[alvo] == 1:
                    pos = 0
                    while pos < len(caminho):
                        if caminho[pos] == pr:
                            break
                        pos = pos + 1
                    ciclo = []
                    t = pos
                    while t < len(caminho):
                        ciclo.append(caminho[t])
                        t = t + 1
                    ciclo.append(pr)
                    return ciclo
                if cor[alvo] == 0:
                    r = dfs(alvo)
                    if r is not None:
                        return r
            k = k + 1
        caminho.pop()
        cor[idx] = 2
        return None

    i = 0
    while i < n:
        if cor[i] == 0:
            r = dfs(i)
            if r is not None:
                return r
        i = i + 1
    return None

def esta_liberada(matriz, aprovadas, codigo):
    prereqs = prereqs_de(matriz, codigo)
    i = 0
    while i < len(prereqs):
        if not contem(aprovadas, prereqs[i]):
            return False
        i = i + 1
    return True

def faltantes(matriz, aprovadas, codigo):
    prereqs = prereqs_de(matriz, codigo)
    faltam = []
    i = 0
    while i < len(prereqs):
        if not contem(aprovadas, prereqs[i]):
            faltam.append(prereqs[i])
        i = i + 1
    return ordenar_lista(faltam)

def classificar(matriz, oferta, aprovadas):
    liberadas = []
    bloqueadas = []
    i = 0
    while i < len(oferta):
        cod = oferta[i]["codigo"]
        if not contem(aprovadas, cod):
            if esta_liberada(matriz, aprovadas, cod):
                liberadas.append(cod)
            else:
                bloqueadas.append({"codigo": cod, "faltam": faltantes(matriz, aprovadas, cod)})
        i = i + 1
    ordenar_lista(liberadas)
    n = len(bloqueadas)
    a = 1
    while a < n:
        chave = bloqueadas[a]
        b = a - 1
        while b >= 0 and bloqueadas[b]["codigo"] > chave["codigo"]:
            bloqueadas[b + 1] = bloqueadas[b]
            b = b - 1
        bloqueadas[b + 1] = chave
        a = a + 1
    return liberadas, bloqueadas

def conflitam(h1, h2):
    i = 0
    while i < len(h1):
        j = 0
        while j < len(h2):
            if h1[i] == h2[j]:
                return True
            j = j + 1
        i = i + 1
    return False

def horarios_de(oferta, codigo):
    i = 0
    while i < len(oferta):
        if oferta[i]["codigo"] == codigo:
            return oferta[i]["horarios"]
        i = i + 1
    return []

def lex_menor(a, b):
    i = 0
    while i < len(a) and i < len(b):
        if a[i] < b[i]:
            return True
        if a[i] > b[i]:
            return False
        i = i + 1
    return len(a) < len(b)

def maior_grade(liberadas, oferta, matriz, teto):
    melhor = [[]]
    melhor_tam = 0
    atual = []

    def bt(idx):
        nonlocal melhor, melhor_tam
        if len(atual) + (len(liberadas) - idx) < melhor_tam:
            return
        if idx == len(liberadas):
            copia = copiar_lista(atual)
            ordenar_lista(copia)
            tam = len(copia)
            if tam > melhor_tam:
                melhor_tam = tam
                melhor = [copia]
            elif tam == melhor_tam and tam > 0:
                melhor.append(copia)
            return
        cand = liberadas[idx]
        ok = True
        soma = ch_of(matriz, cand)
        i = 0
        while i < len(atual):
            soma = soma + ch_of(matriz, atual[i])
            if conflitam(horarios_de(oferta, cand), horarios_de(oferta, atual[i])):
                ok = False
            i = i + 1
        if ok and soma <= teto:
            atual.append(cand)
            bt(idx + 1)
            atual.pop()
        bt(idx + 1)

    bt(0)

    n = len(melhor)
    a = 1
    while a < n:
        chave = melhor[a]
        b = a - 1
        while b >= 0 and lex_menor(chave, melhor[b]):
            melhor[b + 1] = melhor[b]
            b = b - 1
        melhor[b + 1] = chave
        a = a + 1
    return melhor

def resolver(matriz, oferta, historico):
    ciclo = detectar_ciclo(matriz)
    if ciclo is not None:
        return {"ciclo": ciclo, "liberadas": None, "bloqueadas": None, "grades_maximas": None}
    aprovadas = historico["aprovadas"]
    teto = historico["teto_ch"]
    liberadas, bloqueadas = classificar(matriz, oferta, aprovadas)
    grades = maior_grade(liberadas, oferta, matriz, teto)
    return {"ciclo": None, "liberadas": liberadas, "bloqueadas": bloqueadas, "grades_maximas": grades}

def main():
    if len(sys.argv) < 2:
        print("uso: main.py <diretorio_dados | arquivo_caso>", file=sys.stderr)
        sys.exit(1)
    matriz, oferta, historico = ler_entrada(sys.argv[1])
    saida = resolver(matriz, oferta, historico)
    print(json.dumps(saida, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()