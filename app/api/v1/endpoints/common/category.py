from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.session import get_db
from app.models.common.category import Category
from app.schemas.common.category import CategoryCreate, CategoryUpdate, CategoryEventMapRequest, CategoryResponse
from app.api.v1.endpoints.auth import get_current_user
from app.models.common.category_event_mappings import CategoryEventMapping
from app.models.common.events import Event


router = APIRouter()

@router.post("/categories", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    *,
    db: Session = Depends(get_db),
    category_in: CategoryCreate,
    current_user = Depends(get_current_user)
):
    """Create new category"""
    category = Category(
        name=category_in.name,
        description=category_in.description,
        image_url=category_in.image_url,
        status=category_in.status,
        created_by=current_user.id
    )
    db.add(category)
    try:
        db.commit()
        db.refresh(category)
    except Exception as e:
        db.rollback()
        if "duplicate key" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category with this name already exists"
            )
        raise
    return category

@router.get("/categories", response_model=List[CategoryResponse])
def get_categories(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    status: Optional[bool] = None,
    name: Optional[str] = None,
):
    """Get list of categories"""
    query = db.query(Category)
    if status is not None:
        query = query.filter(Category.status == status)
    if name:
        query = query.filter(Category.name.ilike(f"%{name}%"))
    return query.offset(skip).limit(limit).all()

@router.get("/categories/{category_id}", response_model=CategoryResponse)
def get_category(
    category_id: int,
    db: Session = Depends(get_db)
):
    """Get category by ID"""
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@router.put("/categories/{category_id}", response_model=CategoryResponse)
def update_category(
    *,
    db: Session = Depends(get_db),
    category_id: int,
    category_in: CategoryUpdate,
    current_user = Depends(get_current_user)
):
    """Update category"""
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    update_data = category_in.dict(exclude_unset=True)
    update_data["updated_by"] = current_user.id
    
    for field, value in update_data.items():
        setattr(category, field, value)
    
    try:
        db.commit()
        db.refresh(category)
    except Exception as e:
        db.rollback()
        if "duplicate key" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category with this name already exists"
            )
        raise
    return category

@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    *,
    db: Session = Depends(get_db),
    category_id: int,
    current_user = Depends(get_current_user)
):
    """Delete category"""
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Soft delete by updating status
    category.status = False
    category.updated_by = current_user.id
    db.commit()
    return None

@router.post("/categories/map-event", status_code=status.HTTP_201_CREATED)
def map_category_to_event(
    mapping_in: CategoryEventMapRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Map a category to an event"""
    # Validate category and event existence
    category = db.query(Category).filter(Category.id == mapping_in.category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    event = db.query(Event).filter(Event.id == mapping_in.event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # Check if mapping already exists
    existing = db.query(CategoryEventMapping).filter_by(
        category_id=mapping_in.category_id,
        event_id=mapping_in.event_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Mapping already exists")

    # Create mapping
    mapping = CategoryEventMapping(
        category_id=mapping_in.category_id,
        event_id=mapping_in.event_id
    )
    db.add(mapping)
    db.commit()
    db.refresh(mapping)
    return {"message": "Category mapped to event successfully"}

