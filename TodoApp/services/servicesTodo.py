from models.modelTodo import Todo


def delete_todo_existing(todo_id, db, user):
    read_todo_by_id(todo_id, db, user).delete()
    db.commit()


def create_new_todo(todo_model, db):
    db.add(todo_model)
    db.commit()


def update_todo_existing(todo_model, todo_request, db):
    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.priority = todo_request.priority
    todo_model.complete = todo_request.complete

    db.add(todo_model)
    db.commit()


def read_todo_by_id(todo_id, db, user):
    return db.query(Todo).filter(Todo.id == todo_id).filter(Todo.owner_id == user.get('id')).first()


def read_all_todo(db):
    return db.query(Todo).all()
