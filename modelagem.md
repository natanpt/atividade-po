## Conjuntos e parâmetros

- \(V = \{0,1,\dots,n\}\): conjunto de nós, onde \(0\) é o depósito.  
- \(P \subseteq V	imes V\): conjunto de pares \((p,d)\) onde \(p\) é nó de pickup (coleta) e \(d\) é nó de delivery (entrega).  
- \(K=\{1,\dots,m\}\): conjunto de veículos.

Parâmetros:

- \(c_{uv}\): custo (distância/tempo) de ir do nó \(u\) para o nó \(v\). (Matriz de distâncias \(\mathbf{C}\).)
- \(q_i\): demanda no nó \(i\). Convenção: \(q_p>0\) em nós de coleta, \(q_d=-q_p\) no nó de entrega correspondente; \(q_0=0\).
- \(Q_k\): capacidade do veículo \(k\).
- \(d_{max}\) (opcional): limite máximo de distância/tempo por veículo.
- \(t_i\) (opcional): tempo de serviço no nó \(i\).

---

## Variáveis de decisão

Usando a formulação inspirada no modelo de roteamento (OR-Tools):

- \(x_{uv}^k \in \{0,1\}\): 1 se o veículo \(k\) percorre o arco \(u	o v\). (No framework OR-Tools, estas variáveis são implícitas no RoutingModel.)
- \(pos_i^k\) (implícito via ordenação/índice) — ordem de visita do nó \(i\) pela rota do veículo \(k\). (No OR-Tools a precedência é tratada via índices e restrições de pickup/delivery.)
- \(l_i^k\) — carga cumulativa (cumulVar da dimensão 'Capacity') do veículo \(k\) ao sair do nó \(i\). No OR-Tools é representada pela dimensão `Capacity`.

---

## Modelagem matemática

**Função objetivo**  
Minimizar a distância total percorrida por todos os veículos:
\[
\min \sum_{k\in K}\sum_{u\in V}\sum_{v\in V} c_{uv}\, x_{uv}^k
\]

**Restrições principais**

1. **Cada nó (não-depósito) é visitado exatamente uma vez:**
\[
\sum_{k\in K}\sum_{u\in V} x_{ui}^k = 1,\qquad orall i\in V\setminus\{0\}
\]

2. **Fluxo (entrada = saída) para cada nó e veículo:**
\[
\sum_{v\in V} x_{iv}^k - \sum_{u\in V} x_{ui}^k = 0,\qquad orall i\in V,\;orall k\in K
\]

3. **Capacidade dos veículos (carga cumulativa):**
Para cada arco \(u	o v\) usado pelo veículo \(k\):
\[
l_v^k \ge l_u^k + q_v - M\,(1 - x_{uv}^k)
\]
e
\[
0 \le l_i^k \le Q_k,\qquad orall i\in V,\;orall k\in K
\]
(com \(M\) grande o suficiente — no OR-Tools isso é tratado naturalmente via `AddDimensionWithVehicleCapacity`).

4. **Precedência e pareamento pickup-delivery:**  
Para cada par \((p,d)\in P\):
- ambos \(p\) e \(d\) devem ser servidos pelo mesmo veículo;
- a coleta precede a entrega:
\[
	ext{vehicle}(p)=	ext{vehicle}(d)
\quad	ext{e}\quad pos_p < pos_d
\]
No OR-Tools: `RoutingModel.AddPickupAndDelivery(p_idx, d_idx)` e vinculamos `VehicleVar` e `CumulVar` quando necessário.

5. **Início e término no depósito:**
Cada veículo começa e termina no depósito:
\[
	ext{Start}_k = 0,\quad 	ext{End}_k = 0,\qquad orall k\in K
\]

6. **(Opcional) Limite de distância por veículo:**
Se aplicável, adicionar dimensão `Distance` com limite máximo por veículo:
\[
	ext{DistanceCumul}_i \le d_{max}^k
\]

---

## Comentários sobre a modelagem

- A formulação clássica (fluxo + pareamento) é NP-hard; para instâncias de médio/grande porte recorremos a algoritmos especializados (heurísticas, metaheurísticas) ou ao solver de roteamento do OR-Tools que combina CP e heurísticas.
- OR-Tools usa uma estrutura de índices (RoutingIndexManager + RoutingModel). Em vez de manipular explicitamente \(x_{uv}^k\), trabalha-se com índices de roteamento e `Dimensions` (cumulativas) para restrições como capacidade e tempo.
- Relaxações possíveis: relaxar integridade das decisões de rota não é trivial no contexto do RoutingModel; alternativas incluem formular como PL inteira (fluxo) e relaxar a integralidade, mas isso pode perder escalabilidade prática para VRP.
- Linearizações: para variar (time windows, penalidades), pode-se usar variáveis auxiliares; OR-Tools já oferece suporte direto a time windows e dimensões cumulativas.

---