import com.google.gson.GsonBuilder
import java.io.File

// =====================================================================
// MODELO DE DOMÍNIO (Diga, não pergunte)
// =====================================================================

data class Disciplina(
    val codigo: String,
    val nome: String,
    val ch: Int,
    val prerequisitos: List<String>
) {
    fun prerequisitosFaltantes(aprovadas: Set<String>): List<String> {
        return prerequisitos.filter { it !in aprovadas }.sorted()
    }

    fun estaLiberada(aprovadas: Set<String>): Boolean {
        return prerequisitosFaltantes(aprovadas).isEmpty()
    }
}

data class OfertaItem(
    val codigo: String,
    val horarios: Set<String>
)

data class Historico(
    val aprovadas: Set<String>,
    val teto_ch: Int
)

data class DisciplinaOfertada(
    val disciplina: Disciplina,
    val horarios: Set<String>
) {
    val codigo get() = disciplina.codigo
    val cargaHoraria get() = disciplina.ch

    fun conflitaCom(outra: DisciplinaOfertada): Boolean {
        return horarios.any { it in outra.horarios }
    }
}

// =====================================================================
// POLIMORFISMO (Interface Restricao)
// =====================================================================

interface Restricao {
    fun permite(disciplina: DisciplinaOfertada, gradeAtual: List<DisciplinaOfertada>): Boolean
}

class TetoDeCargaHoraria(private val teto: Int) : Restricao {
    override fun permite(disciplina: DisciplinaOfertada, gradeAtual: List<DisciplinaOfertada>): Boolean {
        val cargaAtual = gradeAtual.sumOf { it.cargaHoraria }
        return cargaAtual + disciplina.cargaHoraria <= teto
    }
}

class ConflitoDeHorario : Restricao {
    override fun permite(disciplina: DisciplinaOfertada, gradeAtual: List<DisciplinaOfertada>): Boolean {
        return gradeAtual.none { disciplina.conflitaCom(it) }
    }
}

// =====================================================================
// SERVIÇOS DE DOMÍNIO
// =====================================================================

class MatrizCurricular(private val disciplinas: Map<String, Disciplina>) {
    fun obter(codigo: String): Disciplina? = disciplinas[codigo]

    fun encontrarCiclo(): List<String>? {
        val caminho = mutableListOf<String>()
        val visitados = mutableSetOf<String>()

        fun dfs(codigo: String): List<String>? {
            if (codigo in caminho) {
                val idx = caminho.indexOf(codigo)
                return caminho.subList(idx, caminho.size) + codigo
            }
            if (codigo in visitados) return null

            visitados.add(codigo)
            caminho.add(codigo)

            val disc = obter(codigo)
            if (disc != null) {
                for (prereq in disc.prerequisitos) {
                    val res = dfs(prereq)
                    if (res != null) return res
                }
            }

            caminho.removeAt(caminho.size - 1)
            return null
        }

        for (codigo in disciplinas.keys) {
            val res = dfs(codigo)
            if (res != null) return res
        }
        return null
    }
}

