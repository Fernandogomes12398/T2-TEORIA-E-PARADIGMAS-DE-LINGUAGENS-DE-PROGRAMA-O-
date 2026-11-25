# Análise Comparativa — Rosetta de Paradigmas

Este documento analisa a resolução do mesmo problema (matrícula acadêmica) sob três paradigmas diferentes: Imperativo (Python), Funcional (Python) e Orientado a Objetos (Kotlin). 

## 1. Legibilidade

Para medir a legibilidade, contamos apenas as linhas que efetivamente respondem às quatro perguntas (ignorando leitura de arquivo, declarações de tipo e formatação de saída).

- **Imperativa (Python):** Foi a mais verbosa. Como o paradigma exige a construção manual de laços e o controle explícito do estado (ex: a função de ordenação manual, já que `sorted` não era permitido), o código fica denso. Entender a maior grade (pergunta 4) exigiu aninhar funções de retrocesso (`backtracking`) com manipulação de listas mutáveis, o que torna o fluxo de leitura mais difícil.
- **Funcional (Python):** A legibilidade é mista. As perguntas 2 e 3 (filtrar liberadas e bloqueadas) ficam extremamente elegantes e legíveis em uma ou duas linhas com `tuple` e compreensões. No entanto, a pergunta 1 (detecção de ciclo com caminho) e a pergunta 4 (busca) sofrem porque a recursão pura exige passar muitos parâmetros adiante, o que "polui" a assinatura das funções.
- **OO (Kotlin):** A legibilidade foi a melhor. As classes de domínio (`Disciplina`, `DisciplinaOfertada`) encapsulam a lógica ("Diga, não pergunte"). A interface `Restricao` permite que a busca principal não precise saber se está validando choque de horário ou teto de carga horária — isso é feito magicamente pelo despacho dinâmico. O código é autoexplicativo.

## 2. Expressividade

- **Onde a linguagem ajudou:** O Python funcional brilhou na transformação de coleções. O Kotlin brilhou na modelagem do domínio e na segurança de tipos, especialmente ao definir que uma `DisciplinaOfertada` sempre tem horários. 
- **Onde a linguagem atrapalhou:** O Python Imperativo sofreu com a proibição de funções nativas (escrever a ordenação à mão tomou tempo). Já o Kotlin Imperativo (leitura de JSON) exigiu a configuração de uma biblioteca externa (Gson) apenas para fazer o "encanamento" de entrada, o que é um overhead que o Python não tem.
- **A abstração da restrição:** O ponto mais expressivo da versão OO foi abstrair as regras. Em vez de `if carga_horaria <= teto`, a busca pergunta `restricao.permite(...)`. A versão Imperativa e Funcional exigem que a lógica de conflito e teto seja "hardcoded" dentro da função de busca.

## 3. Desempenho e Método

**Armadilhas de Medição:** A primeira execução de qualquer código é atípica (cache frio). No caso do Kotlin (JVM), o *Just-In-Time (JIT) compiler* aquece dentro do processo, o que faz com que execuções subsequentes sejam muito mais rápidas.

*(Nota: os tempos abaixo são estimativas observacionais. O experimento honesto seria escrever as três versões na mesma linguagem).*

- **Tempo Frio (Startup):** O Kotlin (JVM) tem um tempo de inicialização (startup) muito maior. O Python interpretado é mais rápido para "acordar".
- **Tempo Quente (Regime):** Em execuções repetidas no mesmo processo, o Kotlin se iguala ou supera o Python em velocidade bruta, pois a JVM otimiza os bytecodes em tempo de execução.
- **Complexidade Algorítmica:** A maior diferença não é de paradigma, mas de restrição. A pergunta 4 (maior grade) é intratável (exponencial no número de disciplinas liberadas). Por isso, as três versões implementam poda (se a grade atual + disciplinas restantes não alcançar o recorde, o ramo é cortado). Sem a poda, as três versões travariam em matrizes maiores.

## 4. Conclusão: Qual paradigma foi mais adequado?

Nenhum paradigma ganha nas quatro perguntas, mas o **Orientado a Objetos** foi o mais adequado para este problema específico. 

O problema possui regras de negócio claras (pré-requisitos, carga horária, choque de horários). Modelar isso como objetos que sabem decidir sobre si mesmos (ex: `disciplina.estaLiberada()`) e usar polimorfismo para as restrições de busca tornou o código extensível e fácil de ler. 

Se a pergunta 4 (maior grade) fosse o único requisito, o **Funcional** venceria, pois a busca com listas imutáveis é conceitualmente muito mais segura (não há risco de esquecer de "desfazer" uma mutação no `backtracking`). 

O **Imperativo** foi o mais difícil de escrever, muito por conta das restrições do edital (proibição de funções nativas), o que provou que a verbosidade do paradigma é real, mas também que ele é o mais próximo do funcionamento do hardware (o que explica sua popularidade).

---
*Nota de transparência sobre o uso de IA: A versão OO foi originalmente implementada em Python, mas a pedido do integrante e para demonstrar domínio de linguagens estaticamente tipadas sugeridas pelo professor, foi refatorada para Kotlin usando a biblioteca Gson para leitura de dados.*