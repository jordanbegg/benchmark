from fastapi import FastAPI

from app.routers import (
    exercises,
    musclegroups,
    workout_routines,
    workouts,
    sets,
    planned_sets,
    users,
    weights,
    auth,
    workout_exercises,
    roles,
    permissions,
)

app = FastAPI()

app.include_router(exercises.router)
app.include_router(musclegroups.router)
app.include_router(workout_routines.router)
app.include_router(workouts.router)
app.include_router(sets.router)
app.include_router(planned_sets.router)
app.include_router(users.router)
app.include_router(weights.router)
app.include_router(auth.router)
app.include_router(workout_exercises.router)
app.include_router(roles.router)
app.include_router(permissions.router)


@app.get("/")
async def root():
    return {"message": "Hello World!"}
