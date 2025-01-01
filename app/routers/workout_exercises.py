from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from app.db.models import (
    WorkoutExercise,
    WorkoutExerciseCreate,
    WorkoutExerciseRead,
    Workout,
    Exercise,
)
from app.dependencies import get_session
from app.auth import get_current_user, require_permission


router = APIRouter(
    prefix="/workout_exercises",
    responses={404: {"description": "Not Found"}},
)


@router.post("/", response_model=WorkoutExerciseRead)
@require_permission("create_all_workout_exercises", "create_own_workout_exercise")
def create_workout_exercise(
    *,
    session: Session = Depends(get_session),
    workout_exercise: WorkoutExerciseCreate,
    current_user: Annotated[str, Depends(get_current_user)],
):
    workout_user_id = session.get(Workout, workout_exercise.workout_id).user_id
    if workout_user_id != current_user.id and not current_user.has(
        "create_all_workout_exercises"
    ):
        raise HTTPException(
            status_code=400,
            detail="User does not have permission to create workout exercises for another user",
        )
    workout_exercise_db = WorkoutExercise(
        workout_id=workout_exercise.workout_id, exercise_id=workout_exercise.exercise_id
    )
    if not (session.get(Workout, workout_exercise.workout_id)):
        raise HTTPException(
            status_code=404,
            detail=f"Workout with id {workout_exercise.workout_id}\
                not found",
        )
    if not (session.get(Exercise, workout_exercise.exercise_id)):
        raise HTTPException(
            status_code=404,
            detail=f"Exercise with id {workout_exercise.exercise_id}\
                not found",
        )
    session.add(workout_exercise_db)
    session.commit()
    session.refresh(workout_exercise_db)
    return workout_exercise_db


@router.get("/", response_model=list[WorkoutExerciseRead])
@require_permission("read_all_workout_exercises", "read_own_workout_exercise")
def read_workout_exercises(
    *,
    session: Session = Depends(get_session),
    offset: int = 0,
    limit: int = Query(default=100, lte=100),
    exercise_id: int | None = None,
    workout_id: int | None = None,
    user_id: int | None = None,
    current_user: Annotated[str, Depends(get_current_user)],
):
    if user_id != current_user.id and not current_user.has(
        "read_all_workout_exercises"
    ):
        raise HTTPException(
            status_code=400,
            detail="User does not have permission to read workout exercises of another user",
        )
    query = select(WorkoutExercise)
    if exercise_id:
        query = query.where(WorkoutExercise.exercise_id == exercise_id)
    if workout_id:
        query = query.where(WorkoutExercise.workout_id == workout_id)
    if user_id:
        query = query.join(Workout, WorkoutExercise.workout_id == Workout.id).where(
            Workout.user_id == user_id
        )
    return session.exec(
        query.order_by(WorkoutExercise.id).offset(offset).limit(limit)
    ).all()


@router.get(
    "/{workout_exercise_id}",
    response_model=WorkoutExerciseRead,
)
@require_permission("read_all_workout_exercises", "read_own_workout_exercise")
def read_workout_exercise(
    *,
    session: Session = Depends(get_session),
    workout_exercise_id: int,
    current_user: Annotated[str, Depends(get_current_user)],
):
    if workout_exercise := session.get(WorkoutExercise, workout_exercise_id):
        if workout_exercise.workout.user_id != current_user.id and not current_user.has(
            "read_all_workout_exercises"
        ):
            raise HTTPException(
                status_code=400,
                detail="User does not have permission to read workout exercises of another user",
            )
        return workout_exercise
    else:
        raise HTTPException(status_code=404, detail="Workout Exercise not found")


# @router.delete("/{workout_id}")
# def delete_workout(
#     *, session: Session = Depends(get_session), workout_id: int
# ):
#     workout = session.get(Workout, workout_id)
#     if not workout:
#         raise HTTPException(status_code=404, detail="Workout not found")
#     for workout_exercise in workout.workout_exercises:
#         for set_db in workout_exercise.sets:
#             session.delete(set_db)
#         session.delete(workout_exercise)
#     session.delete(workout)
#     session.commit()
#     return {"ok": True}


# Need to check that it's working

# @router.patch("/{workout_id}", response_model=WorkoutRead)
# def update_workout(
#     *,
#     session: Session = Depends(get_session),
#     workout_id: int,
#     workout: WorkoutUpdate,
# ):
#     workout_db = session.get(Workout, workout_id)
#     if not workout_db:
#         raise HTTPException(
#             status_code=404,
#             detail=f"Workout with id {workout_id} not found",
#         )

#     if not workout.workoutroutine_id:
#         workout.workoutroutine_id = workout_db.workoutroutine_id

#     workout_data = workout.dict(exclude_unset=True)
#     for key, value in workout_data.items():
#         if key == "exercises":
#             workout_db.exercises = []
#             if not (
#                 workout_routine_db := session.get(
#                     WorkoutRoutine, workout.workoutroutine_id
#                 )
#             ):
#                 raise HTTPException(
#                     status_code=404,
#                     detail=f"Workout Routine with id \
#                         {workout.workoutroutine_id} not found",
#                 )
#             routine_exercises = session.get(
#                 WorkoutRoutine, workout.workoutroutine_id
#             ).exercises
#             routine_exercises = workout_routine_db.exercises
#             for exercise in value:
#                 if not (exercise_db := session.get(Exercise, exercise["id"])):
#                     raise HTTPException(
#                         status_code=404,
#                         detail=f"Exercise with id {exercise['id']} not found",
#                     )
#                 if exercise_db not in routine_exercises:
#                     raise HTTPException(
#                         status_code=404,
#                         detail=f"Exercise with id {exercise['id']} not found in\
#                             routine with id {workout.workoutroutine_id}",
#                     )
#                 if "sets" in exercise:
#                     # Delete all existing planned sets
#                     for exising_set_db in exercise_db.sets:
#                         session.delete(exising_set_db)
#                     # Add new sets
#                     for workout_set in exercise["sets"]:
#                         set_db = Set(
#                             reps=workout_set["reps"],
#                             weight=workout_set["weight"],
#                             exercise=exercise_db,
#                             workout=workout_db,
#                         )
#                         session.add(set_db)
#                 workout_db.exercises.append(exercise_db)
#         else:
#             setattr(workout_db, key, value)
#     session.add(workout_db)
#     session.commit()
#     session.refresh(workout_db)

#     # Filter for the sake of the response model but don't update db
#     workout_db = filter_sets(workout_db)
#     return workout_db
