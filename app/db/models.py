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


class ExerciseWorkoutLink(SQLModel, table=True):
    exercise_id: int | None = Field(
        default=None, foreign_key="exercise.id", primary_key=True
    )
    workout_id: int | None = Field(
        default=None, foreign_key="workout.id", primary_key=True
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
    workout_id: int | None = Field(default=None, foreign_key="workout.id")
    workout: "Workout" = Relationship(back_populates="sets")


class PlannedSet(SetBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    exercise_id: int = Field(foreign_key="exercise.id")
    exercise: "Exercise" = Relationship(back_populates="planned_sets")
    workoutroutine_id: int | None = Field(
        default=None, foreign_key="workoutroutine.id"
    )
    workoutroutine: "WorkoutRoutine" = Relationship(
        back_populates="planned_sets"
    )


class SetRead(SetBase):
    exercise_id: int | None = None


class FullSetRead(SetBase):
    exercise_id: int
    workout_id: int
    id: int


class SetUpdate(SetBase):
    exercise_id: int
    workout_id: int


class PlannedSetRead(SetBase):
    exercise_id: int | None = None


class PlannedSetCreate(SetBase):
    exercise_id: int | None = None
    workout_routine_id: int | None = None


class SetCreate(SetBase):
    exercise_id: int | None = None
    workout_id: int | None = None


class ExerciseCreateWithPlannedSets(ExerciseBase):
    id: int
    planned_sets: list[PlannedSetCreate] = []


class ExerciseCreateWithSets(ExerciseBase):
    id: int
    sets: list[SetCreate] = []


class WorkoutRoutineCreate(WorkoutRoutineBase):
    exercises: list[ExerciseCreateWithPlannedSets] = []


class ExerciseReadWithSets(ExerciseRead):
    sets: list[SetRead] = []


class ExerciseReadWithPlannedSets(ExerciseRead):
    planned_sets: list[SetRead] = []


class WorkoutRoutineRead(WorkoutRoutineBase):
    id: int
    exercises: list[ExerciseReadWithPlannedSets] = []


class WorkoutRoutinesRead(WorkoutRoutineBase):
    id: int
    exercises: list[ExerciseRead] = []


class WorkoutRoutineUpdate(WorkoutRoutineBase):
    name: str | None = None
    exercises: list[ExerciseCreateWithPlannedSets] = []


class WorkoutCreate(WorkoutBase):
    exercises: list[ExerciseCreateWithSets] = []
    workoutroutine_id: int


class WorkoutRead(WorkoutBase):
    id: int
    exercises: list[ExerciseReadWithSets] = []
    workoutroutine_id: int | None = None


class WorkoutsRead(WorkoutBase):
    id: int
    exercises: list[ExerciseRead] = []
    workoutroutine_id: int | None = None


class WorkoutsReadWithoutSets(WorkoutBase):
    id: int


class WorkoutUpdate(WorkoutBase):
    exercises: list[ExerciseCreateWithSets] = []
    workoutroutine_id: int | None = None


class Exercise(ExerciseBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    musclegroups: list[MuscleGroup] = Relationship(
        back_populates="exercises", link_model=ExerciseMuscleGroupLink
    )

    workoutroutines: list["WorkoutRoutine"] = Relationship(
        back_populates="exercises", link_model=ExerciseWorkoutRoutineLink
    )

    workouts: list["Workout"] = Relationship(
        back_populates="exercises", link_model=ExerciseWorkoutLink
    )

    sets: list[Set] = Relationship(back_populates="exercise")
    planned_sets: list[PlannedSet] = Relationship(back_populates="exercise")


class Workout(WorkoutBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    workoutroutine_id: int = Field(foreign_key="workoutroutine.id")
    workoutroutine: "WorkoutRoutine" = Relationship(back_populates="workouts")
    exercises: list["Exercise"] = Relationship(
        back_populates="workouts", link_model=ExerciseWorkoutLink
    )
    sets: list[Set] = Relationship(back_populates="workout")


class WorkoutRoutine(WorkoutRoutineBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    workouts: list[Workout] = Relationship(back_populates="workoutroutine")
    exercises: list["Exercise"] = Relationship(
        back_populates="workoutroutines", link_model=ExerciseWorkoutRoutineLink
    )
    planned_sets: list[PlannedSet] = Relationship(
        back_populates="workoutroutine"
    )
