import unittest

from src import constants
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
            for _ in range(100):
                self.assertTrue(self.simulator.check_random_node())

            self.simulator.remove_random_node()

    def test_replication_joining(self) -> None:
        for _ in range(constants.REPLICATION_FACTOR):
            self.simulator.add_random_node()

        for _ in range(100):
            for _ in range(100):
                key = self.simulator.set_random_value()
                self.assertTrue(self.simulator.check_value(key))

            for _ in range(100):
                self.assertTrue(self.simulator.check_random_value())

            for _ in range(100):
                key = self.simulator.append_random_value()
                self.assertTrue((self.simulator.check_value(key)))

            for _ in range(100):
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
            self.simulator.append_random_value()

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
