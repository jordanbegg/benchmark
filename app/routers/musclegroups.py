from fastapi import APIRouter, Depends, Query, HTTPException
from sqlmodel import Session, select

from app.db.models import (
    MuscleGroup,
    MuscleGroupCreate,
    MuscleGroupRead,
    MuscleGroupReadWithExercises,
    MuscleGroupUpdate,
)
from dependencies import get_session

router = APIRouter(
    prefix="/musclegroups",
    responses={404: {"description": "Not Found"}},
)


@router.post("/", response_model=MuscleGroupRead)
def create_musclegroup(
    *, session: Session = Depends(get_session), musclegroup: MuscleGroupCreate
):
    db_musclegroup = MuscleGroup.from_orm(musclegroup)
    session.add(db_musclegroup)
    session.commit()
    session.refresh(db_musclegroup)
    return db_musclegroup


@router.get("/", response_model=list[MuscleGroupRead])
def read_musclegroups(
    *,
    session: Session = Depends(get_session),
    offset: int = 0,
    limit: int = Query(default=100, lte=100),
):
    return session.exec(select(MuscleGroup).offset(offset).limit(limit)).all()


@router.get(
    "/{musclegroup_id}",
    response_model=MuscleGroupReadWithExercises,
)
def read_musclegroup(
    *, session: Session = Depends(get_session), musclegroup_id: int
):
    if musclegroup := session.get(MuscleGroup, musclegroup_id):
        return musclegroup
    else:
        raise HTTPException(status_code=404, detail="MuscleGroup not found")


@router.patch("/{musclegroup_id}", response_model=MuscleGroupRead)
def update_musclegroup(
    *,
    session: Session = Depends(get_session),
    musclegroup_id: int,
    musclegroup: MuscleGroupUpdate,
):
    db_musclegroup = session.get(MuscleGroup, musclegroup_id)
    if not db_musclegroup:
        raise HTTPException(status_code=404, detail="MuscleGroup not found")
    musclegroup_data = musclegroup.dict(exclude_unset=True)
    for key, value in musclegroup_data.items():
        setattr(db_musclegroup, key, value)
    session.add(db_musclegroup)
    session.commit()
    session.refresh(db_musclegroup)
    return db_musclegroup


@router.delete("/{musclegroup_id}")
def delete_musclegroup(
    *, session: Session = Depends(get_session), musclegroup_id: int
):
    musclegroup = session.get(MuscleGroup, musclegroup_id)
    if not musclegroup:
        raise HTTPException(status_code=404, detail="Muscle Group not found")
    session.delete(musclegroup)
    session.commit()
    return {"ok": True}
