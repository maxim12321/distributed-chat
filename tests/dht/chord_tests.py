import unittest

from src import constants
from src.replication.info_key import InfoKey
from tests.dht.chord_simulator import ChordSimulator


class ChordTests(unittest.TestCase):
    def setUp(self) -> None:
        self.simulator = ChordSimulator(10)

    def test_correct_joining(self) -> None:
        for _ in range(100):
            self.simulator.add_random_node()
            self.assertTrue(self.simulator.check_all_node_fingers())

            for _ in range(100):
                self.assertTrue(self.simulator.check_random_node())

    def test_correct_removing(self) -> None:
        for _ in range(100):
            self.simulator.add_random_node()

        for _ in range(100):
            self.assertTrue(self.simulator.check_node_successors())
            self.assertTrue(self.simulator.check_node_predecessors())
            for _ in range(100):
                self.assertTrue(self.simulator.check_random_node())

            self.simulator.remove_random_node()

    def test_data_appending(self) -> None:
        for _ in range(constants.REPLICATION_FACTOR):
            self.simulator.add_random_node()

        for _ in range(100):
            key = self.simulator.append_random_value()

            for _ in range(50):
                self.simulator.append_value(key, b'42')
                self.assertTrue(self.simulator.check_value(key))

    def test_data_updating(self) -> None:
        for _ in range(constants.REPLICATION_FACTOR):
            self.simulator.add_random_node()

        for _ in range(100):
            self.simulator.add_random_node()

            key = self.simulator.append_random_value()
            for _ in range(50):
                self.simulator.append_value(key, b'42')

            for _ in range(100):
                self.simulator.edit_random_value(key)
                self.assertTrue(self.simulator.check_value(key))

    def test_replication_pushing(self) -> None:
        for _ in range(10):
            self.simulator.add_random_node()

        for _ in range(1000):
            key = self.simulator.append_random_value()
            for _ in range(10):
                self.simulator.append_value(key, b'42')
                self.assertTrue(self.simulator.check_value(key))

        for _ in range(1000):
            self.assertTrue(self.simulator.check_random_value())

    def test_replication_joining(self) -> None:
        for _ in range(constants.REPLICATION_FACTOR):
            self.simulator.add_random_node()

        for _ in range(50):
            for _ in range(10):
                key = self.simulator.set_random_value()
                self.assertTrue(self.simulator.check_value(key))

            for _ in range(20):
                self.assertTrue(self.simulator.check_random_value())

            for _ in range(30):
                key = self.simulator.append_random_value()
                self.assertTrue(self.simulator.check_value(key))
                for _ in range(10):
                    self.assertTrue(self.simulator.check_value(key))
                    self.simulator.append_value(key, b'42')
                    self.assertTrue(self.simulator.check_value(key))

            for _ in range(20):
                self.assertTrue(self.simulator.check_random_value())

            self.simulator.add_random_node()

    def test_replication_joining_small(self) -> None:
        self.simulator.add_random_node()
        key = self.simulator.set_random_value()

        for i in range(1, constants.REPLICATION_FACTOR + 10):
            self.assertEqual(min(i, constants.REPLICATION_FACTOR), self.simulator.count_replicas(key))
            self.simulator.add_random_node()

    def test_replication_removing(self) -> None:
        keys = []
        for _ in range(100):
            self.simulator.add_random_node()
            keys.append(self.simulator.set_random_value())

        for _ in range(100):
            key = self.simulator.append_random_value()
            for _ in range(5):
                self.simulator.append_value(key, b'42')

        for _ in range(100 - constants.REPLICATION_FACTOR):
            for key in keys:
                self.assertTrue(self.simulator.check_value(key))

            self.simulator.remove_random_node()

    def test_replication_removing_small(self) -> None:
        for _ in range(constants.REPLICATION_FACTOR):
            self.simulator.add_random_node()

        key = self.simulator.set_random_value()

        for i in range(constants.REPLICATION_FACTOR, 0, -1):
            self.assertEqual(i, self.simulator.count_replicas(key))
            self.simulator.remove_random_node()
