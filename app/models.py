from sqlmodel import Field, SQLModel, Relationship
from pydantic import EmailStr
from pydantic import condecimal
from datetime import datetime, timedelta


class Plan(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=100)
    description: str | None = Field(default=None, max_length=255)
    price: condecimal(max_digits=10, decimal_places=2) = Field(default=0.00)
    duration_months: int = Field(default=1)  # длительность подписки в месяцах


class Subscription(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    plan_id: int = Field(foreign_key="plan.id")
    start_date: datetime = Field(default_factory=datetime.utcnow)
    end_date: datetime
    auto_renew: bool = Field(default=False)

    user: 'User' = Relationship(back_populates="subscriptions")
    plan: 'Plan' = Relationship()

    def is_active(self) -> bool:
        return datetime.utcnow() <= self.end_date

    def renew_subscription(self):
        if self.auto_renew:
            self.start_date = datetime.utcnow()
            self.end_date = self.start_date + timedelta(days=self.plan.duration_months * 30)  # пример для месяцев

    class ConfigDict:
        arbitrary_types_allowed = True


class Payment(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    subscription_id: int = Field(foreign_key="subscription.id")
    amount: condecimal(max_digits=10, decimal_places=2) = Field(default=0.00)
    payment_date: datetime = Field(default_factory=datetime.utcnow)
    status: str = Field(default="pending", max_length=20)  # статусы: "pending", "completed", "failed"

    user: 'User' = Relationship()
    subscription: 'Subscription' = Relationship()


class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    first_name: str | None = Field(default=None, max_length=255)
    last_name: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=20)
    bio: str | None = Field(default=None, max_length=500)


class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    hashed_password: str = Field(max_length=255)
    disabled: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime | None = Field(default=None)

    subscriptions: list["Subscription"] = Relationship(back_populates="user")
    payments: list["Payment"] = Relationship(back_populates="user")

    def update_timestamp(self):
        self.updated_at = datetime.utcnow()

    class ConfigDict:
        arbitrary_types_allowed = True


class UserCreate(UserBase):
    password: str | None = Field(default=None, min_length=8, max_length=40)


class UserUpdate(SQLModel):
    first_name: str | None = Field(default=None, max_length=255)
    last_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=20)
    bio: str | None = Field(default=None, max_length=500)
    password: str | None = Field(default=None, min_length=8, max_length=40)


class UserPublic(UserBase):
    id: int


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    first_name: str | None = Field(default=None, max_length=255)
    last_name: str | None = Field(default=None, max_length=255)

    class ConfigDict:
        arbitrary_types_allowed = True


class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: int | None = None


class Message(SQLModel):
    message: str
