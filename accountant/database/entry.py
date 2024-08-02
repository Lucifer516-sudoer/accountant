"""
This module contains data classes and enum related to entries and kinds of stuff.
"""

from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from uuid import uuid4

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
    Data class representing an entry model, now it is only for CSV file alone
    """

    id: str | None = Field(default_factory=lambda: str(uuid4()))
    date_time: datetime | None = Field(
        default_factory=lambda: str(
            datetime.now().strftime(format="%Y-%m-%dT%H:%M:%S")
        ),
    )
    name: str
    amount: Decimal = Field(default_factory=Decimal)
    reason: str
    tag: str | None = Field(default=None)
    flow_type: FlowType = Field(default=FlowType.CREDIT)
