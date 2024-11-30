from fastapi import APIRouter, Depends, Query, HTTPException
from sqlmodel import Session, select

from app.db.models import (
    User,
    UserRead,
    UserCreate
)
from app.dependencies import get_session

router = APIRouter(
    prefix="/users",
    responses={404: {"description": "Not Found"}},
)


@router.post("/", response_model=UserRead)
def create_user(*, session: Session = Depends(get_session), user: UserCreate):
    db_user = User.from_orm(user)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@router.get("/", response_model=list[UserRead])
def read_users(
    *,
    session: Session = Depends(get_session),
    offset: int = 0,
    limit: int = Query(default=100, lte=100),
):
    return session.exec(
        select(User).order_by(User.id).offset(offset).limit(limit)
    ).all()


@router.get(
    "/{user_id}",
    response_model=UserRead,
)
def read_user(*, session: Session = Depends(get_session), user_id: int):
    if user := session.get(User, user_id):
        return user
    else:
        raise HTTPException(status_code=404, detail="User not found")


# @router.patch("/{musclegroup_id}", response_model=MuscleGroupRead)
# def update_musclegroup(
#     *,
#     session: Session = Depends(get_session),
#     musclegroup_id: int,
#     musclegroup: MuscleGroupUpdate,
# ):
#     db_musclegroup = session.get(User, musclegroup_id)
#     if not db_musclegroup:
#         raise HTTPException(status_code=404, detail="User not found")
#     musclegroup_data = musclegroup.dict(exclude_unset=True)
#     for key, value in musclegroup_data.items():
#         if key == "name":
#             if session.exec(
#                 select(User).where(
#                     User.name == value.lower(),
#                     User.id != db_musclegroup.id,
#                 )
#             ).first():
#                 raise ValueError(
#                     f"User with name {value.lower()} already exists!"
#                 )
#             else:
#                 setattr(db_musclegroup, key, value.lower())
#         setattr(db_musclegroup, key, value)
#     session.add(db_musclegroup)
#     session.commit()
#     session.refresh(db_musclegroup)
#     return db_musclegroup


@router.delete("/{user_id}")
def delete_user(*, session: Session = Depends(get_session), user_id: int):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    for weight in user.weights:
        session.delete(weight)
    for workout_routine in user.workout_routines:
        for routine_exercise in workout_routine.routine_exercises:
            for planned_set in routine_exercise.planned_sets:
                session.delete(planned_set)
            session.delete(routine_exercise)
        for workout in workout_routine.workouts:
            for workout_exercise in workout.workout_exercises:
                for sset in workout_exercise.sets:
                    session.delete(sset)
                session.delete(workout_exercise)
            session.delete(workout)
        session.delete(workout_routine)
    session.delete(user)
    session.commit()
    return {"ok": True}
