import random
from src.dht.chord_simulator import ChordSimulator


simulator = ChordSimulator(10)

chord_size = 0

for i in range(100):
    simulator.add_random_node()
    chord_size += 1
    simulator.check_all_node_fingers()

simulator.print_nodes()

for i in range(1000):
    simulator.check_random_node()

for i in range(1000):
    key = simulator.set_random_value()
    print(f"Replicas = {simulator.count_replicas(key)}")
    simulator.check_value(key)

for i in range(10000):
    simulator.check_random_value()

for i in range(10):
    if chord_size <= 50:
        simulator.add_random_node()
        simulator.add_random_node()
        simulator.add_random_node()
        chord_size += 1
    elif chord_size >= 150:
        simulator.remove_random_node()
        simulator.remove_random_node()
        simulator.remove_random_node()
        chord_size -= 1
    else:
        if random.random() > 0.5:
            simulator.remove_random_node()
            chord_size -= 1
        else:
            simulator.add_random_node()
            chord_size += 1

    for j in range(10):
        simulator.check_random_node()

    for j in range(1000):
        key = simulator.set_random_value()
        simulator.check_value(key)

    for j in range(1000):
        simulator.check_random_value()

    for j in range(1000):
        key = simulator.append_random_value()
        simulator.check_value(key)

simulator.print_statistics()
