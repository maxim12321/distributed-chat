from dataclasses import dataclass


@dataclass
class InfoKey:
    data_type: int
    data_id: int

    def __hash__(self):
        return (self.data_type, self.data_id).__hash__()

    def __str__(self) -> str:
        return f"{self.data_type},{self.data_id}"

    @staticmethod
    def from_string(value: str) -> 'InfoKey':
        data_type, data_id = map(int, value.split(","))
        return InfoKey(data_type, data_id)
