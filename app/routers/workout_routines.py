from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from app.db.models import (
    WorkoutRoutine,
    WorkoutRoutineCreate,
    WorkoutRoutineRead,
    WorkoutRoutinesRead,
    WorkoutRoutineUpdate,
    Exercise,
    PlannedSet,
)
from dependencies import get_session


router = APIRouter(
    prefix="/workout_routines",
    responses={404: {"description": "Not Found"}},
)


def filter_sets(workout_routine: WorkoutRoutine):
    routine_exercises = []
    for exercise in workout_routine.exercises:
        exercise.planned_sets = [
            planned_set
            for planned_set in exercise.planned_sets
            if planned_set.workoutroutine_id == workout_routine.id
        ]
        routine_exercises.append(exercise)
    workout_routine.exercises = routine_exercises
    return workout_routine


@router.post("/", response_model=WorkoutRoutineRead)
def create_workout_routine(
    *,
    session: Session = Depends(get_session),
    workout_routine: WorkoutRoutineCreate,
):
    workout_routine_db = WorkoutRoutine(name=workout_routine.name)
    for exercise in workout_routine.exercises:
        if not (exercise_db := session.get(Exercise, exercise.id)):
            raise HTTPException(
                status_code=404,
                detail=f"Exercise with id {exercise.id} not found",
            )
        for planned_set in exercise.planned_sets:
            set_db = PlannedSet(
                reps=planned_set.reps,
                exercise=exercise_db,
                workoutroutine=workout_routine_db,
            )
            session.add(set_db)
        workout_routine_db.exercises.append(exercise_db)
    session.add(workout_routine_db)
    session.commit()
    session.refresh(workout_routine_db)

    # Filter for the sake of the response model but don't update db
    workout_routine_db = filter_sets(workout_routine_db)
    return workout_routine_db


@router.get("/", response_model=list[WorkoutRoutinesRead])
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
    for set_db in workout_routine.planned_sets:
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
    workout_routine_db = session.get(WorkoutRoutine, workout_routine_id)
    if not workout_routine_db:
        raise HTTPException(
            status_code=404,
            detail=f"Workout Routine with id {workout_routine_id} not found",
        )

    workout_routine_data = workout_routine.dict(exclude_unset=True)
    for key, value in workout_routine_data.items():
        if key == "exercises":
            workout_routine_db.exercises = []
            for exercise in value:
                if not (exercise_db := session.get(Exercise, exercise["id"])):
                    raise HTTPException(
                        status_code=404,
                        detail=f"Exercise with id {exercise['id']} not found",
                    )
                if "planned_sets" in exercise:
                    # Delete all existing planned sets
                    for exising_planned_set_db in exercise_db.planned_sets:
                        session.delete(exising_planned_set_db)
                    # Add new sets
                    for planned_set in exercise["planned_sets"]:
                        set_db = PlannedSet(
                            reps=planned_set["reps"],
                            exercise=exercise_db,
                            workoutroutine=workout_routine_db,
                        )
                        session.add(set_db)
                workout_routine_db.exercises.append(exercise_db)
        else:
            setattr(workout_routine_db, key, value)
    session.add(workout_routine_db)
    session.commit()
    session.refresh(workout_routine_db)
    return workout_routine_db
