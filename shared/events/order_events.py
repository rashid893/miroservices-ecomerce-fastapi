"""
Event schema definitions for future RabbitMQ/event-driven integration.
When order-service creates an order, it will publish an OrderCreatedEvent.
product-service can consume it to decrement stock.
"""
import uuid
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class OrderCreatedEvent:
    """Published when a new order is created (future use)."""
    event_type: str = "order.created"
    order_id: str = ""
    user_id: str = ""
    items: list[dict] = field(default_factory=list)
    total: str = "0.00"
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
