from enum import StrEnum

from enum import Enum, auto

class AutoNameEnum(Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name

class ResearchType(AutoNameEnum):
    MEDICAL = auto()
    ACADEMIC = auto()
    KNOWLEDGE = auto()
    WEB = auto()