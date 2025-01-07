from typing import Annotated

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlmodel import Session, select

from app.db.models import (
    PlannedSet,
    PlannedSetCreate,
    PlannedSetRead,
    Exercise,
    WorkoutRoutine,
    RoutineExercise,
)
from app.dependencies import get_session
from app.auth import get_current_user, require_permission

router = APIRouter(
    prefix="/planned_sets",
    responses={404: {"description": "Not Found"}},
)


@router.post("/", response_model=PlannedSetRead)
@require_permission("create_all_planned_sets", "create_own_planned_sets")
def create_planned_set(
    *,
    session: Session = Depends(get_session),
    planned_set: PlannedSetCreate,
    current_user: Annotated[str, Depends(get_current_user)],
):
    if not session.get(Exercise, planned_set.exercise_id):
        raise HTTPException(
            status_code=404,
            detail=f"Exercise with id {planned_set.exercise_id} not found",
        )
    if not (
        workout_routine_db := session.get(WorkoutRoutine, planned_set.workoutroutine_id)
    ):
        raise HTTPException(
            status_code=404,
            detail=f"WorkoutRoutine with id \
                {planned_set.workoutroutine_id} not found",
        )
    if workout_routine_db.user_id != current_user.id and not current_user.has(
        "create_all_planned_sets"
    ):
        raise HTTPException(
            status_code=400,
            detail="User does not have permission to crate planned sets for another user",
        )
    # Try getting the routine exercise. If it doesn't exist, create it
    routine_exercise_db = session.exec(
        select(RoutineExercise)
        .where(RoutineExercise.exercise_id == planned_set.exercise_id)
        .where(RoutineExercise.routine_id == planned_set.workoutroutine_id)
    ).first()
    if not routine_exercise_db:
        routine_exercise_db = RoutineExercise(
            routine_id=planned_set.workoutroutine_id, exercise=planned_set.exercise_id
        )
        session.add(routine_exercise_db)
        session.commit()
        session.refresh(routine_exercise_db)
    planned_set_db = PlannedSet(
        reps=planned_set.reps, routine_exercise_id=routine_exercise_db.id
    )
    session.add(planned_set_db)
    session.commit()
    session.refresh(planned_set_db)
    return planned_set_db


@router.get("/", response_model=list[PlannedSetRead])
@require_permission("read_all_planned_sets", "read_own_planned_sets")
def read_planned_sets(
    *,
    session: Session = Depends(get_session),
    offset: int = 0,
    limit: int = Query(default=100, lte=100),
    exercise_id: int | None = None,
    workout_routine_id: int | None = None,
    user_id: int | None = None,
    current_user: Annotated[str, Depends(get_current_user)],
):
    if user_id != current_user.id and not current_user.has("read_all_planned_sets"):
        raise HTTPException(
            status_code=400,
            detail="User does not have permission to read planned sets of another user",
        )
    query = select(PlannedSet)
    if user_id:
        query = query.where(
            PlannedSet.routine_exercise.workout_routine.user_id == user_id
        )
    if exercise_id:
        query = query.where(PlannedSet.routine_exercise.exercise_id == exercise_id)
    if workout_routine_id:
        query = query.where(
            PlannedSet.routine_exercise.workout_routine_id == workout_routine_id
        )
    return session.exec(query.order_by(PlannedSet.id).offset(offset).limit(limit)).all()


@router.get(
    "/{planned_set_id}",
    response_model=PlannedSetRead,
)
@require_permission("read_all_planned_sets", "read_own_planned_sets")
def read_planned_set(
    *,
    session: Session = Depends(get_session),
    planned_set_id: int,
    current_user: Annotated[str, Depends(get_current_user)],
):
    if planned_set := session.get(PlannedSet, planned_set_id):
        if (
            planned_set.routine_exercise.workout_routine.user_id != current_user.id
            and not current_user.has("read_all_sets")
        ):
            raise HTTPException(
                status_code=400,
                detail="User does not have permission to read planned sets of another user",
            )
        return planned_set
    else:
        raise HTTPException(status_code=404, detail="PlannedSet not found")


@router.delete("/{planned_set_id}")
@require_permission("delete_all_planned_sets", "delete_own_planned_sets")
def delete_planned_set(
    *,
    session: Session = Depends(get_session),
    planned_set_id: int,
    current_user: Annotated[str, Depends(get_current_user)],
):
    planned_set = session.get(PlannedSet, planned_set_id)
    if not planned_set:
        raise HTTPException(status_code=404, detail="PlannedSet not found")
    if (
        planned_set.routine_exercise.workout_routine.user_id != current_user.id
        and not current_user.has("delete_all_planned_sets")
    ):
        raise HTTPException(
            status_code=400,
            detail="User does not have permission to delete planned sets of another user",
        )
    session.delete(planned_set)
    session.commit()
    return {"ok": True}


# @router.patch("/{planned_set_id}", response_model=PlannedSetRead)
# def update_planned_set(
#     *,
#     session: Session = Depends(get_session),
#     planned_set_id: int,
#     planned_set: PlannedSetUpdate,
# ):
#     planned_set_db = session.get(PlannedSet, planned_set_id)
#     if not planned_set_db:
#         raise HTTPException(status_code=404, detail="PlannedSet not found")
#     set_data = planned_set.dict(exclude_unset=True)
#     for key, value in set_data.items():
#         if key == "exercise_id" and not session.get(Exercise, value):
#             raise HTTPException(
#                 status_code=404,
#                 detail=f"Exercise with id {value} not found",
#             )
#         if key == "workoutroutine_id" and not session.get(WorkoutRoutine, value):
#             raise HTTPException(
#                 status_code=404,
#                 detail=f"WorkoutRoutine with id {value} not found",
#             )
#         setattr(planned_set_db, key, value)
#     session.add(planned_set_db)
#     session.commit()
#     session.refresh(planned_set_db)
#     return planned_set_db
