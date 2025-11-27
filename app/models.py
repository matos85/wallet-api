from sqlalchemy import Column, Integer, UUID
from sqlalchemy.orm import declarative_base
import uuid

Base = declarative_base()

class Wallet(Base):
    __tablename__ = "wallets"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    balance = Column(Integer, default=0)