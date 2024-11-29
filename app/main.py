from fastapi import FastAPI

from app.routers import (
    exercises,
    musclegroups,
    workout_routines,
    workouts,
    sets,
    planned_sets,
    users,
    weights
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

@app.get("/")
async def root():
    return {"message": "Hello World!"}