class GerenciadorDeMatricula(
    private val matriz: MatrizCurricular,
    private val oferta: List<DisciplinaOfertada>,
    private val aprovadas: Set<String>,
    private val restricoes: List<Restricao>
) {
    private val liberadas = mutableListOf<DisciplinaOfertada>()
    private val bloqueadas = mutableListOf<Map<String, Any>>()

    fun processar(): Map<String, Any?> {
        val ciclo = matriz.encontrarCiclo()
        
        // Se houver ciclo, retorna as 4 chaves (as outras 3 com null)
        if (ciclo != null) {
            return mapOf(
                "ciclo" to ciclo,
                "liberadas" to null,
                "bloqueadas" to null,
                "grades_maximas" to null
            )
        }

        for (disc in oferta) {
            if (disc.codigo in aprovadas) continue

            if (disc.disciplina.estaLiberada(aprovadas)) {
                liberadas.add(disc)
            } else {
                val faltam = disc.disciplina.prerequisitosFaltantes(aprovadas)
                bloqueadas.add(mapOf("codigo" to disc.codigo, "faltam" to faltam))
            }
        }

        liberadas.sortBy { it.codigo }
        bloqueadas.sortBy { it["codigo"] as String }

        val grades = buscarGradesMaximas()

        // Retorna as 4 chaves (ciclo é null)
        return mapOf(
            "ciclo" to null,
            "liberadas" to liberadas.map { it.codigo },
            "bloqueadas" to bloqueadas,
            "grades_maximas" to grades.map { grade -> grade.map { it.codigo } }.sortedBy { it.joinToString("") }
        )
    }

    private fun buscarGradesMaximas(): List<List<DisciplinaOfertada>> {
        var melhores = mutableListOf<List<DisciplinaOfertada>>()
        var melhorTam = 0

        fun backtracking(idx: Int, gradeAtual: MutableList<DisciplinaOfertada>) {
            if (gradeAtual.size + (liberadas.size - idx) < melhorTam) return

            if (idx == liberadas.size) {
                val tam = gradeAtual.size
                if (tam > melhorTam) {
                    melhorTam = tam
                    melhores = mutableListOf(gradeAtual.toList())
                } else if (tam == melhorTam && tam > 0) {
                    melhores.add(gradeAtual.toList())
                }
                return
            }

            val disc = liberadas[idx]
            
            // POLIMORFISMO: a busca não sabe qual restrição é, só pergunta se permite
            val permitido = restricoes.all { it.permite(disc, gradeAtual) }

            if (permitido) {
                gradeAtual.add(disc)
                backtracking(idx + 1, gradeAtual)
                gradeAtual.removeAt(gradeAtual.size - 1)
            }

            backtracking(idx + 1, gradeAtual)
        }

        backtracking(0, mutableListOf())

        return if (melhores.isEmpty()) listOf(emptyList()) else melhores
    }
}

// =====================================================================
// CASCA IMPURA (I/O com Gson configurado para não ignorar null)
// =====================================================================

class DadosMatriz(val disciplinas: List<Disciplina>)
class DadosOferta(val disciplinas: List<OfertaItem>)
class DadosCaso(val matriz: DadosMatriz, val oferta: DadosOferta, val historico: Historico)

fun main(args: Array<String>) {
    if (args.isEmpty()) {
        System.err.println("Uso: java -jar oo.jar <diretorio_dados | arquivo_caso>")
        return
    }

    // AQUI ESTÁ A CORREÇÃO: serializeNulls() força a imprimir "ciclo": null
    val gson = GsonBuilder().serializeNulls().create()
    val alvo = File(args[0])

    val matrizJson: DadosMatriz
    val ofertaJson: DadosOferta
    val histJson: Historico

    if (alvo.isDirectory) {
        matrizJson = gson.fromJson(File(alvo, "matriz.json").readText(), DadosMatriz::class.java)
        ofertaJson = gson.fromJson(File(alvo, "oferta.json").readText(), DadosOferta::class.java)
        histJson = gson.fromJson(File(alvo, "historico.json").readText(), Historico::class.java)
    } else {
        val dados = gson.fromJson(alvo.readText(), DadosCaso::class.java)
        matrizJson = dados.matriz
        ofertaJson = dados.oferta
        histJson = dados.historico
    }

    val mapaDisciplinas = matrizJson.disciplinas.associateBy { it.codigo }
    val matriz = MatrizCurricular(mapaDisciplinas)

    val ofertadas = ofertaJson.disciplinas.mapNotNull { item ->
        mapaDisciplinas[item.codigo]?.let { base ->
            DisciplinaOfertada(base, item.horarios)
        }
    }

    val restricoes = listOf(
        TetoDeCargaHoraria(histJson.teto_ch),
        ConflitoDeHorario()
    )

    val gerenciador = GerenciadorDeMatricula(matriz, ofertadas, histJson.aprovadas, restricoes)
    val resultado = gerenciador.processar()

    println(gson.toJson(resultado))
}