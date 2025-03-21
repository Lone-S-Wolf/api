# Guide to Adding a New Model

If you want to add a new model to the application, you'll need to update several files following these steps:

## 1. Update `app/models/models.py`

Add your new model class to the models file:

```python
class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(String)
    answer = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

## 2. Update `app/schemas/schemas.py`

Add corresponding Pydantic schemas for request validation and response serialization:

```python
# Question schemas
class QuestionBase(BaseModel):
    title: str
    content: str
    answer: Optional[str] = None
    is_active: bool = True

class QuestionCreate(QuestionBase):
    pass

class QuestionUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    answer: Optional[str] = None
    is_active: Optional[bool] = None

class Question(QuestionBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
```

## 3. Create `app/routers/questions.py`

Create a new router file for your model with the appropriate endpoints:

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database.database import get_db
from app.models.models import Question as ModelQuestion, User, UserRole
from app.schemas.schemas import Question, QuestionCreate, QuestionUpdate
from app.auth.rbac import get_user_with_roles, get_admin_user

# Only managers and admins can access these endpoints
manager_users = get_user_with_roles([UserRole.MANAGER, UserRole.ADMIN])

router = APIRouter(
    prefix="/questions",
    tags=["questions"],
    dependencies=[Depends(manager_users)]  # Base authentication for all endpoints
)

@router.post("/", response_model=Question, status_code=status.HTTP_201_CREATED)
def create_question(
    question: QuestionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(manager_users)
):
    """Create a new question - Manager and Admin only"""
    db_question = ModelQuestion(**question.model_dump())
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    return db_question

# Add more endpoints as needed...
```

## 4. Update `app/main.py`

Include your new router in the main application:

```python
from fastapi import FastAPI
from app.routers import auth, items, admin, manager, user, viewer, questions

app = FastAPI()

# Include routers
app.include_router(auth.router)
app.include_router(items.router)
app.include_router(admin.router)
app.include_router(manager.router)
app.include_router(user.router)
app.include_router(viewer.router)
app.include_router(questions.router)  # Add this line

@app.get("/")
def read_root():
    return {"message": "Welcome to the API"}
```

## 5. Create Database Migration (Optional)

If you're using Alembic for migrations, create a new migration:

```bash
alembic revision --autogenerate -m "Add questions table"
alembic upgrade head
```

## Additional Considerations

- Consider adding related models if your new model has relationships
- Update tests to cover the new model and endpoints
- Document the new API endpoints
- Update permissions if needed
