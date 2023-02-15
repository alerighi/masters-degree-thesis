import re
import struct

TYPE_RE = re.compile(r"(.[1-9][0-9]*)(\[([0-9]+)])?")

TYPE_TO_STRUCT = {
    "u8": "B",
    "i8": "b",
    "u16": "H",
    "i16": "h",
    "u32": "L",
    "i32": "l",
}


def to_struct_fmt(data_type: str) -> str:
    data_type, _, length = TYPE_RE.match(data_type).groups()
    if length:
        # for simplicity only array of bytes (strings) are supported
        if data_type != "u8":
            raise RuntimeError("invalid type", data_type)

        return f"{length}s"

    return TYPE_TO_STRUCT[data_type]


def serialize(structure: dict, message: dict) -> bytes:
    """
    serialize message to binary with a given structure
    """

    fmt = "<"
    args = []
    for key, data_type in structure.items():
        fmt += to_struct_fmt(data_type)
        value = message[key]
        is_basic_type = data_type in TYPE_TO_STRUCT
        if is_basic_type and not isinstance(value, int) or not is_basic_type and not isinstance(value, bytes):
            raise RuntimeError("invaid type", key)
        args.append(value)

    return struct.pack(fmt, *args)


def deserialize(structure: dict, message: bytes) -> dict:
    """
    deserializes a message with a given structure to an object
    """

    fmt = "<"
    for data_type in structure.values():
        fmt += to_struct_fmt(data_type)

    parts = struct.unpack(fmt, message)
    result = {}
    for key, item in zip(structure.keys(), parts):
        result[key] = item

    return result


def sizeof(structure: dict) -> int:
    """
    gets the encoded size of a structure
    """

    fmt = "<"
    for data_type in structure.values():
        fmt += to_struct_fmt(data_type)

    return struct.calcsize(fmt)
