from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from app.db.models import (
    Workout,
    WorkoutCreate,
    WorkoutRead,
    WorkoutsRead,
    WorkoutUpdate,
    Exercise,
    Set,
    WorkoutRoutine,
    WorkoutExercise
)
from app.dependencies import get_session


router = APIRouter(
    prefix="/workouts",
    responses={404: {"description": "Not Found"}},
)


def filter_sets(workout: Workout):
    workout_exercises = []
    for exercise in workout.exercises:
        exercise.sets = [
            workout_set
            for workout_set in exercise.sets
            if workout_set.workout_id == workout.id
        ]
        workout_exercises.append(exercise)
    workout.exercises = workout_exercises
    return workout


@router.post("/", response_model=WorkoutRead)
def create_workout(
    *,
    session: Session = Depends(get_session),
    workout: WorkoutCreate,
):
    workout_db = Workout(
        workoutroutine_id=workout.workoutroutine_id, date=workout.date
    )
    if not (
        workout_routine_db := session.get(
            WorkoutRoutine, workout.workoutroutine_id
        )
    ):
        raise HTTPException(
            status_code=404,
            detail=f"Workout Routine with id {workout.workoutroutine_id}\
                not found",
        )
    session.add(workout_db)
    session.commit()
    session.refresh(workout_db)
    for exercise in workout.exercises:
        if not (exercise_db := session.get(Exercise, exercise.id)):
            raise HTTPException(
                status_code=404,
                detail=f"Exercise with id {exercise.id} not found",
            )
        workout_exercise_db = WorkoutExercise(
            workout=workout_db, exercise=exercise_db
        )
        session.add(workout_exercise_db)
        session.commit()
        session.refresh(workout_exercise_db)
        for workout_set in exercise.sets:
            set_db = Set(
                reps=workout_set.reps,
                weight=workout_set.weight,
                workout_exercise=workout_exercise_db
            )
            session.add(set_db)
    session.add(workout_db)
    session.commit()
    session.refresh(workout_db)
    return workout_db


@router.get("/", response_model=list[WorkoutsRead])
def read_workouts(
    *,
    session: Session = Depends(get_session),
    offset: int = 0,
    limit: int = Query(default=100, lte=100),
):
    return session.exec(select(Workout).order_by(Workout.id).offset(offset).limit(limit)).all()


@router.get(
    "/{workout_id}",
    response_model=WorkoutRead,
)
def read_workout(*, session: Session = Depends(get_session), workout_id: int):
    if workout := session.get(Workout, workout_id):
        return workout
    else:
        raise HTTPException(status_code=404, detail="Workout not found")


@router.delete("/{workout_id}")
def delete_workout(
    *, session: Session = Depends(get_session), workout_id: int
):
    workout = session.get(Workout, workout_id)
    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")
    for workout_exercise in workout.workout_exercises:
        for set_db in workout_exercise.sets:
            session.delete(set_db)
        session.delete(workout_exercise)
    session.delete(workout)
    session.commit()
    return {"ok": True}


@router.patch("/{workout_id}", response_model=WorkoutRead)
def update_workout(
    *,
    session: Session = Depends(get_session),
    workout_id: int,
    workout: WorkoutUpdate,
):
    workout_db = session.get(Workout, workout_id)
    if not workout_db:
        raise HTTPException(
            status_code=404,
            detail=f"Workout with id {workout_id} not found",
        )

    if not workout.workoutroutine_id:
        workout.workoutroutine_id = workout_db.workoutroutine_id

    workout_data = workout.dict(exclude_unset=True)
    for key, value in workout_data.items():
        if key == "exercises":
            workout_db.exercises = []
            if not (
                workout_routine_db := session.get(
                    WorkoutRoutine, workout.workoutroutine_id
                )
            ):
                raise HTTPException(
                    status_code=404,
                    detail=f"Workout Routine with id \
                        {workout.workoutroutine_id} not found",
                )
            routine_exercises = session.get(
                WorkoutRoutine, workout.workoutroutine_id
            ).exercises
            routine_exercises = workout_routine_db.exercises
            for exercise in value:
                if not (exercise_db := session.get(Exercise, exercise["id"])):
                    raise HTTPException(
                        status_code=404,
                        detail=f"Exercise with id {exercise['id']} not found",
                    )
                if exercise_db not in routine_exercises:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Exercise with id {exercise['id']} not found in\
                            routine with id {workout.workoutroutine_id}",
                    )
                if "sets" in exercise:
                    # Delete all existing planned sets
                    for exising_set_db in exercise_db.sets:
                        session.delete(exising_set_db)
                    # Add new sets
                    for workout_set in exercise["sets"]:
                        set_db = Set(
                            reps=workout_set["reps"],
                            weight=workout_set["weight"],
                            exercise=exercise_db,
                            workout=workout_db,
                        )
                        session.add(set_db)
                workout_db.exercises.append(exercise_db)
        else:
            setattr(workout_db, key, value)
    session.add(workout_db)
    session.commit()
    session.refresh(workout_db)

    # Filter for the sake of the response model but don't update db
    workout_db = filter_sets(workout_db)
    return workout_db
