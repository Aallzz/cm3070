"""
Representation of tick data
"""
from dataclasses import dataclass, fields
from typing import Optional, Literal

TickType = Literal["bid", "ask", "trade"]
UpdateType = Literal["new", "update", "delete", "sell", "buy"]

# Mapping for converting tick_type and update_type to integer values
tick_type_to_int = {"bid": 0, "ask": 1, "trade": 2}
update_type_to_int = {"new": 0, "update": 1, "delete": 2, "sell": 3, "buy": 4}


@dataclass
class TickRecord:
    """
    Representation of a tick record
    """
    receive_timestamp: int  # Unix timestamp in milliseconds
    exchange_timestamp: Optional[int]  # Unix timestamp in milliseconds
    tick_type: TickType
    update_type: UpdateType
    price: float  # Prxxice unit needs to be understood
    size: float

    def get_value(self, field_name, value):
        """
        Convert specific field values based on field name.
        """
        if field_name == 'tick_type':
            return tick_type_to_int.get(value, "")
        elif field_name == 'update_type':
            return update_type_to_int.get(value, "")
        return value if value is not None else ""

    def to_csv_line(self) -> str:
        """
        Convert the record to a string for CSV output, applying conversions for specific fields.
        """
        return ','.join(
            str(self.get_value(field.name, getattr(self, field.name)))
            for field in fields(self)
        )

    @classmethod
    def csv_header(cls) -> str:
        """
        Return the header of the CSV file, dynamically generated from the dataclass fields
        """
        return ','.join(field.name for field in fields(cls))
