# models.py - DAHA MƏNTİQLİ VERSİYA
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from sqlalchemy import UniqueConstraint
from pydantic import validator

class WishlistBase(SQLModel):
    user_id: str
    product_variation_id: Optional[str] = None
    shop_id: Optional[str] = None
    
    @validator('product_variation_id', 'shop_id')
    def validate_at_least_one(cls, v, values):
        if 'product_variation_id' in values and 'shop_id' in values:
            if not values.get('product_variation_id') and not values.get('shop_id'):
                raise ValueError('Either product_variation_id or shop_id must be provided')
        return v

class Wishlist(WishlistBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # ✅ UNIQUE CONSTRAINT - eyni user eyni kombinasiyanı iki dəfə əlavə edə bilməz
    __table_args__ = (
        UniqueConstraint('user_id', 'product_variation_id', 'shop_id', 
                        name='unique_user_product_shop'),
    )

class WishlistCreate(WishlistBase):
    pass

class WishlistResponse(WishlistBase):
    id: int
    created_at: datetime

class WishlistListResponse(SQLModel):
    items: list[WishlistResponse]