from enum import Enum
from .exceptions import InvalidStingerStructure

class ArgType(Enum):
    UNKNOWN = 0
    VALUE = 1
    ENUM = 2
    JSON_SCHEMA = 3


class ArgValueType(Enum):
    BOOLEAN = 0
    INTEGER = 1
    FLOAT = 2
    STRING = 3

    @classmethod
    def from_string(cls, arg_type: str) -> ArgValueType:
        if hasattr(cls, arg_type.upper()):
            return getattr(cls, arg_type.upper())
        else:
            raise InvalidStingerStructure(f"No ArgType called '{arg_type}'")

    @classmethod
    def to_python_type(cls, arg_type: ArgValueType) -> str:
        if arg_type == cls.BOOLEAN:
            return "bool"
        elif arg_type == cls.INTEGER:
            return "int"
        elif arg_type == cls.FLOAT:
            return "float"
        elif arg_type == cls.STRING:
            return "str"
        raise InvalidStingerStructure("Unhandled arg type")

    @classmethod
    def to_json_type(cls, arg_type: ArgValueType) -> str:
        pass