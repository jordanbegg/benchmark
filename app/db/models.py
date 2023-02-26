from sqlmodel import Field, SQLModel, Relationship


class ExerciseMuscleGroupLink(SQLModel, table=True):
    exercise_id: int | None = Field(
        default=None, foreign_key="exercise.id", primary_key=True
    )
    musclegroup_id: int | None = Field(
        default=None, foreign_key="musclegroup.id", primary_key=True
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
    name: str = Field(index=True, unique=True)


class Exercise(ExerciseBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    musclegroups: list[MuscleGroup] = Relationship(
        back_populates="exercises", link_model=ExerciseMuscleGroupLink
    )


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
