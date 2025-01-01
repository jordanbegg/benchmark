from typing import Annotated

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlmodel import Session, select

from app.db.models import (
    Exercise,
    ExerciseCreate,
    ExerciseRead,
    ExerciseReadWithMuscleGroups,
    ExerciseReadFull,
    ExerciseUpdate,
    MuscleGroup,
)
from app.dependencies import get_session
from app.auth import get_current_user, require_permission


router = APIRouter(
    prefix="/exercises",
    responses={404: {"description": "Not Found"}},
)


@router.post("/", response_model=ExerciseReadWithMuscleGroups)
@require_permission("create_exercise")
def create_exercise(
    *,
    session: Session = Depends(get_session),
    exercise: ExerciseCreate,
    current_user: Annotated[str, Depends(get_current_user)],
):
    if session.exec(
        select(Exercise).where(Exercise.name == exercise.name.lower())
    ).first():
        raise ValueError(f"Exercise named {exercise.name} already exists!")
    musclegroups = []
    for musclegroup_id in exercise.musclegroup_ids:
        if musclegroup := session.get(MuscleGroup, musclegroup_id):
            musclegroups.append(musclegroup)
    db_exercise = Exercise(name=exercise.name.lower(), musclegroups=musclegroups)
    session.add(db_exercise)
    session.commit()
    session.refresh(db_exercise)
    return db_exercise


@router.get("/", response_model=list[ExerciseRead])
@require_permission("read_exercise")
def read_exercises(
    *,
    session: Session = Depends(get_session),
    offset: int = 0,
    limit: int = Query(default=100, lte=100),
    current_user: Annotated[str, Depends(get_current_user)],
):
    return session.exec(
        select(Exercise).order_by(Exercise.id).offset(offset).limit(limit)
    ).all()


@router.get("/{exercise_id}", response_model=ExerciseReadFull)
@require_permission("read_exercise")
def read_exercise(
    *,
    session: Session = Depends(get_session),
    exercise_id: int,
    current_user: Annotated[str, Depends(get_current_user)],
):
    if exercise := session.get(Exercise, exercise_id):
        return exercise
    else:
        raise HTTPException(status_code=404, detail="Exercise not found")


@router.patch("/{exercise_id}", response_model=ExerciseReadWithMuscleGroups)
@require_permission("update_exercise")
def update_exercise(
    *,
    session: Session = Depends(get_session),
    exercise_id: int,
    exercise: ExerciseUpdate,
    current_user: Annotated[str, Depends(get_current_user)],
):
    db_exercise = session.get(Exercise, exercise_id)
    if not db_exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")

    exercise_data = exercise.dict(exclude_unset=True)
    for key, value in exercise_data.items():
        if key == "musclegroup_ids":
            musclegroups = []
            for musclegroup_id in value:
                if musclegroup := session.get(MuscleGroup, musclegroup_id):
                    musclegroups.append(musclegroup)
            db_exercise.musclegroups = musclegroups
        elif key == "name":
            if session.exec(
                select(Exercise).where(
                    Exercise.name == value.lower(),
                    Exercise.id != db_exercise.id,
                )
            ).first():
                raise ValueError(f"Exercise with name {value.lower()} already exists!")
            else:
                setattr(db_exercise, key, value.lower())
        else:
            setattr(db_exercise, key, value)
    session.add(db_exercise)
    session.commit()
    session.refresh(db_exercise)
    return db_exercise


@router.delete("/{exercise_id}")
@require_permission("delete_exercise")
def delete_exercise(
    *,
    session: Session = Depends(get_session),
    exercise_id: int,
    current_user: Annotated[str, Depends(get_current_user)],
):
    exercise = session.get(Exercise, exercise_id)
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")
    # Need to delete the routine exercises first
    for routine_exercise in exercise.routine_exercises:
        session.delete(routine_exercise)
        session.commit()
    for workout_exercise in exercise.workout_exercises:
        session.delete(workout_exercise)
        session.commit()
    session.delete(exercise)
    session.commit()
    return {"ok": True}
