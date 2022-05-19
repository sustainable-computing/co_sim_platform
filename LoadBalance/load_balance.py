from collections import deque
import sys
import git 

# Setup path to search for custom modules at the git root level
repo = git.Repo('.', search_parent_directories=True)
repo_root_path = repo.working_tree_dir
sys.path.insert(1, repo_root_path)

from SmartGridOntology import SmartGrid_Query as query


graph = query.SmartGridGraph('../SmartGridOntology/models/LoadBalance.ttl')


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

# for endpoint in endpoints:
#     print(endpoint)

# controllers = graph.query_controllers_from_sensor('Power_Meter_611_3')
# for controller in controllers:
#     print(controller)

# print('\n\n')
# controllers =  graph.query_controllers_from_actuators('Flow_Switch_645')
# for controller in controllers:
#     print(controller)

graph.query_interfaces('Flow_Switch_645')