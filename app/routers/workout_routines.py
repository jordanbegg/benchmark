from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from app.db.models import (
    WorkoutRoutine,
    WorkoutRoutineCreate,
    WorkoutRoutineRead,
    WorkoutRoutinesRead,
    Exercise,
    PlannedSet,
    RoutineExercise,
)
from app.dependencies import get_session
from app.auth import get_current_user, require_permission


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
@require_permission("create_all_workout_routines", "create_own_workout_routine")
def create_workout_routine(
    *,
    session: Session = Depends(get_session),
    workout_routine: WorkoutRoutineCreate,
    current_user: Annotated[str, Depends(get_current_user)],
):
    if workout_routine.user_id != current_user.id and not current_user.has(
        "create_all_workout_routines"
    ):
        raise HTTPException(
            status_code=400,
            detail="User does not have permission to create workout routines for another user",
        )
    if session.exec(
        select(WorkoutRoutine)
        .where(WorkoutRoutine.name == workout_routine.name.lower())
        .where(WorkoutRoutine.user_id == workout_routine.user_id)
    ).first():
        raise ValueError(
            f"WorkoutRoutine named {workout_routine.name.lower()} \
            already exists for user {workout_routine.user_id}!"
        )
    workout_routine_db = WorkoutRoutine(
        name=workout_routine.name.lower(), user_id=workout_routine.user_id
    )
    session.add(workout_routine_db)
    session.commit()
    session.refresh(workout_routine_db)
    for exercise in workout_routine.exercises:
        if not (exercise_db := session.get(Exercise, exercise.id)):
            raise HTTPException(
                status_code=404,
                detail=f"Exercise with id {exercise.id} not found",
            )
        routine_exercise_db = RoutineExercise(
            workout_routine=workout_routine_db, exercise=exercise_db
        )
        session.add(routine_exercise_db)
        session.commit()
        session.refresh(routine_exercise_db)
        for planned_set in exercise.planned_sets:
            set_db = PlannedSet(
                reps=planned_set.reps, routine_exercise=routine_exercise_db
            )
            session.add(set_db)
    session.add(workout_routine_db)
    session.commit()
    session.refresh(workout_routine_db)

    return workout_routine_db


@router.get("/", response_model=list[WorkoutRoutinesRead])
@require_permission("read_all_workout_routines", "read_own_workout_routine")
def read_workout_routines(
    *,
    session: Session = Depends(get_session),
    offset: int = 0,
    limit: int = Query(default=100, lte=100),
    user_id: int = None,
    current_user: Annotated[str, Depends(get_current_user)],
):
    if user_id != current_user.id and not current_user.has("read_all_workout_routines"):
        raise HTTPException(
            status_code=400,
            detail="User does not have permission to read workout routines of another user",
        )
    query = select(WorkoutRoutine)
    if user_id:
        query = query.where(WorkoutRoutine.user_id == user_id)
    return session.exec(
        query.order_by(WorkoutRoutine.id).offset(offset).limit(limit)
    ).all()


@router.get(
    "/{workoutroutine_id}",
    response_model=WorkoutRoutineRead,
)
@require_permission("read_all_workout_routines", "read_own_workout_routine")
def read_workout_routine(
    *,
    session: Session = Depends(get_session),
    workoutroutine_id: int,
    current_user: Annotated[str, Depends(get_current_user)],
):
    if workout_routine := session.get(WorkoutRoutine, workoutroutine_id):
        if workout_routine.user_id != current_user.id and not current_user.has(
            "read_all_workout_routines"
        ):
            raise HTTPException(
                status_code=400,
                detail="User does not have permission to read workout routines of another user",
            )
        return workout_routine
    else:
        raise HTTPException(status_code=404, detail="WorkoutRoutine not found")


@router.delete("/{workout_routine_id}")
@require_permission("delete_all_workouts", "delete_own_workout")
def delete_workout_routine(
    *,
    session: Session = Depends(get_session),
    workoutroutine_id: int,
    current_user: Annotated[str, Depends(get_current_user)],
):
    workout_routine = session.get(WorkoutRoutine, workoutroutine_id)
    if not workout_routine:
        raise HTTPException(status_code=404, detail="Workout Routine not found")
    if workout_routine.user_id != current_user.id and not current_user.has(
        "delete_all_workout_routines"
    ):
        raise HTTPException(
            status_code=400,
            detail="User does not have permission to delete workout routines of another user",
        )
    for routine_exercise in workout_routine.routine_exercises:
        for planned_set in routine_exercise.planned_sets:
            session.delete(planned_set)
        session.delete(routine_exercise)
    for workout in workout_routine.workouts:
        for workout_exercise in workout.workout_exercises:
            session.delete(workout_exercise)
        session.delete(workout)
    session.delete(workout_routine)
    session.commit()
    return {"ok": True}


# Not working
# @router.patch("/{workout_routine_id}", response_model=WorkoutRoutineRead)
# def update_workout_routine(
#     *,
#     session: Session = Depends(get_session),
#     workout_routine_id: int,
#     workout_routine: WorkoutRoutineUpdate,
# ):
#     workout_routine_db = session.get(WorkoutRoutine, workout_routine_id)
#     if not workout_routine_db:
#         raise HTTPException(
#             status_code=404,
#             detail=f"Workout Routine with id {workout_routine_id} not found",
#         )

#     workout_routine_data = workout_routine.dict(exclude_unset=True)
#     for key, value in workout_routine_data.items():
#         if key == "exercises":
#             for exercise in value:
#                 if not (exercise_db := session.get(Exercise, exercise["id"])):
#                     raise HTTPException(
#                         status_code=404,
#                         detail=f"Exercise with id {exercise['id']} not found",
#                     )
#                 routine_exercise_db = session.exec(
#                     select(RoutineExercise).where(
#                         WorkoutRoutine.id == workout_routine_id
#                     ).where(
#                         Exercise.id == exercise_db.id
#                     )
#                 ).first()
#                 if not routine_exercise_db:
#                     routine_exercise_db = RoutineExercise(
#             workout_routine=workout_routine_db, exercise=exercise_db
#         )
#                 session.add(routine_exercise_db)
#                 session.commit()
#                 session.refresh(routine_exercise_db)
#                 if "planned_sets" in exercise:
#                     for exising_planned_set_db in routine_exercise_db.planned_sets:
#                         session.delete(exising_planned_set_db)
#                         session.commit()
#                         session.refresh(routine_exercise_db)
#                     # Add new sets
#                     for planned_set in exercise["planned_sets"]:
#                         set_db = PlannedSet(
#                             reps=planned_set["reps"],
#                             routine_exercise=routine_exercise_db,
#                         )
#                         session.add(set_db)
#                         session.commit()
#                         session.refresh(set_db)
#         elif key == "name":
#             if session.exec(
#                 select(WorkoutRoutine).where(
#                     WorkoutRoutine.name == value.lower(),
#                     WorkoutRoutine.id != workout_routine_db.id,
#                 )
#             ).first():
#                 raise ValueError(
#                     f"WorkoutRoutine with name {value.lower()} already exists!"
#                 )
#             else:
#                 setattr(workout_routine_db, key, value.lower())
#         else:
#             setattr(workout_routine_db, key, value)
#     print("\n\n\n")
#     print(workout_routine_db.routine_exercises[0].planned_sets)
#     print(type(workout_routine_db))
#     session.add(workout_routine_db)
#     session.commit()
#     session.refresh(workout_routine_db)

#     return workout_routine_db
