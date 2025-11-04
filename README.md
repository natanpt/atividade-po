# Problema de Roteirização com Coleta e Entrega (Pickup & Delivery — PDVRP)

**Grupo:** Aguisson Alves, Natan Pedrosa, José Luciano e João Pedro

**Resumo:**  
Este projeto modela e resolve um problema de roteirização de veículos com pares de coleta e entrega (pickup & delivery). O objetivo é atribuir e ordenar visitas a nós (coletas e entregas) por uma frota de veículos com capacidades limitadas, minimizando a distância total percorrida e respeitando precedência (coleta antes da entrega) e restrições de capacidade.

**Tipo:**  
Problema de otimização combinatória — Programação inteira mista / Problema de roteirização com restrições (PDVRP). A solução é construída com abordagem de Routing (Constraint Programming / OR-Tools), que trata variáveis discretas de roteamento e dimensões (cumulativas) para capacidades.

---

## Contexto / enunciado
Dada uma rede de nós (um depósito e vários clientes que são, alternativamente, pontos de coleta ou de entrega) e uma frota de veículos com capacidades limitadas, planejar rotas que:

- comecem e terminem no depósito;
- atendam todos os nós;
- respeitem que cada par (coleta, entrega) seja visitado pelo mesmo veículo e que a coleta ocorra antes da entrega;
- nunca excedam a capacidade do veículo ao longo da rota;
- minimizem o custo total (por exemplo, distância ou tempo).

Aplicações típicas: logística reversa (coleta de devoluções), transporte de mercadorias que exigem picking e posterior entrega, serviços simultâneos de coleta e entrega por um mesmo veículo.

---
## Dados de entrada

Formato do arquivo: `data/data.json` (JSON). Chaves esperadas:

- `"distance_matrix"`: matriz NxN (lista de listas) com custos \(c_{uv}\).
- `"pickups_deliveries"`: lista de pares `[pickup_node, delivery_node]` (nós referenciados por índices 0..N-1).
- `"demands"`: lista de inteiros (tamanho N), demandas positivas em pickups e negativas nas entregas correspondentes.
- `"num_vehicles"`: número de veículos (inteiro).
- `"depot"`: índice do depósito (normalmente 0).
- `"vehicle_capacities"`: lista com a capacidade de cada veículo.

**Exemplo (trecho do `data/data.json` de teste):**
```json
{
  "distance_matrix": [
    [0, 9, 9, 9, 9, 14, 14, 14, 14],
    [9, 0, 2, 4, 6, 10, 10, 10, 10],
    [9, 2, 0, 8, 2, 9, 9, 9, 9],
    [9, 4, 8, 0, 6, 8, 8, 8, 8],
    [9, 6, 2, 6, 0, 7, 7, 7, 7],
    [14,10,9,8,7,0,2,4,6],
    [14,10,9,8,7,2,0,8,4],
    [14,10,9,8,7,4,8,0,2],
    [14,10,9,8,7,6,4,2,0]
  ],
  "pickups_deliveries": [
    [1, 5],
    [2, 6],
    [3, 7],
    [4, 8]
  ],
  "demands": [0,1,1,1,1,-1,-1,-1,-1],
  "num_vehicles": 2,
  "depot": 0,
  "vehicle_capacities": [2,2]
}
```

---

## Solver escolhido e justificativa

**OR-Tools (Routing + CP-SAT components)** — justifica-se por:

- Implementações específicas para VRP/PDVRP (RoutingModel, AddPickupAndDelivery, Dimensions).
- Suporte a restrições comuns (capacidades, time windows, precedência) e heurísticas eficientes (PATH_CHEAPEST_ARC, GUIDED_LOCAL_SEARCH, etc.).
- Boa escalabilidade prática para instâncias reais e facilidade de integração com Python.

> Alternativas: modelar como PL/inteira com PuLP/Pyomo e resolver com CBC/Gurobi para pequenas/medianas instâncias; porém para VRP com precedências o OR-Tools costuma ser mais direto e eficiente.

---

## Estratégia de implementação

Arquivos principais:

- `solver.py` — script que:
  - carrega `data/data.json`;
  - cria `RoutingIndexManager` e `RoutingModel`;
  - registra callbacks (distância, demanda);
  - adiciona dimensões (Capacity) via `AddDimensionWithVehicleCapacity`;
  - adiciona pares `AddPickupAndDelivery` e restrições auxiliares;
  - configura `search_parameters` (first_solution_strategy, time_limit);
  - resolve e imprime rotas e cargas cumulativas.
- `notebooks/solucao.ipynb` — notebook mínimo para reproduzir execução e visualizar dados/saída.
- `data/` — arquivos JSON de instância.

Verificações / testes:
- Testar integridade do JSON (dimensões corretas da matriz).
- Garantir `len(demands) == N` e que `pickups_deliveries` referenciam índices válidos.
- Testes em instâncias pequenas (sanity checks) antes de escalar.

---

## Como executar (comandos)

1. Criar/ativar virtualenv (recomendado):
```bash
python -m venv .venv
source .venv/bin/activate   # Linux/Mac
.venv\Scripts\ctivate      # Windows
```

2. Instalar dependências:
```bash
pip install -r requirements.txt
# requirements.txt contém: ortools>=9.0
```

3. Executar solver com a instância padrão:
```bash
python solver.py data/data.json
```

4. (Opcional) Executar notebook:
```bash
jupyter notebook notebooks/solucao.ipynb
```

5. Link do Binder - [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/natanpt/atividade_po/HEAD?urlpath=%2Fdoc%2Ftree%2F%2Fnotebooks%2Fsolucao.ipynb)
---

## Resultados esperados e discussão

- Saída textual com as rotas para cada veículo, carga cumulativa nas visitas e distância total mínima encontrada.
- Para instâncias pequenas, o solver deve encontrar solução ótima ou uma heurística de qualidade em poucos segundos. Para instâncias maiores, ajustar `search_parameters` (estratégias de busca e time_limit) para equilibrar tempo/qualidade.
- Sensibilidades importantes:
  - reduzir capacidade dos veículos pode aumentar a necessidade de mais veículos e aumentar custo total;
  - custos assimétricos na matriz podem alterar alocação de pares a veículos diferentes;
  - adicionar time windows frequentemente torna o problema mais restritivo e pode aumentar tempo de solução.

Métricas a reportar:
- Distância total;
- Número de veículos utilizados (algumas vezes menos que `num_vehicles` disponível);
- Carga máxima observada por veículo;
- Tempo de execução.

---

## Comentários finais e extensões possíveis

- Adicionar **time windows** (`time` dimension) para cada nó.
- Tornar `distance_matrix` derivada de coordenadas Euclidianas (gerador de instâncias).
- Implementar visualização (mapa/plot) das rotas no notebook usando `matplotlib`.
- Produzir CSV/JSON estruturado com as rotas para integração com outros sistemas.

---

## Referências / bibliografia

- OR-Tools — *https://developers.google.com/optimization/routing/pickup_delivery?hl=pt-br*
- Código referência - *https://github.com/google/or-tools/blob/stable/ortools/constraint_solver/samples/vrp_pickup_delivery.py*