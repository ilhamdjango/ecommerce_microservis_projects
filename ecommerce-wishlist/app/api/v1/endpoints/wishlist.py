# app/api/v1/endpoints/wishlist.py faylında

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.database import get_session
from app.models import Wishlist, WishlistCreate, WishlistResponse, WishlistListResponse

router = APIRouter(tags=["Wishlist"])

# ✅ YENİ VERSİYA - HEÇ BİR YOXLAMA YOXDUR

# POST /api/wishlist/ → add to wishlist
@router.post("/", response_model=WishlistResponse, status_code=status.HTTP_201_CREATED)
async def add_to_wishlist(
    wishlist: WishlistCreate, 
    session: Session = Depends(get_session)
):
    # Fixed user_id - heç bir yoxlama yoxdur
    user_id = "user-123e4567-e89b-12d3-a456-426614174000"
    
    # ... qalan kod eyni (user_id parametrini sil)

# GET /api/wishlist/ → list wishlist items  
@router.get("/", response_model=WishlistListResponse)
def list_wishlist(
    session: Session = Depends(get_session)
):
    # Fixed user_id - heç bir yoxlama yoxdur
    user_id = "user-123e4567-e89b-12d3-a456-426614174000"
    
    statement = select(Wishlist).where(Wishlist.user_id == user_id)
    items = session.exec(statement).all()
    return WishlistListResponse(items=items)

# DELETE /api/wishlist/{item_id} → remove from wishlist
@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_from_wishlist(
    item_id: int,
    session: Session = Depends(get_session)
):
    # Fixed user_id - heç bir yoxlama yoxdur
    user_id = "user-123e4567-e89b-12d3-a456-426614174000"
    
    statement = select(Wishlist).where(
        Wishlist.id == item_id, 
        Wishlist.user_id == user_id
    )
    # ... qalan kod eyni