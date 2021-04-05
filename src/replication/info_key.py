from dataclasses import dataclass


@dataclass
class InfoKey:
    data_type: int
    data_id: int

    def __hash__(self):
        return (self.data_type, self.data_id).__hash__()
