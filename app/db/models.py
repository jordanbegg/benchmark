import datetime

from sqlmodel import Field, SQLModel, Relationship


class RolePermissions(SQLModel, table=True):
    role_permission_id: int | None = Field(default=None, primary_key=True)
    permission_id: int = Field(foreign_key="permission.id")
    role_id: int = Field(foreign_key="role.id")
    permission: "Permission" = Relationship(back_populates="role_permissions")
    role: "Role" = Relationship(back_populates="role_permissions")


class PermissionBase(SQLModel):
    name: str


class PermissionCreate(PermissionBase):
    pass


class PermissionRead(PermissionBase):
    id: int


class Permission(PermissionBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    role_permissions: list["RolePermissions"] = Relationship(
        back_populates="permission"
    )


class RoleBase(SQLModel):
    name: str


class RoleCreate(RoleBase):
    name: str
    permission_ids: list[int] = []


class RolePermissionsRead(SQLModel):
    role: RoleBase
    permission: PermissionRead


class RolePermissionsReadOnlyPermission(SQLModel):
    permission: PermissionRead


class Role(RoleBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    users: list["User"] = Relationship(back_populates="role")
    role_permissions: list["RolePermissions"] = Relationship(back_populates="role")


class RoleRead(RoleBase):
    id: int
    role_permissions: list["RolePermissionsRead"] = []


class RoleReadMinimal(SQLModel):
    id: int


class RoleReadOnlyPermissions(RoleBase):
    id: int
    role_permissions: list[RolePermissionsReadOnlyPermission] = []


class UserBase(SQLModel):
    name: str
    email_address: str = Field(index=True, unique=True, max_length=256)


class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    password_hash: str
    weights: list["Weight"] = Relationship(back_populates="user")
    workouts: list["Workout"] = Relationship(back_populates="user")
    workout_routines: list["WorkoutRoutine"] = Relationship(back_populates="user")
    role_id: int | None = Field(foreign_key="role.id")
    role: Role = Relationship(back_populates="users")

    def has(self, permission: str):
        if permission in [rp.permission.name for rp in self.role.role_permissions]:
            return True


class UserLogin(SQLModel):
    email_address: str
    password: str


class UserCreate(UserBase):
    password: str
    role_id: int | None = None


class UserRead(UserBase):
    id: int
    role: RoleReadMinimal


class WeightBase(SQLModel):
    date: datetime.date = datetime.date.today()
    weight: float


class Weight(WeightBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    user: User = Relationship(back_populates="weights")
    user_id: int = Field(default=None, foreign_key="user.id")


class WeightCreate(WeightBase):
    user_id: int


class WeightRead(WeightBase):
    id: int
    user_id: int


class ExerciseMuscleGroup(SQLModel, table=True):
    exercise_musclegroup_id: int | None = Field(default=None, primary_key=True)
    exercise_id: int = Field(foreign_key="exercise.id")
    musclegroup_id: int = Field(foreign_key="musclegroup.id")
    exercise: "Exercise" = Relationship(back_populates="exercise_muscle_groups")
    muscle_group: "MuscleGroup" = Relationship(back_populates="exercise_muscle_groups")


class RoutineExercise(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    routine_id: int = Field(foreign_key="workoutroutine.id")
    exercise_id: int = Field(foreign_key="exercise.id")
    workout_routine: "WorkoutRoutine" = Relationship(back_populates="routine_exercises")
    exercise: "Exercise" = Relationship(back_populates="routine_exercises")
    planned_sets: list["PlannedSet"] = Relationship(back_populates="routine_exercise")


class WorkoutExercise(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    workout_id: int = Field(foreign_key="workout.id")
    exercise_id: int = Field(foreign_key="exercise.id")
    workout: "Workout" = Relationship(back_populates="workout_exercises")
    exercise: "Exercise" = Relationship(back_populates="workout_exercises")
    sets: list["Set"] = Relationship(back_populates="workout_exercise")


class MuscleGroupBase(SQLModel):
    name: str = Field(index=True, unique=True, max_length=128)


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
    name: str | None = Field(default=None, index=True, unique=True, max_length=128)


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
    name: str = Field(index=True, max_length=128)


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
    workout_exercise: WorkoutExercise = Relationship(back_populates="sets")


class PlannedSet(SetBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    routine_exercise_id: int | None = Field(foreign_key="routineexercise.id")
    reps: int
    routine_exercise: RoutineExercise = Relationship(back_populates="planned_sets")


class SetRead(SetBase):
    id: int
    workout_exercise_id: int


class SetUpdate(SetBase):
    exercise_id: int | None = None
    workout_id: int | None = None


class PlannedSetUpdate(PlannedSetBase):
    exercise_id: int | None = None
    workoutroutine_id: int | None = None


class PlannedSetRead(PlannedSetBase):
    id: int
    routine_exercise_id: int | None = None


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
    user_id: int


class ExerciseReadWithSets(ExerciseRead):
    sets: list[SetRead] = []


class RoutineExerciseReadWithPlannedSets(SQLModel):
    exercise: ExerciseRead
    planned_sets: list[PlannedSetRead] = []


class WorkoutExerciseReadWithSets(SQLModel):
    exercise: ExerciseRead
    sets: list[SetRead] = []


class ExerciseReadFull(ExerciseBase):
    musclegroups: list[MuscleGroupRead] = []
    sets: list[SetRead] = []


class WorkoutExerciseBase(SQLModel):
    workout_id: int
    exercise_id: int


class WorkoutExerciseRead(WorkoutExerciseBase):
    workout: WorkoutBase
    sets: list[SetRead]


class WorkoutExerciseCreate(WorkoutExerciseBase):
    pass


class WorkoutRoutineRead(WorkoutRoutineBase):
    id: int
    routine_exercises: list[RoutineExerciseReadWithPlannedSets] = []
    user_id: int


class WorkoutRoutinesRead(WorkoutRoutineBase):
    id: int
    routine_exercises: list[RoutineExerciseReadWithPlannedSets] = []
    user_id: int


class WorkoutRead(WorkoutBase):
    id: int
    workoutroutine_id: int
    workout_exercises: list[WorkoutExerciseReadWithSets] = []
    user_id: int


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
    user_id: int


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

    routine_exercises: list["RoutineExercise"] = Relationship(back_populates="exercise")
    workout_exercises: list["WorkoutExercise"] = Relationship(back_populates="exercise")
    exercise_muscle_groups: list["ExerciseMuscleGroup"] = Relationship(
        back_populates="exercise"
    )


class Workout(WorkoutBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    workoutroutine_id: int = Field(foreign_key="workoutroutine.id")
    workoutroutine: "WorkoutRoutine" = Relationship(back_populates="workouts")
    workout_exercises: list[WorkoutExercise] = Relationship(back_populates="workout")

    user_id: int = Field(default=None, foreign_key="user.id")
    user: User = Relationship(back_populates="workouts")


class WorkoutRoutine(WorkoutRoutineBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    workouts: list[Workout] = Relationship(back_populates="workoutroutine")
    routine_exercises: list[RoutineExercise] = Relationship(
        back_populates="workout_routine"
    )

    user_id: int = Field(default=None, foreign_key="user.id")
    user: User = Relationship(back_populates="workout_routines")
