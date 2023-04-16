from fastapi import FastAPI

from app.routers import (
    exercises,
    musclegroups,
    workout_routines,
    workouts,
    sets,
    planned_sets,
)

app = FastAPI()

app.include_router(exercises.router)
app.include_router(musclegroups.router)
app.include_router(workout_routines.router)
app.include_router(workouts.router)
app.include_router(sets.router)
app.include_router(planned_sets.router)


@app.get("/")
async def root():
    return {"message": "Hello World!"}
