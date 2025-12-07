"""
Database models untuk Product.
Saat ini menggunakan simple dict storage, nanti bisa diganti dengan Supabase ORM.
"""
from datetime import datetime
from typing import Optional
from uuid import uuid4


class Product:
    """Product model untuk database storage."""
    
    def __init__(
        self,
        title: str,
        description: str,
        category: str,
        price: int,
        image_path: str,
        user_id: Optional[str] = None,
        product_id: Optional[str] = None,
        created_at: Optional[datetime] = None
    ):
        self.product_id = product_id or str(uuid4())
        self.title = title
        self.description = description
        self.category = category
        self.price = price
        self.image_path = image_path
        self.user_id = user_id
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "product_id": self.product_id,
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "price": self.price,
            "image_path": self.image_path,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Product":
        """Create Product instance from dictionary."""
        return cls(
            product_id=data.get("product_id"),
            title=data["title"],
            description=data["description"],
            category=data["category"],
            price=data["price"],
            image_path=data["image_path"],
            user_id=data.get("user_id"),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None
        )
