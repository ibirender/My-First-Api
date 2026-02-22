import bcrypt
from fastapi import FastAPI, Depends, HTTPException, status,Header,BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime,timedelta
from app import models, schemas, crud  # Changed from . import to app import
from app.database import engine, get_db  # Changed from .database to app.database
import secrets
import random
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials  
from app.email_service import send_reset_email # ← YEH LINE ADD KARO

# YEH BHI ADD KARO - security scheme define karo
security = HTTPBearer()
# In-memory token storage (for development only)
fake_token_db = {}

# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Product Management API",
    description="Product Management System",
    version="1.0.0"
)

# ===== STEP 1: USER REGISTRATION (POST /register) =====
@app.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if username exists
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Check if email exists
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    return crud.create_user(db=db, user=user)


# ===== STEP 2: LOGIN (POST /login) =====
@app.post("/login", response_model=schemas.Token)
def login(user_data: schemas.UserLogin, db: Session = Depends(get_db)):
    """Login and get access token"""
    # Authenticate user
    user = crud.authenticate_user(db, user_data.username, user_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    # Generate simple token
    token = secrets.token_hex(16)  # e.g., "4f7a3b1c8e2d9f5a"
    
    # Store token
    fake_token_db[token] = user.username
    
    return {
        "access_token": token,
        "token_type": "bearer"
    }

# ===== STEP 3: GET CURRENT USER (GET /users/me) =====
# def get_current_user(authorization: str = Depends(lambda: None), db: Session = Depends(get_db)):
#     """Dependency to get current user from token"""
#     # This is simplified - in real app, you'd get from Header
#     # For now, we'll pass token as query param for testing
#     raise HTTPException(
#         status_code=status.HTTP_501_NOT_IMPLEMENTED,
#         detail="Will implement in next step"
#     )
@app.get("/users/me", response_model=schemas.UserResponse)  
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Dependency to get current user from token"""
    # Token extract karo (credentials se)
    token = credentials.credentials
    
    # Check if token exists in our fake database
    if token not in fake_token_db:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    # Get username from token
    username = fake_token_db[token]
    
    # Get user from database
    user = crud.get_user_by_username(db, username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user

# 1. UPDATE PROFILE - apni info badlo
@app.put("/users/me")
def update_profile(
    user_update: schemas.UserUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    for key, value in user_update.model_dump(exclude_unset=True).items():
        setattr(current_user, key, value)
    db.commit()
    db.refresh(current_user)
    return current_user




@app.post("/change-password")
def change_password(
    password_data: schemas.ChangePassword,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
  # Check current password
    if not bcrypt.checkpw(
        password_data.current_password.encode('utf-8'),
        current_user.hashed_password.encode('utf-8')
    ):
        raise HTTPException(400, "Current password is incorrect")
     # Check new passwords match
    if password_data.new_password != password_data.confirm_password:
        raise HTTPException(400, "New passwords do not match")
    # Hash new password
    salt = bcrypt.gensalt()
    new_hashed = bcrypt.hashpw(
        password_data.new_password.encode('utf-8'),
        salt
    )
    
    # Update database
    current_user.hashed_password = new_hashed.decode('utf-8')
    db.add(current_user)  
    db.commit()
    db.refresh(current_user)

     # 5. 🔥 IMPORTANT: DELETE ALL TOKENS for this user
    tokens_to_delete = []
    for token, username in fake_token_db.items():
        if username == current_user.username:
            tokens_to_delete.append(token)
    for token in tokens_to_delete:
        fake_token_db.pop(token)
        print(f"deleted token: {token} and curent user is {current_user.username}")
        print("yes deleted all tokens for this user")
    
    return {
        "message": "Password changed successfully. You have been logged out from all devices.",
        "tokens_deleted": len(tokens_to_delete)
    }



@app.post("/logout")
def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    if token in fake_token_db:
        fake_token_db.pop(token)
        return {"message": "Logged out successfully"}
    else:
        raise HTTPException 
    {"message":"token is already expired or invalid try again with valid token"}



@app.get("/")
def root():
    return {
        "message": "Product Management API",
        "version": "1.0.0",
        "endpoints": {
            "POST /users/": "Register new user",
            "GET /users/{username}": "Get user by username",
            "GET /products": "Get all products",
             "POST /login": "Login and get token",    # New
            "GET /users/me": "Get my profile",  #new
            "GET /products/{id}": "Get product by ID",
            "POST /products": "Create new product",
            "PUT /products/{id}": "Update product",
            "DELETE /products/{id}": "Delete product",
            "GET /health": "Health check"
        }
    }

# User endpoints
@app.post("/users/", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if user already exists
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    return crud.create_user(db=db, user=user)

@app.get("/users/{username}", response_model=schemas.UserResponse)
def get_user(username: str, db: Session = Depends(get_db)):
    """Get user by username"""
    db_user = crud.get_user_by_username(db, username=username)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

# Product endpoints
@app.post("/products/", response_model=schemas.ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    """Create a new product"""
    return crud.create_product(db=db, product=product)

@app.get("/products/", response_model=List[schemas.ProductResponse])
def read_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all products with pagination"""
    products = crud.get_products(db, skip=skip, limit=limit)
    return products

@app.get("/products/{product_id}", response_model=schemas.ProductResponse)
def read_product(product_id: int, db: Session = Depends(get_db)):
    """Get a specific product by ID"""
    db_product = crud.get_product(db, product_id=product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product

@app.put("/products/{product_id}", response_model=schemas.ProductResponse)
def update_product(product_id: int, product: schemas.ProductUpdate, db: Session = Depends(get_db)):
    """Update a product"""
    db_product = crud.update_product(db, product_id=product_id, product_update=product)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product

@app.delete("/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    """Delete a product"""
    db_product = crud.delete_product(db, product_id=product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product deleted successfully"}

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    """Health check endpoint"""
    try:
        db.execute("SELECT 1")
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.now()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }
    
def get_current_admin(current_user: models.User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    return current_user
def get_user_count(db: Session):
    """Total users count return karega"""
    return db.query(models.User).count()

def get_product_count(db:Session):
    """Total products count return karega"""
    return db.query(models.Product).count()

@app.get("/admin-dashboard")
def admin_dashboard(admin:models.User = Depends(get_current_admin), db: Session = Depends(get_db)):
    return {"message": f"Welcome to the admin dashboard, {admin.username} and total users count is {get_user_count(db)} and total products count is {get_product_count(db)}"}

@app.delete("/users/{user_id}")
def delete_user(
    user_id:int,
    admin:models.User = Depends(get_current_admin),
    db:Session=Depends(get_db)):

    user=db.query(models.User).filter(models.User.id==user_id).first()
    # Agar user nahi mila to error do
    if not user:
        raise HTTPException(
            status_code=404,
            detail=f"User with id {user_id} not found"
        )
    
    # User mil gaya to delete karo
    db.delete(user)
    db.commit()
    
    return {"message": f"User {user.username} deleted successfully"}


@app.put("/users/{user_id}/make_amdin")
def make_user_as_admin(user_id:int,
    current_user:models.User = Depends(get_current_user),
    db:Session=Depends(get_db)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    user=db.query(models.User).filter(models.User.id==user_id).first()
    if not user:
        raise HTTPException(status_code=404,detail="user not found")
    user.is_admin=True
    db.commit()

    
    return {"message": f"{user.username} is now an admin"}
@app.get("/check-admin")
def check_admin(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    admins = db.query(models.User)\
               .filter(models.User.is_admin == True)\
               .all()

    return {"all_admins": admins}

# @app.post("/forgot-password")
# def forgot_password(email: str, db: Session = Depends(get_db)):
#     """Password reset ke liye token generate"""
#     user = db.query(models.User)\
#              .filter(models.User.email == email)\
#              .first()
#     if not user:
#         raise HTTPException(status_code=404, detail="Email not found")
#     # Generate reset token
#     reset_token = secrets.token_hex(16)
#     user.reset_token = reset_token
#     db.commit()
#     return{"message": "Password reset token generated", "reset_token": reset_token}


# @app.post("/reset-password/")
# def reset_password(token:str, new_password:str, confirm_password:str, db:Session = Depends(get_db)):
#     """Password reset karne ke liye token verify karo aur password update karo"""
#     user = db.query(models.User).filter(models.User.reset_token == token).first()
#     if not user:
#         raise HTTPException(status_code=400, detail="Invalid or expired token")
#     if new_password != confirm_password:
#         raise HTTPException(status_code=400, detail="New passwords do not match to confirm password")
#     # Hash new password
#     salt = bcrypt.gensalt()
#     new_hashed = bcrypt.hashpw(new_password.encode('utf-8'), salt)
#     user.hashed_password = new_hashed.decode('utf-8')
#     user.reset_token = None  # Clear reset token
#     db.commit()     
#     return {"message": "Password reset successfully"}

# app/main.py mein ye import karo (top par)
from datetime import datetime, timedelta
from fastapi import BackgroundTasks
from app.email_service import send_reset_email

# ===== FORGOT PASSWORD ENDPOINT =====
@app.post("/forgot-password")
def forgot_password(
    email: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Password reset link bhejo email par"""
    
    # User dhundo
    user = db.query(models.User).filter(models.User.email == email).first()
    
    # Security: Same response (chahe email ho ya na ho)
    if not user:
        # Brute force se bachne ke liye delay
        import time
        time.sleep(1)
        return {"message": "If email exists, reset link sent"}
    
    # Token generate karo
    #token = secrets.token_urlsafe(32)
    # OTP bhi generate karo
    otp = str(random.randint(100000, 999999))
    
    # Token save karo with expiry (1 hour)
    user.otp = otp
    user.otp_expiry = datetime.utcnow() + timedelta(hours=.5)
    db.commit()
    
    # Background mein email bhejo
    background_tasks.add_task(send_reset_email, email, otp)
    
    return {"message": "Reset link sent to your email"}


# ===== RESET PASSWORD ENDPOINT =====
@app.post("/reset-password")
def reset_password(
    otp: str,
    new_password: str,
    db: Session = Depends(get_db)
):
    """Token verify karo aur password reset karo"""
    
    # Token se user dhundo
    user = db.query(models.User).filter(models.User.otp == otp).first()
    
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")
    
    # Expiry check karo
    if user.otp_expiry < datetime.utcnow():
        raise HTTPException(status_code=400, detail="OTP has expired")
    
    # Naya password hash karo
    hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
    user.hashed_password = hashed.decode('utf-8')
    
    # OTP clear karo (ek baar use)
    user.otp = None
    user.otp_expiry = None
    
    db.commit()
    
    return {"message": "Password updated successfully"}

