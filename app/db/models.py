import datetime

from sqlmodel import Field, SQLModel, Relationship


class ExerciseMuscleGroupLink(SQLModel, table=True):
    exercise_id: int | None = Field(
        default=None, foreign_key="exercise.id", primary_key=True
    )
    musclegroup_id: int | None = Field(
        default=None, foreign_key="musclegroup.id", primary_key=True
    )


class ExerciseWorkoutRoutineLink(SQLModel, table=True):
    exercise_id: int | None = Field(
        default=None, foreign_key="exercise.id", primary_key=True
    )
    workoutroutine_id: int | None = Field(
        default=None, foreign_key="workoutroutine.id", primary_key=True
    )


class MuscleGroupBase(SQLModel):
    name: str = Field(index=True, unique=True)


class MuscleGroup(MuscleGroupBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    exercises: list["Exercise"] = Relationship(
        back_populates="musclegroups", link_model=ExerciseMuscleGroupLink
    )


class MuscleGroupCreate(MuscleGroupBase):
    pass


class MuscleGroupRead(MuscleGroupBase):
    id: int


class MuscleGroupUpdate(SQLModel):
    name: str | None = None


class ExerciseBase(SQLModel):
    name: str | None = Field(default=None, index=True, unique=True)


class ExerciseCreate(ExerciseBase):
    musclegroup_ids: list[int] = []


class ExerciseRead(ExerciseBase):
    id: int


class ExerciseUpdate(SQLModel):
    name: str | None = None
    musclegroup_ids: list[int] = []


class ExerciseReadWithMuscleGroups(ExerciseRead):
    musclegroups: list[MuscleGroupRead] = []


class MuscleGroupReadWithExercises(MuscleGroupRead):
    exercises: list[ExerciseRead] = []


class WorkoutRoutineBase(SQLModel):
    name: str = Field(unique=True, index=True)


class WorkoutBase(SQLModel):
    date: datetime.date = datetime.date.today()


class SetBase(SQLModel):
    reps: int | None = None
    weight: float | None = None


class Set(SetBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    exercise_id: int = Field(foreign_key="exercise.id")
    exercise: "Exercise" = Relationship(back_populates="sets")
    is_actual: bool
    workout_id: int | None = Field(default=None, foreign_key="workout.id")
    workout: "Workout" = Relationship(back_populates="sets")


class SetRead(SetBase):
    pass


class SetCreate(SetBase):
    exercise_id: int | None = None
    is_actual: bool = True
    workout_id: int | None = None


class ExerciseCreateWithSets(ExerciseBase):
    id: int
    sets: list[SetCreate] = []


class WorkoutRoutineCreate(WorkoutRoutineBase):
    exercises: list[ExerciseCreateWithSets] = []


class ExerciseReadWithSets(ExerciseRead):
    sets: list[SetRead] = []


class WorkoutRoutineRead(WorkoutRoutineBase):
    id: int
    exercises: list[ExerciseReadWithSets] = []


class WorkoutRoutineUpdate(WorkoutRoutineBase):
    name: str | None = None
    exercises: list[ExerciseCreateWithSets] = []


class WorkoutCreate(WorkoutBase):
    sets: list[SetCreate] = []


class Exercise(ExerciseBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    musclegroups: list[MuscleGroup] = Relationship(
        back_populates="exercises", link_model=ExerciseMuscleGroupLink
    )

    workoutroutines: list["WorkoutRoutine"] = Relationship(
        back_populates="exercises", link_model=ExerciseWorkoutRoutineLink
    )

    sets: list[Set] = Relationship(back_populates="exercise")


class Workout(WorkoutBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    workoutroutine_id: int = Field(foreign_key="workoutroutine.id")
    workoutroutine: "WorkoutRoutine" = Relationship(back_populates="workouts")
    sets: list[Set] = Relationship(back_populates="workout")


class WorkoutRoutine(WorkoutRoutineBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    workouts: list[Workout] = Relationship(back_populates="workoutroutine")
    exercises: list["Exercise"] = Relationship(
        back_populates="workoutroutines", link_model=ExerciseWorkoutRoutineLink
    )
