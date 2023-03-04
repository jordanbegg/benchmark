from fastapi import FastAPI

from app.routers import exercises, musclegroups, workout_routines

app = FastAPI()

app.include_router(exercises.router)
app.include_router(musclegroups.router)
app.include_router(workout_routines.router)


@app.get("/")
async def root():
    return {"message": "Hello World!"}
