import subprocess, json, sys, os

base = os.path.dirname(os.path.abspath(__file__))

# Define as duas implementações
implementacoes = [
    ("imperativa", [sys.executable, os.path.join(base, "imperativa", "main.py")]),
    ("funcional",  [sys.executable, os.path.join(base, "funcional",  "main.py")]),
]

casos = {
    "caso1": "dados",
    "caso2": "dados/caso2_ciclo.json",
    "caso3": "dados/caso3_historico_vazio.json",
    "caso4": "dados/caso4_historico_completo.json",
    "caso5": "dados/caso5_teto_reduzido.json"
}

with open(os.path.join(base, "saidas_esperadas.json")) as f:
    esperadas = json.load(f)

falhas = 0

for nome, alvo in casos.items():
    print(f"== {nome} ==")
    caminho = os.path.join(base, alvo)
    saidas = {}
    
    for impl_nome, cmd in implementacoes:
        res = subprocess.run(cmd + [caminho], capture_output=True, text=True)
        
        if res.returncode != 0:
            print(f"  [{impl_nome}] ERRO de execução:\n{res.stderr}")
            falhas += 1
            saidas[impl_nome] = None
            continue
            
        try:
            saidas[impl_nome] = json.loads(res.stdout)
        except json.JSONDecodeError:
            print(f"  [{impl_nome}] ERRO: saída não é JSON válido.")
            falhas += 1
            saidas[impl_nome] = None

    # Compara cada uma com o gabarito
    for impl_nome, obtido in saidas.items():
        if obtido is None:
            continue
        if obtido == esperadas[nome]:
            print(f"  [{impl_nome}] OK")
        else:
            print(f"  [{impl_nome}] FALHOU (divergiu do gabarito)")
            print(f"    Esperado: {json.dumps(esperadas[nome], sort_keys=True)}")
            print(f"    Obtido:   {json.dumps(obtido, sort_keys=True)}")
            falhas += 1

    # Compara as duas entre si (garante que são idênticas)
    if all(s is not None for s in saidas.values()):
        vals = list(saidas.values())
        if all(v == vals[0] for v in vals):
            print("  [equivalência] OK")
        else:
            print("  [equivalência] DIVERGEM (as implementações deram respostas diferentes)")
            falhas += 1

print()
if falhas == 0:
    print("✅ Todos os 5 casos passaram em TODAS as implementações e são equivalentes.")
else:
    print(f"❌ {falhas} falha(s) encontradas.")
    sys.exit(1)