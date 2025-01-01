from typing import Annotated

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlmodel import Session, select

from app.db.models import (
    PermissionCreate,
    PermissionRead,
    Permission,
)
from app.dependencies import get_session
from app.auth import get_current_user, require_permission


router = APIRouter(
    prefix="/permissions",
    responses={404: {"description": "Not Found"}},
)


@router.post("/", response_model=PermissionRead)
@require_permission("create_permission")
def create_permission(
    *,
    session: Session = Depends(get_session),
    permission: PermissionCreate,
    current_user: Annotated[str, Depends(get_current_user)],
):
    if session.exec(
        select(Permission).where(Permission.name == permission.name.lower())
    ).first():
        raise ValueError(f"Permission named {permission.name} already exists!")

    permission_db = Permission(name=permission.name.lower())
    session.add(permission_db)
    session.commit()
    session.refresh(permission_db)
    return permission_db


@router.get("/", response_model=list[PermissionRead])
@require_permission("read_permission")
def read_permissions(
    *,
    session: Session = Depends(get_session),
    offset: int = 0,
    limit: int = Query(default=100, lte=100),
    current_user: Annotated[str, Depends(get_current_user)],
):
    return session.exec(
        select(Permission).order_by(Permission.id).offset(offset).limit(limit)
    ).all()


@router.get("/{permission_id}", response_model=PermissionRead)
@require_permission("read_permission")
def read_permission(
    *,
    session: Session = Depends(get_session),
    permission_id: int,
    current_user: Annotated[str, Depends(get_current_user)],
):
    if permission := session.get(Permission, permission_id):
        return permission
    else:
        raise HTTPException(status_code=404, detail="Permission not found")


# @router.patch("/{exercise_id}", response_model=ExerciseReadWithMuscleGroups)
# def update_exercise(
#     *,
#     session: Session = Depends(get_session),
#     exercise_id: int,
#     exercise: ExerciseUpdate,
# ):
#     db_exercise = session.get(Exercise, exercise_id)
#     if not db_exercise:
#         raise HTTPException(status_code=404, detail="Exercise not found")

#     exercise_data = exercise.dict(exclude_unset=True)
#     for key, value in exercise_data.items():
#         if key == "musclegroup_ids":
#             musclegroups = []
#             for musclegroup_id in value:
#                 if musclegroup := session.get(MuscleGroup, musclegroup_id):
#                     musclegroups.append(musclegroup)
#             db_exercise.musclegroups = musclegroups
#         elif key == "name":
#             if session.exec(
#                 select(Exercise).where(
#                     Exercise.name == value.lower(),
#                     Exercise.id != db_exercise.id,
#                 )
#             ).first():
#                 raise ValueError(
#                     f"Exercise with name {value.lower()} already exists!"
#                 )
#             else:
#                 setattr(db_exercise, key, value.lower())
#         else:
#             setattr(db_exercise, key, value)
#     session.add(db_exercise)
#     session.commit()
#     session.refresh(db_exercise)
#     return db_exercise


@router.delete("/{permission_id}")
@require_permission("delete_permission")
def delete_permission(
    *,
    session: Session = Depends(get_session),
    permission_id: int,
    current_user: Annotated[str, Depends(get_current_user)],
):
    permission = session.get(Permission, permission_id)
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    # Need to delete the role permissions first
    for role_permission in permission.role_permissions:
        session.delete(role_permission)
        session.commit()
    session.delete(permission)
    session.commit()
    return {"ok": True}
