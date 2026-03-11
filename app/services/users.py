from sqlalchemy.orm import Session
from app.models.user import User


def get_or_create_user(db: Session, current_user: dict) -> User:
    user = db.query(User).filter(User.kc_sub == current_user["sub"]).first()
    if user is None:
        user = User(
                kc_sub=current_user["sub"],
                username=current_user.get("username") or "unknown",
                )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user
