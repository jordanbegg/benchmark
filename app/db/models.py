import datetime

from sqlmodel import Field, SQLModel, Relationship


class ExerciseMuscleGroup(SQLModel, table=True):
    exercise_musclegroup_id: int | None = Field(default=None, primary_key=True)
    exercise_id: int = Field(foreign_key="exercise.id")
    musclegroup_id: int = Field(foreign_key="musclegroup.id")
    exercise: "Exercise" = Relationship(
        back_populates="exercise_muscle_groups"
    )
    muscle_group: "MuscleGroup" = Relationship(
        back_populates="exercise_muscle_groups"
    )


class RoutineExercise(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    routine_id: int = Field(foreign_key="workoutroutine.id")
    exercise_id: int = Field(foreign_key="exercise.id")
    workout_routine: "WorkoutRoutine" = Relationship(
        back_populates="routine_exercises"
    )
    exercise: "Exercise" = Relationship(back_populates="routine_exercises")
    planned_sets: list["PlannedSet"] = Relationship(
        back_populates="routine_exercise"
    )


class WorkoutExercise(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    workout_id: int = Field(foreign_key="workout.id")
    exercise_id: int = Field(foreign_key="exercise.id")
    workout: "Workout" = Relationship(
        back_populates="workout_exercises"
    )
    exercise: "Exercise" = Relationship(back_populates="workout_exercises")
    sets: list["Set"] = Relationship(
        back_populates="workout_exercise"
    )

class MuscleGroupBase(SQLModel):
    name: str = Field(index=True, unique=True)


class MuscleGroup(MuscleGroupBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    exercise_muscle_groups: list["ExerciseMuscleGroup"] = Relationship(
        back_populates="muscle_group"
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


class PlannedSetBase(SQLModel):
    reps: int | None = None


class Set(SetBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    workout_exercise_id: int | None = Field(foreign_key="workoutexercise.id")
    workout_exercise: WorkoutExercise = Relationship(
        back_populates="sets"
    )


class PlannedSet(SetBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    routine_exercise_id: int | None = Field(foreign_key="routineexercise.id")
    reps: int
    routine_exercise: RoutineExercise = Relationship(
        back_populates="planned_sets"
    )


class SetRead(SetBase):
    pass


class FullSetRead(SetBase):
    exercise_id: int
    workout_id: int
    id: int


class FullPlannedSetRead(PlannedSetBase):
    exercise_id: int
    workoutroutine_id: int
    id: int


class SetUpdate(SetBase):
    exercise_id: int | None = None
    workout_id: int | None = None


class PlannedSetUpdate(PlannedSetBase):
    exercise_id: int | None = None
    workoutroutine_id: int | None = None


class PlannedSetRead(PlannedSetBase):
    exercise_id: int | None = None


class PlannedSetCreate(PlannedSetBase):
    exercise_id: int | None = None
    workoutroutine_id: int | None = None


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


class RoutineExerciseReadWithPlannedSets(SQLModel):
    exercise: ExerciseRead
    planned_sets: list[SetRead] = []

class WorkoutExerciseReadWithSets(SQLModel):
    exercise: ExerciseRead
    sets: list[SetRead] = []

class WorkoutRoutineRead(WorkoutRoutineBase):
    id: int
    routine_exercises: list[RoutineExerciseReadWithPlannedSets] = []


class WorkoutRoutinesRead(WorkoutRoutineBase):
    id: int
    routine_exercises: list[RoutineExerciseReadWithPlannedSets] = []

class WorkoutRead(WorkoutBase):
    id: int
    workoutroutine_id: int
    workout_exercises: list[WorkoutExerciseReadWithSets] = []

class WorkoutsRead(WorkoutBase):
    id: int
    workoutroutine_id: int
    workout_exercises: list[WorkoutExerciseReadWithSets] = []

class WorkoutRoutineUpdate(WorkoutRoutineBase):
    name: str | None = None
    exercises: list[ExerciseCreateWithPlannedSets] = []


class WorkoutCreate(WorkoutBase):
    workoutroutine_id: int
    exercises: list[ExerciseCreateWithSets] = []


# class WorkoutRead(WorkoutBase):
#     id: int
#     exercises: list[ExerciseReadWithSets] = []
#     workoutroutine_id: int | None = None


# class WorkoutsRead(WorkoutBase):
#     id: int
#     exercises: list[ExerciseRead] = []
#     workoutroutine_id: int | None = None


class WorkoutsReadWithoutSets(WorkoutBase):
    id: int


class WorkoutUpdate(WorkoutBase):
    exercises: list[ExerciseCreateWithSets] = []
    workoutroutine_id: int | None = None


class Exercise(ExerciseBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    routine_exercises: list["RoutineExercise"] = Relationship(
        back_populates="exercise"
    )
    workout_exercises: list["WorkoutExercise"] = Relationship(
        back_populates="exercise"
    )
    exercise_muscle_groups: list["ExerciseMuscleGroup"] = Relationship(
        back_populates="exercise"
    )


class Workout(WorkoutBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    workoutroutine_id: int = Field(foreign_key="workoutroutine.id")
    workoutroutine: "WorkoutRoutine" = Relationship(back_populates="workouts")
    workout_exercises: list[WorkoutExercise] = Relationship(
        back_populates="workout"
    )


class WorkoutRoutine(WorkoutRoutineBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    workouts: list[Workout] = Relationship(back_populates="workoutroutine")
    routine_exercises: list[RoutineExercise] = Relationship(
        back_populates="workout_routine"
    )
