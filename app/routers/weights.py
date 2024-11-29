from fastapi import APIRouter, Depends, Query, HTTPException
from sqlmodel import Session, select

from app.db.models import (
    Weight,
    WeightRead,
    WeightCreate,
)
from app.dependencies import get_session

router = APIRouter(
    prefix="/weights",
    responses={404: {"description": "Not Found"}},
)


@router.post("/", response_model=WeightRead)
def create_weight(
    *, session: Session = Depends(get_session), weight: WeightCreate
):
    db_weight = Weight.from_orm(weight)
    session.add(db_weight)
    session.commit()
    session.refresh(db_weight)
    return db_weight


@router.get("/", response_model=list[WeightRead])
def read_weights(
    *,
    session: Session = Depends(get_session),
    offset: int = 0,
    limit: int = Query(default=100, lte=100),
):
    return session.exec(
        select(Weight)
        .order_by(Weight.id)
        .offset(offset)
        .limit(limit)
    ).all()


@router.get(
    "/{weight_id}",
    response_model=WeightRead,
)
def read_weight(
    *, session: Session = Depends(get_session), weight_id: int
):
    if weight := session.get(Weight, weight_id):
        return weight
    else:
        raise HTTPException(status_code=404, detail="Weight not found")


# @router.patch("/{musclegroup_id}", response_model=MuscleGroupRead)
# def update_musclegroup(
#     *,
#     session: Session = Depends(get_session),
#     musclegroup_id: int,
#     musclegroup: MuscleGroupUpdate,
# ):
#     db_musclegroup = session.get(Weight, musclegroup_id)
#     if not db_musclegroup:
#         raise HTTPException(status_code=404, detail="Weight not found")
#     musclegroup_data = musclegroup.dict(exclude_unset=True)
#     for key, value in musclegroup_data.items():
#         if key == "name":
#             if session.exec(
#                 select(Weight).where(
#                     Weight.name == value.lower(),
#                     Weight.id != db_musclegroup.id,
#                 )
#             ).first():
#                 raise ValueError(
#                     f"Weight with name {value.lower()} already exists!"
#                 )
#             else:
#                 setattr(db_musclegroup, key, value.lower())
#         setattr(db_musclegroup, key, value)
#     session.add(db_musclegroup)
#     session.commit()
#     session.refresh(db_musclegroup)
#     return db_musclegroup


@router.delete("/{weight_id}")
def delete_weight(
    *, session: Session = Depends(get_session), weight_id: int
):
    weight = session.get(Weight, weight_id)
    if not weight:
        raise HTTPException(status_code=404, detail="Weight not found")
    session.delete(weight)
    session.commit()
    return {"ok": True}
