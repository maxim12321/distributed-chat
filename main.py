from src.dht.chord_simulator import ChordSimulator


simulator = ChordSimulator(15)

for i in range(100):
    simulator.add_random_node()
    simulator.check_all_node_fingers()

simulator.print_nodes()

for i in range(1000):
    simulator.check_random_node()
