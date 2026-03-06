from shared_lib.db.models.user import UserRole, Role, User
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from config import Config


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class DataInitializer:
    @staticmethod
    def init_roles(session: Session):
        existing_roles = {
            role.name for role in session.query(Role).all()
        }

        for role_name in UserRole:
            if role_name not in existing_roles:
                session.add(Role(name=role_name))

        session.flush()

    @staticmethod
    def create_default_admin(session: Session):
        admin_email = getattr(Config, "DEFAULT_ADMIN_EMAIL", None) or getattr(
            Config, "ADMIN_EMAIL", "admin@example.com"
        )
        admin_password = getattr(Config, "DEFAULT_ADMIN_PASSWORD", None) or getattr(
            Config, "ADMIN_PASSWORD", "admin123"
        )

        existing_admin = session.query(User).filter(User.email == admin_email).first()
        if existing_admin:
            return

        admin_role = session.query(Role).filter(Role.name == UserRole.ADMIN).first()
        if not admin_role:
            raise ValueError("ADMIN role not found. Run init_roles first.")

        admin_user = User(
            email=admin_email,
            hashed_password=pwd_context.hash(admin_password),
            first_name="System",
            last_name="Admin",
            is_deleted=False,
            role_id=admin_role.id,
        )

        session.add(admin_user)
        session.flush()

    @staticmethod
    def create_test_user(session: Session):
        test_email = getattr(Config, "TEST_USER_EMAIL", "user@example.com")
        test_password = getattr(Config, "TEST_USER_PASSWORD", "user123")

        existing_user = session.query(User).filter(User.email == test_email).first()
        if existing_user:
            return

        user_role = session.query(Role).filter(Role.name == UserRole.USER).first()
        if not user_role:
            raise ValueError("USER role not found. Run init_roles first.")

        test_user = User(
            email=test_email,
            hashed_password=pwd_context.hash(test_password),
            first_name="Test",
            last_name="User",
            is_deleted=False,
            role_id=user_role.id,
        )

        session.add(test_user)
        session.flush()

    @classmethod
    def seed_all(cls, session: Session):
        cls.init_roles(session)
        cls.create_default_admin(session)
        cls.create_test_user(session)
        session.commit()