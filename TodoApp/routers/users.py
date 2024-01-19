from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, Path, APIRouter, Request, Form
from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates

from TodoApp.database import SessionLocal
from .auth import get_current_user, verify_password, get_password_hash
from starlette import status
from pydantic import BaseModel, Field
from passlib.context import CryptContext
from TodoApp.models.modelUser import User

router = APIRouter(
    prefix="/user",
    tags=["user"],
    responses={404: {'description': 'Not Found'}}
)


class UserVerification(BaseModel):
    old_password: str = Field(..., min_length=8)
    new_password: str = Field(..., min_length=8)


class EditUserRequest(BaseModel):
    email: str = Field(..., min_length=1)
    first_name: str = Field(..., min_length=1)
    last_name: str = Field(..., min_length=1)
    phone_number: str = Field(..., min_length=1)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.get('/', status_code=status.HTTP_200_OK)
async def get_user(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")

    return db.query(User).filter(User.id == user.get('id')).first()


@router.put('/change_password', status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
        user: user_dependency,
        db: db_dependency,
        user_verification: UserVerification):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")

    user_model = db.query(User).filter(User.id == user.get('id  ')).first()

    if not bcrypt_context.verify(user_verification.old_password, user_model.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect password")

    user.hashed_password = bcrypt_context.hash(user_verification.new_password)

    db.add(user)
    db.commit()


@router.put('/edit__user', status_code=status.HTTP_204_NO_CONTENT)
async def edit_user(
        user: user_dependency,
        db: db_dependency,
        edit_user_request: EditUserRequest
):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")

    user_model = db.query(User).filter(User.id == user.get('id')).first()

    user_model.email = edit_user_request.email
    user_model.first_name = edit_user_request.first_name
    user_model.last_name = edit_user_request.last_name
    user_model.phone_number = edit_user_request.phone_number

    db.add(user_model)
    db.commit()


templates = Jinja2Templates(directory='templates')


@router.get('/change-password')
async def change_password(request: Request, db: db_dependency):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url='/auth', status_code=status.HTTP_302_FOUND)

    user_model = db.query(User).filter(User.id == user.get('id')).first()

    username = user_model.username

    return templates.TemplateResponse(
        'change_password.html',
        {
            "request": request,
            'user': user,
            'username': username
        }
    )


@router.post('/change-password')
async def change_password_commit(request: Request,
                                 db: db_dependency,
                                 username: str = Form(...),
                                 current_password: str = Form(...),
                                 new_password: str = Form(...),
                                 new_password_confirm: str = Form(...),
                                 ):
    user = await get_current_user(request)

    if user is None:
        return RedirectResponse(url='/auth', status_code=status.HTTP_302_FOUND)

    user_model = db.query(User).filter(User.id == user.get('id')).first()

    if not verify_password(current_password, user_model.hashed_password):
        msg = 'Incorrect Password'
        return templates.TemplateResponse('change_password.html',
                                          {
                                              'request': request,
                                              'username': username, 'msg': msg})

    if new_password != new_password_confirm:
        msg = 'Passwords do not match'
        return templates.TemplateResponse('change_password.html',
                                          {
                                              'request': request,
                                              'username': username, 'msg': msg})

    user_model.hashed_password = get_password_hash(new_password)

    db.add(user_model)
    db.commit()

    msg = 'password updated'

    return templates.TemplateResponse('change_password.html',
                                      {
                                          'request': request,
                                          'username': username,
                                          'msg': msg})
