from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.db.models import (
    WorkoutRoutine,
    WorkoutRoutineCreate,
    WorkoutRoutineRead,
    Exercise,
    Set,
)
from dependencies import get_session


router = APIRouter(
    prefix="/workout_routines",
    responses={404: {"description": "Not Found"}},
)


@router.post("/", response_model=WorkoutRoutineRead)
def create_workout_routine(
    *,
    session: Session = Depends(get_session),
    workout_routine: WorkoutRoutineCreate,
):
    workout_routine_db = WorkoutRoutine(name=workout_routine.name)
    exercises = []
    sets = []
    for exercise in workout_routine.exercises:
        if not (
            exercise_db := session.exec(
                select(Exercise).where(Exercise.name == exercise.name)
            ).one()
        ):
            raise HTTPException(
                status_code=404, detail=f"Exercise '{exercise.name}' not found"
            )
        exercise_sets = []
        for planned_set in exercise.sets:
            set_db = Set(
                reps=planned_set.reps,
                is_actual=False,
                exercise_id=exercise_db.id,
            )
            exercise_sets.append(set_db)
        if exercise_sets:
            exercise_db.sets = exercise_sets
            sets.extend(exercise_sets)
        session.add(exercise_db)
        exercises.append(exercise_db)
    workout_routine_db.exercises = exercises
    session.add(workout_routine_db)
    session.commit()
    session.refresh(workout_routine_db)
    return workout_routine_db
