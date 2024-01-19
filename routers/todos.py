import sys
from fastapi import Depends, APIRouter, Request, Form
from sqlalchemy.orm import Session
from .auth import get_current_user
from models.modelTodo import Todo
from database import SessionLocal
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from starlette.responses import RedirectResponse
from starlette import status

sys.path.append("../TodoApp")

router = APIRouter(
    prefix="/todo",
    tags=["todo"],
    responses={404: {"description": "Not found"}}
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


templates = Jinja2Templates(directory='templates')


@router.get('/', response_class=HTMLResponse)
async def read_all_by_user(request: Request, db: Session = Depends(get_db)):
    
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url='/auth', status_code=status.HTTP_302_FOUND)
    
    todos = db.query(Todo).filter(Todo.owner_id == user.get('id')).all()

    return templates.TemplateResponse('home.html', {"request": request, 'todos': todos, 'user': user})


@router.get('/add-todo', response_class=HTMLResponse)
async def add_new_todo(request: Request):

    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url='/auth', status_code=status.HTTP_302_FOUND)

    return templates.TemplateResponse('add-todo.html', {'request': request, 'user': user})


@router.post('/add-todo', response_class=HTMLResponse)
async def create_todo(request: Request, title: str = Form(...), description: str = Form(...),
                      priority: int = Form(...), db: Session = Depends(get_db)):

    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url='/auth', status_code=status.HTTP_302_FOUND)

    todo_model = Todo()
    todo_model.title = title
    todo_model.description = description
    todo_model.priority = priority
    todo_model.complete = False
    todo_model.owner_id = user.get('id')

    db.add(todo_model)
    db.commit()

    return RedirectResponse(url='/todo', status_code=status.HTTP_302_FOUND)


@router.get('/edit-todo/{todo_id}', response_class=HTMLResponse)
async def edit_todo(request: Request, todo_id: int, db: Session = Depends(get_db)):

    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url='/auth', status_code=status.HTTP_302_FOUND)

    todo = db.query(Todo).filter(Todo.id == todo_id).first()

    return templates.TemplateResponse('edit-todo.html', {'request': request, 'todo': todo, 'user': user})


@router.post('/edit-todo/{todo_id}', response_class=HTMLResponse)
async def edit_todo_commit(request: Request, todo_id: int, title: str = Form(...), description: str = Form(...),
                           priority: int = Form(...), db: Session = Depends(get_db)):

    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url='/auth', status_code=status.HTTP_302_FOUND)

    todo = db.query(Todo).filter(Todo.id == todo_id).first()

    if not todo:
        return RedirectResponse(url='/todo', status_code=status.HTTP_302_FOUND)

    todo.title = title
    todo.description = description
    todo.priority = priority

    db.commit()

    return RedirectResponse(url='/todo', status_code=status.HTTP_302_FOUND)


@router.get('/delete/{todo_id}', response_class=HTMLResponse)
async def delete_todo(request: Request, todo_id: int, db: Session = Depends(get_db)):

    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url='/auth', status_code=status.HTTP_302_FOUND)

    todo = db.query(Todo).filter(Todo.id == todo_id).filter(Todo.owner_id == user.get('id')).first()

    db.delete(todo)
    db.commit()

    return RedirectResponse(url='/todo', status_code=status.HTTP_302_FOUND)


@router.get('/complete/{todo_id}', response_class=HTMLResponse)
async def complete_todo(request: Request, todo_id: int, db: Session = Depends(get_db)):

    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url='/auth', status_code=status.HTTP_302_FOUND)

    todo = db.query(Todo).filter(Todo.id == todo_id).first()

    todo.complete = not todo.complete

    db.add(todo)
    db.commit()

    return RedirectResponse(url='/todo', status_code=status.HTTP_302_FOUND)
