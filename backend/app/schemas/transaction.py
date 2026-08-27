"""
Pydantic schemas for Transaction and Entity models.
"""

from decimal import Decimal
from datetime import datetime, timezone
from typing import List, Optional
import re
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


# Regular expression patterns for safety validation
RAW_PAN_PATTERN = re.compile(r"\b(?:\d[ -]*?){13,19}\b")
CARD_BIN_PATTERN = re.compile(r"^\d{6,8}$")
CARD_LAST4_PATTERN = re.compile(r"^\d{4}$")


class TransactionCreate(BaseModel):
    """
    Schema for ingesting a payment transaction.
    Enforces strict typing (Decimal amounts) and zero-trust payment tokenization.
    """
    transaction_id: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Unique external transaction reference ID.",
        examples=["txn_1001"],
    )
    customer_id: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Customer or account identifier.",
        examples=["cust_8921"],
    )
    amount: Decimal = Field(
        ...,
        gt=Decimal("0.00"),
        decimal_places=2,
        max_digits=18,
        description="Transaction monetary amount as a positive Decimal with 2 decimal places.",
        examples=[Decimal("149.99")],
    )
    currency: str = Field(
        default="USD",
        min_length=3,
        max_length=3,
        description="3-letter ISO currency code.",
        examples=["USD"],
    )
    status: str = Field(
        default="SUCCESS",
        max_length=30,
        description="Transaction execution status (e.g. SUCCESS, FAILED, PENDING).",
        examples=["SUCCESS"],
    )
    payment_method: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Payment method category (e.g. card, upi, bank_transfer).",
        examples=["card"],
    )

    # Safe instrument references (NEVER accept raw PAN or CVV)
    card_bin: Optional[str] = Field(
        default=None,
        description="First 6 to 8 digits of card for issuing bank correlation.",
        examples=["411111"],
    )
    card_last4: Optional[str] = Field(
        default=None,
        description="Last 4 digits of card for reference display.",
        examples=["1111"],
    )
    instrument_token: Optional[str] = Field(
        default=None,
        max_length=128,
        description="Safe one-way hash or token representing the payment instrument.",
        examples=["tok_card_fingerprint_8f1a"],
    )
    upi_vpa: Optional[str] = Field(
        default=None,
        max_length=128,
        description="Virtual Payment Address / UPI ID.",
        examples=["user@okhdfcbank"],
    )

    # Device & Network signals
    device_id: Optional[str] = Field(
        default=None,
        max_length=128,
        description="Unique device fingerprint token.",
        examples=["dev_fp_982b"],
    )
    ip_address: Optional[str] = Field(
        default=None,
        max_length=45,
        description="Client IPv4 or IPv6 address.",
        examples=["198.51.100.42"],
    )
    user_agent: Optional[str] = Field(
        default=None,
        max_length=512,
        description="Browser or client User-Agent string.",
    )
    location_city: Optional[str] = Field(
        default=None,
        max_length=100,
        description="City location of transaction origin.",
    )
    location_country: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Country code or name.",
        examples=["US"],
    )
    transacted_at: Optional[datetime] = Field(
        default=None,
        description="Timestamp when the transaction occurred in UTC. Defaults to current UTC time.",
    )

    @field_validator("currency")
    @classmethod
    def normalize_currency(cls, v: str) -> str:
        return v.strip().upper()

    @field_validator("card_bin")
    @classmethod
    def validate_card_bin(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            cleaned = v.strip()
            if not CARD_BIN_PATTERN.match(cleaned):
                raise ValueError("card_bin must be between 6 and 8 numeric digits.")
            return cleaned
        return v

    @field_validator("card_last4")
    @classmethod
    def validate_card_last4(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            cleaned = v.strip()
            if not CARD_LAST4_PATTERN.match(cleaned):
                raise ValueError("card_last4 must be exactly 4 numeric digits.")
            return cleaned
        return v

    @model_validator(mode="after")
    def reject_sensitive_credentials_or_pan(self) -> "TransactionCreate":
        """
        Zero-trust safety validator: ensures no raw card numbers, CVVs, or secret credentials are provided.
        """
        # Ensure default timestamp is set to UTC if missing
        if self.transacted_at is None:
            self.transacted_at = datetime.now(timezone.utc)
        elif self.transacted_at.tzinfo is None:
            self.transacted_at = self.transacted_at.replace(tzinfo=timezone.utc)

        # Scan text fields for accidental 13-19 digit PAN strings
        for field_name in ["instrument_token", "upi_vpa", "device_id", "user_agent"]:
            val = getattr(self, field_name, None)
            if val and RAW_PAN_PATTERN.search(str(val)):
                raise ValueError(
                    f"Forbidden sensitive data detected in {field_name}. Raw card numbers (PANs) are strictly prohibited."
                )

        return self


class EntityRead(BaseModel):
    """
    Output representation of a normalized graph Entity.
    """
    model_config = ConfigDict(from_attributes=True)

    id: int
    entity_type: str
    entity_value: str
    created_at: datetime


class TransactionEntityRead(BaseModel):
    """
    Output representation of a Transaction-to-Entity relationship link.
    """
    model_config = ConfigDict(from_attributes=True)

    relationship_type: str
    entity: EntityRead


class TransactionRead(BaseModel):
    """
    Output representation of a Transaction with its associated normalized entities.
    """
    model_config = ConfigDict(from_attributes=True)

    id: int
    transaction_id: str
    customer_id: str
    amount: Decimal
    currency: str
    status: str
    payment_method: str
    card_bin: Optional[str] = None
    card_last4: Optional[str] = None
    instrument_token: Optional[str] = None
    upi_vpa: Optional[str] = None
    device_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    location_city: Optional[str] = None
    location_country: Optional[str] = None
    transacted_at: datetime
    created_at: datetime
    updated_at: datetime
    entities: List[TransactionEntityRead] = Field(
        default=[],
        description="Associated graph entity relationships.",
    )


class TransactionListResponse(BaseModel):
    """
    Paginated list response for transactions.
    """
    items: List[TransactionRead]
    total: int
    page: int
    page_size: int


class TransactionBatchCreate(BaseModel):
    """
    Batch transaction ingestion payload.
    """
    transactions: List[TransactionCreate] = Field(
        ...,
        min_length=1,
        max_length=500,
        description="List of transactions to ingest atomically.",
    )


class TransactionBatchResponse(BaseModel):
    """
    Batch transaction ingestion response summary.
    """
    ingested_count: int
    items: List[TransactionRead]
