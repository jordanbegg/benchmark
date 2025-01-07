from typing import Annotated

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlmodel import Session, select

from app.db.models import (
    Set,
    SetCreate,
    SetRead,
    Exercise,
    Workout,
    WorkoutExercise,
)
from app.dependencies import get_session
from app.auth import get_current_user, require_permission

router = APIRouter(
    prefix="/sets",
    responses={404: {"description": "Not Found"}},
)


@router.post("/", response_model=SetRead)
@require_permission("create_all_sets", "create_own_sets")
def create_set(
    *,
    session: Session = Depends(get_session),
    workout_set: SetCreate,
    current_user: Annotated[str, Depends(get_current_user)],
):
    if not session.get(Exercise, workout_set.exercise_id):
        raise HTTPException(
            status_code=404,
            detail=f"Exercise with id {workout_set.exercise_id} not found",
        )
    if not (workout_db := session.get(Workout, workout_set.workout_id)):
        raise HTTPException(
            status_code=404,
            detail=f"Workout with id \
                {workout_set.workout_id} not found",
        )
    if workout_db.user_id != current_user.id and not current_user.has(
        "create_all_sets"
    ):
        raise HTTPException(
            status_code=400,
            detail="User does not have permission to create sets for another user",
        )
    # Try getting the routine exercise. If it doesn't exist, create it
    workout_exercise_db = session.exec(
        select(WorkoutExercise)
        .where(WorkoutExercise.exercise_id == workout_set.exercise_id)
        .where(WorkoutExercise.workout_id == workout_set.workout_id)
    ).first()
    if not workout_exercise_db:
        workout_exercise_db = WorkoutExercise(
            workout_id=workout_set.workout_id, exercise=workout_set.exercise_id
        )
        session.add(workout_exercise_db)
        session.commit()
        session.refresh(workout_exercise_db)
    workout_set_db = Set(
        reps=workout_set.reps,
        weight=workout_set.weight,
        workout_exercise_id=workout_exercise_db.id,
    )
    session.add(workout_set_db)
    session.commit()
    session.refresh(workout_set_db)
    return workout_set_db


@router.get("/", response_model=list[SetRead])
@require_permission("read_all_planned_sets", "read_own_planned_sets")
def read_sets(
    *,
    session: Session = Depends(get_session),
    offset: int = 0,
    limit: int = Query(default=100, lte=100),
    exercise_id: int | None = None,
    workout_id: int | None = None,
    user_id: int | None = None,
    current_user: Annotated[str, Depends(get_current_user)],
):
    if user_id != current_user.id and not current_user.has("read_all_sets"):
        raise HTTPException(
            status_code=400,
            detail="User does not have permission to read sets of another user",
        )
    query = select(Set)
    if user_id:
        query = query.where(Set.workout_exercise.workout.user_id == user_id)
    if exercise_id:
        query = query.where(Set.workout_exercise.exercise_id == exercise_id)
    if workout_id:
        query = query.where(Set.workout_exercise.workout_id == workout_id)
    return session.exec(query.order_by(Set.id).offset(offset).limit(limit)).all()


@router.get(
    "/{set_id}",
    response_model=SetRead,
)
@require_permission("read_all_sets", "read_own_sets")
def read_set(
    *,
    session: Session = Depends(get_session),
    set_id: int,
    current_user: Annotated[str, Depends(get_current_user)],
):
    if workout_set := session.get(Set, set_id):
        if (
            workout_set.workout_exercise.workout.user_id != current_user.id
            and not current_user.has("read_all_sets")
        ):
            raise HTTPException(
                status_code=400,
                detail="User does not have permission to read sets of another user",
            )
        return workout_set
    else:
        raise HTTPException(status_code=404, detail="Set not found")


@router.delete("/{set_id}")
@require_permission("delete_all_sets", "delete_own_sets")
def delete_set(
    *,
    session: Session = Depends(get_session),
    set_id: int,
    current_user: Annotated[str, Depends(get_current_user)],
):
    workout_set = session.get(Set, set_id)
    if not workout_set:
        raise HTTPException(status_code=404, detail="Set not found")
    if (
        workout_set.workout_exercise.workout.user_id != current_user.id
        and not current_user.has("delete_all_sets")
    ):
        raise HTTPException(
            status_code=400,
            detail="User does not have permission to delete sets of another user",
        )
    session.delete(workout_set)
    session.commit()
    return {"ok": True}


# @router.patch("/{set_id}", response_model=SetRead)
# def update_set(
#     *,
#     session: Session = Depends(get_session),
#     set_id: int,
#     workout_set: SetUpdate,
# ):
#     set_db = session.get(Set, set_id)
#     if not set_db:
#         raise HTTPException(status_code=404, detail="Set not found")
#     set_data = workout_set.dict(exclude_unset=True)
#     for key, value in set_data.items():
#         if key == "exercise_id" and not session.get(Exercise, value):
#             raise HTTPException(
#                 status_code=404,
#                 detail=f"Exercise with id {value} not found",
#             )
#         if key == "workout_id" and not session.get(Workout, value):
#             raise HTTPException(
#                 status_code=404,
#                 detail=f"Workout with id {value} not found",
#             )
#         setattr(set_db, key, value)
#     session.add(set_db)
#     session.commit()
#     session.refresh(set_db)
#     return set_db
