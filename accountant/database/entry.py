"""
This module contains data classes and enum related to entries and kinds of stuff.
"""

from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, Field


class FlowType(StrEnum):
    """
    Enum representing Cash Flow Type
    """

    CREDIT = "credit"
    DEBIT = "debit"
    SAVINGS = "savings"


class Entry(BaseModel):
    """
    Data class representing an entry
    """

    date_time: str | None = Field(default_factory=lambda: str(datetime.now()))
    name: str
    amount: Decimal = Field(json_schema_extra={})
    reason: str
    tag: str | None = Field(default=None)
    flow_type: FlowType = Field(default=FlowType.CREDIT)
