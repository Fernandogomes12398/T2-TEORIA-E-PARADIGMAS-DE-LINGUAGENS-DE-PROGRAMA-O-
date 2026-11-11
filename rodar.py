import subprocess, json, sys, os
base = os.path.dirname(os.path.abspath(__file__))
imper = os.path.join(base, "imperativa", "main.py")

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
    res = subprocess.run([sys.executable, imper, caminho], capture_output=True, text=True)
    if res.returncode != 0:
        print(f"  ERRO de execução:\n{res.stderr}")
        falhas += 1
        continue
    obtido = json.loads(res.stdout)
    if obtido == esperadas[nome]:
        print("  OK")
    else:
        print("  FALHOU")
        print("  Esperado:", json.dumps(esperadas[nome], sort_keys=True))
        print("  Obtido:  ", json.dumps(obtido, sort_keys=True))
        falhas += 1

print()
if falhas == 0:
    print("✅ Todos os 5 casos passaram.")
else:
    print(f"❌ {falhas} caso(s) falharam.")
    sys.exit(1)