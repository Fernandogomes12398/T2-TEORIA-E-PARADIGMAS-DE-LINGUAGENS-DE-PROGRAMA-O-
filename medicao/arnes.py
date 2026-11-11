import subprocess, time, statistics, sys, os, json

N_FRIO = 20
N_QUENTE = 1000
WARMUP = 100

def medir_frio(comando, n=N_FRIO):
    tempos = []
    for _ in range(n):
        t0 = time.perf_counter()
        subprocess.run(comando, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        tempos.append((time.perf_counter() - t0) * 1000)
    return resumo(tempos)

def resumo(tempos):
    tempos_ord = sorted(tempos)
    n = len(tempos_ord)
    mediana = statistics.median(tempos_ord)
    minimo = tempos_ord[0]
    q1 = tempos_ord[n // 4]
    q3 = tempos_ord[(3 * n) // 4]
    return {"mediana_ms": round(mediana, 3), "min_ms": round(minimo, 3), "iqr_ms": round(q3 - q1, 3)}

def medir_quente(script, dados, n=N_QUENTE, warmup=WARMUP):
    sys.path.insert(0, os.path.dirname(script))
    import importlib.util
    spec = importlib.util.spec_from_file_location("alvo", script)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    matriz, oferta, historico = mod.ler_entrada(dados)
    for _ in range(warmup):
        mod.resolver(matriz, oferta, historico)
    tempos = []
    for _ in range(n):
        t0 = time.perf_counter()
        mod.resolver(matriz, oferta, historico)
        tempos.append((time.perf_counter() - t0) * 1000)
    return resumo(tempos)

if __name__ == "__main__":
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    imper = os.path.join(base, "imperativa", "main.py")

    print("== regime FRIO (caso 1, 20 repetições) ==")
    r = medir_frio([sys.executable, imper, os.path.join(base, "dados")])
    print(json.dumps(r, indent=2))

    print("== regime QUENTE (caso 1, 1000 iterações, warmup 100) ==")
    r = medir_quente(imper, os.path.join(base, "dados"))
    print(json.dumps(r, indent=2))