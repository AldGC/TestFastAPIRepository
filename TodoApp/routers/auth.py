from datetime import timedelta, datetime
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Request, Response, Form
from pydantic import BaseModel
from sqlalchemy.orm import Session
from TodoApp.database import SessionLocal, engine, Base
from TodoApp.models.modelUser import User
from passlib.context import CryptContext
from starlette import status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from typing import Optional
from fastapi.responses import HTMLResponse
from starlette.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory='templates')

import sys

sys.path.append("..")

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={401: {"user": "Not authorized"}}
)


class LoginForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.username: Optional[str] = None
        self.password: Optional[str] = None

    async def create_oauth_form(self):
        form = await self.request.form()
        self.username = form.get("email")
        self.password = form.get("password")


SECRET_KEY = '545a77147eb035b5c7efb48478fc6501de2ab0700ba6f176cf921144636deea2'
ALGORITHM = 'HS256'

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
Oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")
Base.metadata.create_all(bind=engine)


"""class CreateUserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str
    phone_number: str"""


class Token(BaseModel):
    access_token: str
    token_type: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


def get_password_hash(password):
    return bcrypt_context.hash(password)


def verify_password(plain_password, hashed_password):
    return bcrypt_context.verify(plain_password, hashed_password)


def authenticated_user(username: str, password: str, db):
    user = db.query(User).filter(User.username == username).first()

    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user


def create_access_token(username: str, user_id: int, role: str,
                        expires_delta: Optional[timedelta] = None):
    encode = {
        "sub": username,
        "id": user_id,
        'role': role,
    }

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    encode.update({"exp": expire})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(request: Request):
    try:
        token = request.cookies.get('access_token')
        if token is None:
            return None

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        user_role: str = payload.get('role')
        if username is None or user_id is None:
            logout(request)

        return {"username": username, "id": user_id, 'user_role': user_role}

    except JWTError:
        raise HTTPException(status_code=404, detail="Not found")
        """raise get_user_exception()"""


"""@router.post(
    path='/create_user',
    status_code=status.HTTP_201_CREATED,
    summary='Create user',

)
async def create_user(db: db_dependency, create_user_request: CreateUserRequest):
    create_user_request = User(
        email=create_user_request.email,
        username=create_user_request.username,
        first_name=create_user_request.first_name,
        last_name=create_user_request.last_name,
        role=create_user_request.role,
        hashed_password=get_password_hash(create_user_request.password),
        is_active=True,
        phone_number=create_user_request.phone_number
    )

    db.add(create_user_request)
    db.commit()
"""

@router.post('/token')
async def login_for_access_token(response: Response,
                                 db: db_dependency,
                                 form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticated_user(form_data.username, form_data.password, db)

    if not user:
        return False

    token = create_access_token(user.username, user.id, user.role, timedelta(minutes=60))

    response.set_cookie(key='access_token', value=token, httponly=True)

    return True


@router.get('/', response_class=HTMLResponse)
async def authentication_page(request: Request):
    return templates.TemplateResponse('login.html', {'request': request})


@router.post('/', response_class=HTMLResponse)
async def login(request: Request, db: db_dependency):
    try:
        form = LoginForm(request)
        await form.create_oauth_form()
        response = RedirectResponse(url='/todo', status_code=status.HTTP_302_FOUND)

        validate_user_cookie = await login_for_access_token(response=response, form_data=form, db=db)

        if not validate_user_cookie:
            msg = 'Incorrect Username or Password'
            return templates.TemplateResponse('login.html', {'request': request, 'msg': msg})

        return response
    except HTTPException:
        msg = 'Unknown Error'
        return templates.TemplateResponse('login.html', {'request': request, 'msg': msg})


@router.get('/logout')
async def logout(request: Request):
    msg = 'Logout Successful'
    response = templates.TemplateResponse('Login.html', {'request': request, 'msg': msg})
    response.delete_cookie(key='access_token')
    return response


@router.get('/register', response_class=HTMLResponse)
async def register(request: Request):
    return templates.TemplateResponse('register.html', {'request': request})


@router.post('/register', response_class=HTMLResponse)
async def register_user(request: Request,
                        db: db_dependency,
                        email: str = Form(...),
                        username: str = Form(...),
                        first_name: str = Form(...),
                        last_name: str = Form(...),
                        password: str = Form(...),
                        password_confirmation: str = Form(...),
                        ):
    validation1 = db.query(User).filter(User.username == username).first()
    validation2 = db.query(User).filter(User.email == email).first()

    if password != password_confirmation or validation1 is not None or validation2 is not None:
        msg = 'Invalid registration request'
        return templates.TemplateResponse('register.html', {'request': request, 'msg': msg})

    user_model = User()
    user_model.email = email
    user_model.username = username
    user_model.first_name = first_name
    user_model.last_name = last_name
    user_model.hashed_password = get_password_hash(password)
    user_model.is_active = True

    db.add(user_model)
    db.commit()

    msg = 'User successfully created'
    return templates.TemplateResponse('login.html', {'request': request, 'msg': msg})

"""
def get_user_exception():
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return credentials_exception


def token_exception():
    token_exception_response = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return token_exception_response
"""