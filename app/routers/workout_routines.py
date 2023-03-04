from fastapi import APIRouter, Depends, Query, HTTPException
from sqlmodel import Session, select

from app.db.models import (
    WorkoutRoutine,
    WorkoutRoutineCreate,
    WorkoutRoutineRead,
    Exercise,
    Set,
    ExerciseRead,
    ExerciseCreate,
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


# @router.get("/", response_model=list[ExerciseRead])
# def read_exercises(
#     *,
#     session: Session = Depends(get_session),
#     offset: int = 0,
#     limit: int = Query(default=100, lte=100),
# ):
#     return session.exec(select(Exercise).offset(offset).limit(limit)).all()


# @router.get("/{exercise_id}", response_model=ExerciseReadWithMuscleGroups)
# def read_exercise(*, session: Session = Depends(get_session), exercise_id: int):
#     if exercise := session.get(Exercise, exercise_id):
#         return exercise
#     else:
#         raise HTTPException(status_code=404, detail="Exercise not found")


# @router.patch("/{exercise_id}", response_model=ExerciseReadWithMuscleGroups)
# def update_exercise(
#     *,
#     session: Session = Depends(get_session),
#     exercise_id: int,
#     exercise: ExerciseUpdate,
# ):
#     db_exercise = session.get(Exercise, exercise_id)
#     if not db_exercise:
#         raise HTTPException(status_code=404, detail="Exercise not found")

#     exercise_data = exercise.dict(exclude_unset=True)
#     for key, value in exercise_data.items():
#         if key == "musclegroup_ids":
#             musclegroups = []
#             for musclegroup_id in value:
#                 if musclegroup := session.get(MuscleGroup, musclegroup_id):
#                     musclegroups.append(musclegroup)
#             db_exercise.musclegroups = musclegroups
#         else:
#             setattr(db_exercise, key, value)
#     session.add(db_exercise)
#     session.commit()
#     session.refresh(db_exercise)
#     return db_exercise


# @router.delete("/{exercise_id}")
# def delete_exercise(*, session: Session = Depends(get_session), exercise_id: int):
#     exercise = session.get(Exercise, exercise_id)
#     if not exercise:
#         raise HTTPException(status_code=404, detail="Exercise not found")
#     session.delete(exercise)
#     session.commit()
#     return {"ok": True}
