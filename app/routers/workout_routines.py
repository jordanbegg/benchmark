from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from app.db.models import (
    WorkoutRoutine,
    WorkoutRoutineCreate,
    WorkoutRoutineRead,
    WorkoutRoutineUpdate,
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
    for exercise in workout_routine.exercises:
        if not (exercise_db := session.get(Exercise, exercise.id)):
            raise HTTPException(
                status_code=404,
                detail=f"Exercise with id {exercise.id} not found",
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
        session.add(exercise_db)
        exercises.append(exercise_db)
    workout_routine_db.exercises = exercises
    session.add(workout_routine_db)
    session.commit()
    session.refresh(workout_routine_db)
    return workout_routine_db


@router.get("/", response_model=list[WorkoutRoutineRead])
def read_workout_routines(
    *,
    session: Session = Depends(get_session),
    offset: int = 0,
    limit: int = Query(default=100, lte=100),
):
    return session.exec(
        select(WorkoutRoutine).offset(offset).limit(limit)
    ).all()


@router.get(
    "/{workoutroutine_id}",
    response_model=WorkoutRoutineRead,
)
def read_workout_routine(
    *, session: Session = Depends(get_session), workoutroutine_id: int
):
    if workout_routine := session.get(WorkoutRoutine, workoutroutine_id):
        return workout_routine
    else:
        raise HTTPException(status_code=404, detail="WorkoutRoutine not found")


@router.delete("/{workout_routine_id}")
def delete_workout_routine(
    *, session: Session = Depends(get_session), workout_routine_id: int
):
    workout_routine = session.get(WorkoutRoutine, workout_routine_id)
    if not workout_routine:
        raise HTTPException(
            status_code=404, detail="Workout Routine not found"
        )
    sets = []
    for exercise in workout_routine.exercises:
        sets.extend(exercise.sets)
    for set_db in sets:
        session.delete(set_db)
    session.delete(workout_routine)
    session.commit()
    return {"ok": True}


@router.patch("/{workout_routine_id}", response_model=WorkoutRoutineRead)
def update_workout_routine(
    *,
    session: Session = Depends(get_session),
    workout_routine_id: int,
    workout_routine: WorkoutRoutineUpdate,
):
    db_workout_routine = session.get(WorkoutRoutine, workout_routine_id)
    if not db_workout_routine:
        raise HTTPException(
            status_code=404,
            detail=f"Workout Routine with id {workout_routine_id} not found",
        )

    workout_routine_data = workout_routine.dict(exclude_unset=True)
    for key, value in workout_routine_data.items():
        if key == "exercises":
            exercises = []
            for exercise in value:
                if not (exercise_db := session.get(Exercise, exercise["id"])):
                    raise HTTPException(
                        status_code=404,
                        detail=f"Exercise with id {exercise['id']} not found",
                    )
                if "sets" in exercise:
                    # Delete all existing planned sets
                    for exising_set_db in exercise_db.sets:
                        session.delete(exising_set_db)
                    # Add new sets
                    exercise_sets = []
                    for planned_set in exercise["sets"]:
                        set_db = Set(
                            reps=planned_set["reps"],
                            is_actual=False,
                            exercise_id=exercise_db.id,
                        )
                        exercise_sets.append(set_db)
                    if exercise_sets:
                        exercise_db.sets = exercise_sets
                    session.add(exercise_db)
                    exercises.append(exercise_db)
            db_workout_routine.exercises = exercises
        else:
            setattr(db_workout_routine, key, value)
    session.add(db_workout_routine)
    session.commit()
    session.refresh(db_workout_routine)
    return db_workout_routine
