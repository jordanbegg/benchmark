from fastapi import APIRouter, Depends, Query, HTTPException
from sqlmodel import Session, select

from app.db.models import (
    Set,
    SetCreate,
    FullSetRead,
    SetUpdate,
    Exercise,
    Workout,
)
from app.dependencies import get_session

router = APIRouter(
    prefix="/sets",
    responses={404: {"description": "Not Found"}},
)


@router.post("/", response_model=FullSetRead)
def create_set(
    *, session: Session = Depends(get_session), workout_set: SetCreate
):
    db_workout_set = Set.from_orm(workout_set)
    if not session.get(Exercise, workout_set.exercise_id):
        raise HTTPException(
            status_code=404,
            detail=f"Exercise with id {workout_set.exercise_id} not found",
        )
    if not session.get(Workout, workout_set.workout_id):
        raise HTTPException(
            status_code=404,
            detail=f"Workout with id {workout_set.workout_id} not found",
        )
    session.add(db_workout_set)
    session.commit()
    session.refresh(db_workout_set)
    return db_workout_set


@router.get("/", response_model=list[FullSetRead])
def read_sets(
    *,
    session: Session = Depends(get_session),
    offset: int = 0,
    limit: int = Query(default=100, lte=100),
):
    return session.exec(
        select(Set).order_by(Set.id).offset(offset).limit(limit)
    ).all()


@router.get(
    "/{set_id}",
    response_model=FullSetRead,
)
def read_set(*, session: Session = Depends(get_session), set_id: int):
    if workout_set := session.get(Set, set_id):
        return workout_set
    else:
        raise HTTPException(status_code=404, detail="Set not found")


@router.delete("/{set_id}")
def delete_set(*, session: Session = Depends(get_session), set_id: int):
    workout_set = session.get(Set, set_id)
    if not workout_set:
        raise HTTPException(status_code=404, detail="Set not found")
    session.delete(workout_set)
    session.commit()
    return {"ok": True}


@router.patch("/{set_id}", response_model=FullSetRead)
def update_set(
    *,
    session: Session = Depends(get_session),
    set_id: int,
    workout_set: SetUpdate,
):
    set_db = session.get(Set, set_id)
    if not set_db:
        raise HTTPException(status_code=404, detail="Set not found")
    set_data = workout_set.dict(exclude_unset=True)
    for key, value in set_data.items():
        if key == "exercise_id" and not session.get(Exercise, value):
            raise HTTPException(
                status_code=404,
                detail=f"Exercise with id {value} not found",
            )
        if key == "workout_id" and not session.get(Workout, value):
            raise HTTPException(
                status_code=404,
                detail=f"Workout with id {value} not found",
            )
        setattr(set_db, key, value)
    session.add(set_db)
    session.commit()
    session.refresh(set_db)
    return set_db
