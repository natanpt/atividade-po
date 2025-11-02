# solver.py
# Script para resolver um exemplo do VRP com Coleta e Entrega (Pickup & Delivery) usando OR-Tools.
#
# Como rodar:
# 1) Instale as dependências: pip install -r requirements.txt
# 2) Execute: python solver.py data/data.json
#
# Observação: este script assume que o pacote `ortools` está instalado localmente.
import json
import sys

def create_data_model_from_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def solve(data):
    try:
        from ortools.constraint_solver import routing_enums_pb2
        from ortools.constraint_solver import pywrapcp
    except Exception as e:
        print('Erro: não foi possível importar or-tools. Certifique-se de instalar ortools (pip install ortools).')
        raise

    distance_matrix = data['distance_matrix']
    pickups_deliveries = data['pickups_deliveries']
    demands = data.get('demands', [0]*len(distance_matrix))
    vehicle_capacities = data.get('vehicle_capacities', [sum([abs(d) for d in demands])] * data['num_vehicles'])
    num_vehicles = data['num_vehicles']
    depot = data.get('depot', 0)

    manager = pywrapcp.RoutingIndexManager(len(distance_matrix), num_vehicles, depot)
    routing = pywrapcp.RoutingModel(manager)

    # Distance callback
    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return int(distance_matrix[from_node][to_node])

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Add capacity constraint.
    def demand_callback(from_index):
        from_node = manager.IndexToNode(from_index)
        return int(demands[from_node])

    demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0,  # null capacity slack
        vehicle_capacities,  # vehicle maximum capacities
        True,  # start cumul to zero
        'Capacity')

    # Add pickup and delivery constraints
    for pair in pickups_deliveries:
        pickup_index = manager.NodeToIndex(pair[0])
        delivery_index = manager.NodeToIndex(pair[1])
        routing.AddPickupAndDelivery(pickup_index, delivery_index)
        routing.solver().Add(routing.VehicleVar(pickup_index) == routing.VehicleVar(delivery_index))
        capacity_dim = routing.GetDimensionOrDie('Capacity')
        routing.solver().Add(capacity_dim.CumulVar(pickup_index) <= capacity_dim.CumulVar(delivery_index))


    # Setting first solution heuristic.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
    search_parameters.time_limit.FromSeconds(10)

    solution = routing.SolveWithParameters(search_parameters)

    if solution:
        total_distance = 0
        routes = []
        for vehicle_id in range(num_vehicles):
            index = routing.Start(vehicle_id)
            route = []
            route_loads = []
            while not routing.IsEnd(index):
                node_index = manager.IndexToNode(index)
                route.append(node_index)
                load = routing.GetDimensionOrDie('Capacity').CumulVar(index)
                route_loads.append(solution.Value(load))
                previous_index = index
                index = solution.Value(routing.NextVar(index))
            # append end node
            route.append(manager.IndexToNode(index))
            routes.append({'vehicle_id': vehicle_id, 'route': route, 'loads': route_loads})
        # compute total distance
        for r in routes:
            dist = 0
            for i in range(len(r['route']) - 1):
                dist += distance_matrix[r['route'][i]][r['route'][i+1]]
            total_distance += dist
        print('Total distance:', total_distance)
        for r in routes:
            print('Vehicle', r['vehicle_id'], 'route:', r['route'], 'loads (cumul at visits):', r['loads'])
        return routes
    else:
        print('Nenhuma solução encontrada.')
        return None

if __name__ == '__main__':
    if len(sys.argv) < 2:
        data_path = 'data/data.json'
    else:
        data_path = sys.argv[1]
    data = create_data_model_from_json(data_path)
    solve(data)
