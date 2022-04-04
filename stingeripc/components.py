from __future__ import annotations
from enum import Enum
from typing import Dict, List, Optional
from .topics import SignalTopicCreator, InterfaceTopicCreator

ALLOWED_ARG_TYPES = []

class InvalidStingerStructure(Exception): pass


class PayloadType(Enum):
    JSON_SCHEMA = 0
    ARG_LIST = 1


class ArgType(Enum):
    BOOLEAN = 0
    INTEGER = 1
    FLOAT = 2
    STRING = 3

    @classmethod
    def from_string(cls, arg_type: str) -> ArgType:
        if hasattr(cls, arg_type.upper()):
            return getattr(cls, arg_type.upper())
        else:
            raise InvalidStingerStructure(f"No ArgType called '{arg_type}'")


class Arg(object):
    
    def __init__(self, name: str, arg_type: ArgType, description: Optional[str]=None):
        self._name = name
        self._arg_type = arg_type
        self._description = description

    def set_description(self, description: str) -> Arg:
        self._description = description
        return self

    @property
    def name(self) -> str:
        return self._name
    
    @property
    def type(self) -> PayloadType:
        return self._arg_type

    @property
    def description(self) -> Optional[str]:
        return self._description

    @classmethod
    def new_from_stinger(cls, name: str, stinger: Dict[str, str]) -> Arg:
        if 'type' not in stinger:
            raise InvalidStingerStructure("No 'type' in arg structure")
        arg = cls(name, ArgType.from_string(stinger['type']))
        if 'description' in stinger and isinstance(stinger['description'], str):
            arg.set_description(stinger['description'])
        return arg


class Schema(object):
    """ Eventually this will do more than simply be a dumb object.
    It will probably do some parsing of the schema to make it more
    accessible/powerful.
    """

    def __init__(self, schema):
        self._schema = schema


class Signal(object):

    def __init__(self, topic_creator: SignalTopicCreator, name: str):
        self._topic_creator = topic_creator
        self._name = name
        self._payload_type = PayloadType.ARG_LIST
        self._schema = None # type: Optional[Schema]
        self._arg_list = [] # type: List[Arg]
    
    def set_schema(self, schema: Schema) -> Signal:
        self._schema = schema
        self._payload_type = PayloadType.JSON_SCHEMA
        return self
    
    def set_arg_list(self, arg_list: List[Arg]) -> Signal:
        self._arg_list = arg_list
        self._payload_type = PayloadType.ARG_LIST
        return self

    @property
    def arg_list(self):
        return self._arg_list

    @property
    def name(self):
        return self._name

    @property
    def emit_topic(self):
        return self._topic_creator.signal_topic(self.name)

    @classmethod
    def new_from_stinger(cls, topic_creator: SignalTopicCreator, name: str, spec: Dict[str, str]) -> "Signal":
        """ Alternative constructor from a Stinger signal structure.
        """
        signal = cls(topic_creator, name)
        if (('args' in spec and 1 or 0) + ('schema' in spec and 1 or 0)) != 1:
            raise InvalidStingerStructure("Signal specification must have 'args' xor 'schema'")
        if 'args' in spec:
            arg_list = []
            for k, v in spec['args'].items():
                new_arg = Arg.new_from_stinger(name=k, stinger=v)
                arg_list.append(new_arg)
            return signal.set_arg_list(arg_list)
        if 'schema' in spec:
            return signal.set_schema(spec['schema'])


class StingerSpec:

    def __name__(self, topic_creator: InterfaceTopicCreator, interface):
        self._topic_creator = topic_creator
        try:
            self._name = interface['name']
            self._version = interface['version']
        except KeyError as e:
            raise InvalidStingerStructure(f"Missing interface property: {e}")
        except TypeError:
            raise InvalidStingerStructure(f"Interface didn't appear to have a correct type")
        self.signals = {}

    def add_signal(self, signal: Signal):
        self.signals[signal.name] = signal

    @classmethod
    def new_from_stinger(cls, topic_creator, stinger: Dict) -> StingerSpec:
        if 'stingeripc' not in stinger:
            raise InvalidStingerStructure("Missing 'stingeripc' format version")
        if stinger['stingeripc'] not in ["0.0.2"]:
            raise InvalidStingerStructure(f"Unsupported stinger format version: {stinger['stingeripc']}")
        stinger_spec = StingerSpec(stinger['interface'])

        try:
            if 'signals' in stinger:
                for signal_name, signal_spec in stinger['signals'].items():
                    signal = Signal.new_from_stinger(self._topic_creator.signal_topic_creator(), signal_name, signal_spec)
                    stinger_spec.add_signal(signal)
        except TypeError as e:
            raise InvalidStingerStructure(f"Signal specification appears to be invalid: {e}")

        return stinger_spec
