from typing import Annotated

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlmodel import Session, select, desc

from app.db.models import (
    Weight,
    WeightRead,
    WeightCreate,
)
from app.dependencies import get_session
from app.auth import get_current_user, require_permission

router = APIRouter(
    prefix="/weights",
    responses={404: {"description": "Not Found"}},
)


@router.post("/", response_model=WeightRead)
@require_permission("create_all_weights", "create_own_weight")
def create_weight(
    *,
    session: Session = Depends(get_session),
    weight: WeightCreate,
    current_user: Annotated[str, Depends(get_current_user)],
):
    if weight.user_id != current_user.id and not current_user.has("create_all_weights"):
        raise HTTPException(
            status_code=400,
            detail="User does not have permission to create weights for another user",
        )
    db_weight = Weight.from_orm(weight)
    session.add(db_weight)
    session.commit()
    session.refresh(db_weight)
    return db_weight


@router.get("/", response_model=list[WeightRead])
@require_permission("read_all_weights", "read_own_weight")
def read_weights(
    *,
    session: Session = Depends(get_session),
    offset: int = 0,
    limit: int = Query(default=100, lte=100),
    user_id: int | None = None,
    current_user: Annotated[str, Depends(get_current_user)],
):
    if user_id != current_user.id and not current_user.has("read_all_weights"):
        raise HTTPException(
            status_code=400,
            detail="User does not have permission to read weights for another user",
        )
    query = select(Weight)
    if user_id:
        query = query.where(Weight.user_id == user_id)
    return session.exec(
        query.order_by(desc(Weight.date)).offset(offset).limit(limit)
    ).all()


@router.get(
    "/{weight_id}",
    response_model=WeightRead,
)
@require_permission("read_all_weights", "read_own_weight")
def read_weight(
    *,
    session: Session = Depends(get_session),
    weight_id: int,
    current_user: Annotated[str, Depends(get_current_user)],
):
    if weight := session.get(Weight, weight_id):
        if weight.user_id != current_user.id and not current_user.has(
            "read_all_weights"
        ):
            raise HTTPException(
                status_code=400,
                detail="User does not have permission to read weights for another user",
            )
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
@require_permission("delete_all_weights", "delete_own_weight")
def delete_weight(
    *,
    session: Session = Depends(get_session),
    weight_id: int,
    current_user: Annotated[str, Depends(get_current_user)],
):
    weight = session.get(Weight, weight_id)
    if not weight:
        raise HTTPException(status_code=404, detail="Weight not found")
    if weight.user_id != current_user.id and not current_user.has("delete_all_weights"):
        raise HTTPException(
            status_code=400,
            detail="User does not have permission to delete weights for another user",
        )
    session.delete(weight)
    session.commit()
    return {"ok": True}
