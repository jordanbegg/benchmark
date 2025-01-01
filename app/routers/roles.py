from typing import Annotated

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlmodel import Session, select

from app.db.models import (
    RoleCreate,
    Role,
    Permission,
    RolePermissions,
    RoleReadOnlyPermissions,
)
from app.dependencies import get_session
from app.auth import get_current_user, require_permission


router = APIRouter(
    prefix="/roles",
    responses={404: {"description": "Not Found"}},
)


@router.post("/", response_model=RoleReadOnlyPermissions)
@require_permission("create_role")
def create_role(
    *,
    session: Session = Depends(get_session),
    role: RoleCreate,
    current_user: Annotated[str, Depends(get_current_user)],
):
    if session.exec(select(Role).where(Role.name == role.name.lower())).first():
        raise ValueError(f"Role named {role.name} already exists!")

    role_db = Role(name=role.name.lower())
    session.add(role_db)
    session.commit()
    session.refresh(role_db)

    for permission_id in role.permission_ids:
        if not (permission_db := session.get(Permission, permission_id)):
            raise HTTPException(
                status_code=404,
                detail=f"Permission with id {permission_id} not found",
            )
        role_permission_db = RolePermissions(role=role_db, permission=permission_db)
        session.add(role_permission_db)
        session.commit()
        session.refresh(role_permission_db)
    session.add(role_db)
    session.commit()
    session.refresh(role_db)
    return role_db


@router.get("/", response_model=list[RoleReadOnlyPermissions])
@require_permission("read_role")
def read_roles(
    *,
    session: Session = Depends(get_session),
    offset: int = 0,
    limit: int = Query(default=100, lte=100),
    current_user: Annotated[str, Depends(get_current_user)],
):
    return session.exec(
        select(Role).order_by(Role.id).offset(offset).limit(limit)
    ).all()


@router.get("/{role_id}", response_model=RoleReadOnlyPermissions)
@require_permission("read_role")
def read_role(
    *,
    session: Session = Depends(get_session),
    role_id: int,
    current_user: Annotated[str, Depends(get_current_user)],
):
    if role := session.get(Role, role_id):
        return role
    else:
        raise HTTPException(status_code=404, detail="Role not found")


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


@router.delete("/{role_id}")
@require_permission("delete_role")
def delete_role(
    *,
    session: Session = Depends(get_session),
    role_id: int,
    current_user: Annotated[str, Depends(get_current_user)],
):
    role = session.get(Role, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    # Need to delete the role permissions first
    for role_permission in role.role_permissions:
        session.delete(role_permission)
        session.commit()
    session.delete(role)
    session.commit()
    return {"ok": True}
