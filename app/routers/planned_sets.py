from fastapi import APIRouter, Depends, Query, HTTPException
from sqlmodel import Session, select

from app.db.models import (
    PlannedSet,
    PlannedSetCreate,
    FullPlannedSetRead,
    PlannedSetUpdate,
    Exercise,
    WorkoutRoutine,
)
from dependencies import get_session

router = APIRouter(
    prefix="/planned_sets",
    responses={404: {"description": "Not Found"}},
)


@router.post("/", response_model=FullPlannedSetRead)
def create_planned_set(
    *, session: Session = Depends(get_session), planned_set: PlannedSetCreate
):
    planned_set_db = PlannedSet.from_orm(planned_set)
    if not session.get(Exercise, planned_set.exercise_id):
        raise HTTPException(
            status_code=404,
            detail=f"Exercise with id {planned_set.exercise_id} not found",
        )
    if not session.get(WorkoutRoutine, planned_set.workoutroutine_id):
        raise HTTPException(
            status_code=404,
            detail=f"WorkoutRoutine with id \
                {planned_set.workoutroutine_id} not found",
        )
    session.add(planned_set_db)
    session.commit()
    session.refresh(planned_set_db)
    return planned_set_db


@router.get("/", response_model=list[FullPlannedSetRead])
def read_planned_sets(
    *,
    session: Session = Depends(get_session),
    offset: int = 0,
    limit: int = Query(default=100, lte=100),
):
    return session.exec(select(PlannedSet).offset(offset).limit(limit)).all()


@router.get(
    "/{planned_set_id}",
    response_model=FullPlannedSetRead,
)
def read_planned_set(
    *, session: Session = Depends(get_session), planned_set_id: int
):
    if workout_set := session.get(PlannedSet, planned_set_id):
        return workout_set
    else:
        raise HTTPException(status_code=404, detail="PlannedSet not found")


@router.delete("/{planned_set_id}")
def delete_set(
    *, session: Session = Depends(get_session), planned_set_id: int
):
    planned_set = session.get(PlannedSet, planned_set_id)
    if not planned_set:
        raise HTTPException(status_code=404, detail="PlannedSet not found")
    session.delete(planned_set)
    session.commit()
    return {"ok": True}


@router.patch("/{planned_set_id}", response_model=FullPlannedSetRead)
def update_set(
    *,
    session: Session = Depends(get_session),
    planned_set_id: int,
    planned_set: PlannedSetUpdate,
):
    planned_set_db = session.get(PlannedSet, planned_set_id)
    if not planned_set_db:
        raise HTTPException(status_code=404, detail="PlannedSet not found")
    set_data = planned_set.dict(exclude_unset=True)
    for key, value in set_data.items():
        if key == "exercise_id" and not session.get(Exercise, value):
            raise HTTPException(
                status_code=404,
                detail=f"Exercise with id {value} not found",
            )
        if key == "workoutroutine_id" and not session.get(
            WorkoutRoutine, value
        ):
            raise HTTPException(
                status_code=404,
                detail=f"WorkoutRoutine with id {value} not found",
            )
        setattr(planned_set_db, key, value)
    session.add(planned_set_db)
    session.commit()
    session.refresh(planned_set_db)
    return planned_set_db
