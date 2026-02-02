import json
import os
from typing import List, Optional
from datetime import datetime, timedelta

from fastapi import FastAPI, HTTPException, Request, Depends, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from wakeonlan import send_magic_packet
from jose import JWTError, jwt

# --- Configuration ---
SECRET_KEY = "ghost_secret_key_change_this_in_production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 1 week

app = FastAPI(title="Ghost")

templates = Jinja2Templates(directory="templates")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

CONFIG_FILE = "config.json"

# --- Models ---
class PC(BaseModel):
    name: str
    mac: str

class User(BaseModel):
    username: str
    password: str  # In production, store hashes!
    role: str  # "admin" or "user"
    allowed_macs: List[str] = []

class Config(BaseModel):
    pcs: List[PC]
    users: List[User]

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# --- Helpers ---
def load_config() -> Config:
    if not os.path.exists(CONFIG_FILE):
        return Config(pcs=[], users=[])
    with open(CONFIG_FILE, "r") as f:
        data = json.load(f)
        return Config(**data)

def get_user(username: str) -> Optional[User]:
    config = load_config()
    for user in config.users:
        if user.username == username:
            return user
    return None

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_user_optional(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        return None
    try:
        # Bearer token in cookie usually comes as "Bearer <token>" or just "<token>"
        # Let's assume we store just the token string in the cookie
        if token.startswith("Bearer "):
            token = token[7:]
        return await get_current_user(token)
    except HTTPException:
        return None

# --- Routes ---

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = get_user(form_data.username)
    # Simple plain text password check for MVP as requested
    if not user or user.password != form_data.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    user = await get_current_user_optional(request)
    if not user:
        return templates.TemplateResponse("login.html", {"request": request})
    
    config = load_config()
    visible_pcs = []
    
    if user.role == "admin":
        visible_pcs = config.pcs
    else:
        # Filter PCs
        for pc in config.pcs:
            if pc.mac in user.allowed_macs:
                visible_pcs.append(pc)
                
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "pcs": visible_pcs, 
        "user": user,
        "is_admin": user.role == "admin"
    })

@app.post("/api/wake")
async def wake_pc(item: PC, current_user: User = Depends(get_current_user)):
    # Verify permission
    if current_user.role != "admin" and item.mac not in current_user.allowed_macs:
        raise HTTPException(status_code=403, detail="You do not have permission to wake this PC.")
    
    try:
        print(f"User {current_user.username} sending magic packet to {item.mac}")
        send_magic_packet(item.mac)
        return {"status": "success", "message": f"Magic packet sent to {item.name}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/logout")
def logout():
    response = RedirectResponse(url="/")
    response.delete_cookie("access_token")
    return response
