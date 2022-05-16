from collections import deque

import SmartGrid_Query as query

graph = query.SmartGridGraph('LoadBalance.ttl')


def traverse_network(root_node):
    """
    BFS tree traversal of the network starting from the root node
    """
    q = deque([root_node])
    visited = set()
    while len(q) > 0:
        node = q.popleft()
        print(node)
        visited.add(node)
        neighbor_nodes = graph.query_network_neighbor_endpoints(node)
        for neighbor in neighbor_nodes:
            if neighbor not in visited and neighbor not in q:
                q.append(neighbor)

def traverse_grid(root_bus):
    """
    BFS Tree traversal of the power grid starting from the root bus
    """

    q = deque([root_bus])
    visited = set()
    while len(q) > 0:
        bus = q.popleft()
        print(bus)
        visited.add(bus)
        neighbor_buses = graph.query_neighbor_buses(bus)
        for neighbor in neighbor_buses:
            if neighbor not in visited and neighbor not in q:
                q.append(neighbor) 


# traverse_network('Endpoint_Controller')

# traverse_grid('Bus_SourceBus')

# power_path = graph.query_electrical_path('Load_611_3', 'Load_645_2')
# print(power_path)
# network_path = graph.query_network_path('Power_Meter_611_3', 'Power_Meter_645_2')
# print(network_path)
# # endpoints = graph.query_network_neighbor_endpoints('611')
# subcontrollers = graph.query_subcontrollers('Controller_Load_Balancer')
# for subcontroller in subcontrollers:
#     print(subcontroller)
graph.query_buses()
equipments = graph.query_double_buses('632','645')
for equipment in equipments:
    print(equipment)
# for endpoint in endpoints:
#     print(endpoint)
