"""
Service layer for managing transaction ingestion, persistence, and normalized entity linking.
"""

from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.models.transaction import Transaction
from app.models.entity import Entity, EntityType
from app.models.transaction_entity import TransactionEntity, RelationshipType
from app.schemas.transaction import TransactionCreate, TransactionBatchCreate


class DuplicateTransactionError(Exception):
    """Raised when a transaction with the same transaction_id already exists."""
    pass


class TransactionService:
    @staticmethod
    async def _get_or_create_entity(
        db: AsyncSession,
        entity_type: str,
        entity_value: str,
    ) -> Entity:
        """
        Retrieve an existing entity or create a new normalized entity record.
        """
        stmt = select(Entity).where(
            Entity.entity_type == entity_type,
            Entity.entity_value == entity_value,
        )
        result = await db.execute(stmt)
        entity = result.scalars().first()

        if not entity:
            entity = Entity(
                entity_type=entity_type,
                entity_value=entity_value,
            )
            db.add(entity)
            await db.flush()

        return entity

    @classmethod
    async def ingest_transaction(
        cls,
        db: AsyncSession,
        transaction_in: TransactionCreate,
    ) -> Transaction:
        """
        Persist a transaction and link all normalized graph entities.
        """
        # Check for existing transaction_id
        stmt = select(Transaction).where(Transaction.transaction_id == transaction_in.transaction_id)
        existing = (await db.execute(stmt)).scalars().first()
        if existing:
            raise DuplicateTransactionError(
                f"Transaction with ID '{transaction_in.transaction_in}' already exists."
                if hasattr(transaction_in, "transaction_in")
                else f"Transaction with ID '{transaction_in.transaction_id}' already exists."
            )

        # Create Transaction instance
        tx = Transaction(
            transaction_id=transaction_in.transaction_id,
            customer_id=transaction_in.customer_id,
            amount=transaction_in.amount,
            currency=transaction_in.currency,
            status=transaction_in.status,
            payment_method=transaction_in.payment_method,
            card_bin=transaction_in.card_bin,
            card_last4=transaction_in.card_last4,
            instrument_token=transaction_in.instrument_token,
            upi_vpa=transaction_in.upi_vpa,
            device_id=transaction_in.device_id,
            ip_address=transaction_in.ip_address,
            user_agent=transaction_in.user_agent,
            location_city=transaction_in.location_city,
            location_country=transaction_in.location_country,
            transacted_at=transaction_in.transacted_at,
        )
        db.add(tx)
        await db.flush()

        # 1. Link USER Entity (Customer)
        user_entity = await cls._get_or_create_entity(
            db=db,
            entity_type=EntityType.USER,
            entity_value=transaction_in.customer_id,
        )
        tx_user_rel = TransactionEntity(
            transaction_id=tx.id,
            entity_id=user_entity.id,
            relationship_type=RelationshipType.ACCOUNT_HOLDER,
        )
        db.add(tx_user_rel)

        # 2. Link PAYMENT_INSTRUMENT Entity
        instrument_val = None
        if transaction_in.instrument_token:
            instrument_val = transaction_in.instrument_token
        elif transaction_in.upi_vpa:
            instrument_val = transaction_in.upi_vpa
        elif transaction_in.card_bin and transaction_in.card_last4:
            instrument_val = f"{transaction_in.card_bin}:{transaction_in.card_last4}"

        if instrument_val:
            instrument_entity = await cls._get_or_create_entity(
                db=db,
                entity_type=EntityType.PAYMENT_INSTRUMENT,
                entity_value=instrument_val,
            )
            tx_inst_rel = TransactionEntity(
                transaction_id=tx.id,
                entity_id=instrument_entity.id,
                relationship_type=RelationshipType.PAYMENT_SOURCE,
            )
            db.add(tx_inst_rel)

        # 3. Link DEVICE Entity
        if transaction_in.device_id:
            device_entity = await cls._get_or_create_entity(
                db=db,
                entity_type=EntityType.DEVICE,
                entity_value=transaction_in.device_id,
            )
            tx_dev_rel = TransactionEntity(
                transaction_id=tx.id,
                entity_id=device_entity.id,
                relationship_type=RelationshipType.DEVICE_ORIGIN,
            )
            db.add(tx_dev_rel)

        # 4. Link IP Entity
        if transaction_in.ip_address:
            ip_entity = await cls._get_or_create_entity(
                db=db,
                entity_type=EntityType.IP,
                entity_value=transaction_in.ip_address,
            )
            tx_ip_rel = TransactionEntity(
                transaction_id=tx.id,
                entity_id=ip_entity.id,
                relationship_type=RelationshipType.IP_ORIGIN,
            )
            db.add(tx_ip_rel)

        await db.flush()

        # Reload with entity relations
        return await cls.get_transaction_by_id(db=db, transaction_id=tx.transaction_id)  # type: ignore

    @classmethod
    async def ingest_transactions_batch(
        cls,
        db: AsyncSession,
        batch_in: TransactionBatchCreate,
    ) -> List[Transaction]:
        """
        Ingest a batch of transactions atomically.
        """
        ingested = []
        for tx_in in batch_in.transactions:
            tx = await cls.ingest_transaction(db=db, transaction_in=tx_in)
            ingested.append(tx)
        return ingested

    @classmethod
    async def get_transaction_by_id(
        cls,
        db: AsyncSession,
        transaction_id: str,
    ) -> Optional[Transaction]:
        """
        Retrieve a single transaction by its unique external transaction_id,
        including all associated normalized entities.
        """
        stmt = (
            select(Transaction)
            .options(
                selectinload(Transaction.entities).selectinload(TransactionEntity.entity)
            )
            .where(Transaction.transaction_id == transaction_id)
        )
        result = await db.execute(stmt)
        return result.scalars().first()

    @classmethod
    async def get_transactions(
        cls,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 50,
        customer_id: Optional[str] = None,
        status: Optional[str] = None,
        payment_method: Optional[str] = None,
    ) -> Tuple[List[Transaction], int]:
        """
        Retrieve a paginated list of transactions with optional filtering and total count.
        """
        # Base filter condition
        filters = []
        if customer_id:
            filters.append(Transaction.customer_id == customer_id)
        if status:
            filters.append(Transaction.status == status)
        if payment_method:
            filters.append(Transaction.payment_method == payment_method)

        # Count total
        count_stmt = select(func.count()).select_from(Transaction)
        if filters:
            count_stmt = count_stmt.where(*filters)
        total_count = (await db.execute(count_stmt)).scalar() or 0

        # Query paginated items
        stmt = (
            select(Transaction)
            .options(
                selectinload(Transaction.entities).selectinload(TransactionEntity.entity)
            )
            .order_by(Transaction.transacted_at.desc())
            .offset(skip)
            .limit(limit)
        )
        if filters:
            stmt = stmt.where(*filters)

        result = await db.execute(stmt)
        items = list(result.scalars().all())

        return items, total_count
