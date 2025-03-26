from pydantic import BaseModel
from datetime import datetime

class Transaction(BaseModel):
    transactionId: str
    user: str
    timestamp: datetime = datetime.utcnow()
