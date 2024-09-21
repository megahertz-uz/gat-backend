from sqlmodel import Field, SQLModel, Relationship
from pydantic import EmailStr, condecimal
from datetime import datetime, timedelta
from enum import Enum


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
            self.end_date = self.start_date + timedelta(days=self.plan.duration_months * 30)

    class ConfigDict:
        arbitrary_types_allowed = True


class Payment(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    subscription_id: int = Field(foreign_key="subscription.id")
    amount: condecimal(max_digits=10, decimal_places=2) = Field(default=0.00)
    payment_date: datetime = Field(default_factory=datetime.utcnow)
    status: str = Field(default="pending", max_length=20)  # статусы: "pending", "completed", "failed"

    user: 'User' = Relationship(back_populates="payments")
    subscription: 'Subscription' = Relationship()


class Dialogue(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    mission_id: int = Field(foreign_key="mission.id")
    character_name: str = Field(max_length=255)
    text: str = Field(max_length=500)
    background_url: str = Field(max_length=255)
    character_image_url: str = Field(max_length=255)
    order: int = Field(default=0)  # Порядок вызова диалогов

    mission: 'Mission' = Relationship(back_populates="dialogues")


class QuestStatusEnum(str, Enum):
    in_progress = "in_progress"
    completed = "completed"
    failed = "failed"


class MissionStatusEnum(str, Enum):
    in_progress = "in_progress"
    completed = "completed"
    failed = "failed"


class CityBase(SQLModel):
    title: str
    latitude: float
    longitude: float
    picture_small_url: str = Field(max_length=255)


class City(CityBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    description: str | None = Field(default=None, max_length=500)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    quests: list["Quest"] = Relationship(back_populates="city")


class CityWithProgress(SQLModel):
    id: int
    name: str
    description: str | None
    picture_small_url: str
    latitude: float
    longitude: float
    progress: float


class CityPublic(SQLModel):
    id: int
    title: str
    picture_small_url: str
    latitude: float
    longitude: float


class Artifact(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=255)
    description: str | None = Field(default=None, max_length=500)


class ArtifactPiece(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    artifact_id: int = Field(foreign_key="artifact.id")
    name: str = Field(max_length=255)
    description: str | None = Field(default=None, max_length=500)

    artifact: Artifact = Relationship()


class Quest(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(max_length=255)
    description: str | None = Field(default=None, max_length=500)
    city_id: int = Field(foreign_key="city.id")
    city: City | None = Relationship(back_populates="quests")
    missions: list["Mission"] = Relationship(back_populates="quest")



class QuestPublic(SQLModel):
    id: int
    title: str
    description: str | None
    picture_small_url: str
    city: str


class Mission(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    quest_id: int = Field(foreign_key="quest.id")
    name: str = Field(max_length=255)
    description: str | None = Field(default=None, max_length=500)
    mission_order: int = Field()  # Порядок вызова миссий в квесте
    reward_artifact_piece_id: int | None = Field(foreign_key="artifactpiece.id")
    city_id: int | None = Field(foreign_key="city.id")

    quest: Quest = Relationship(back_populates="missions")
    city: City | None = Relationship()
    reward_artifact_piece: ArtifactPiece | None = Relationship()
    dialogues: list["Dialogue"] = Relationship(back_populates="mission")


class Achievement(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=255)
    description: str | None = Field(default=None, max_length=500)


class UserAchievement(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    achievement_id: int = Field(foreign_key="achievement.id")
    progress: int = Field(default=0)
    unit_of_measurement: str | None = Field(max_length=50)

    user: 'User' = Relationship(back_populates="achievements")
    achievement: 'Achievement' = Relationship()


class UserQuest(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    quest_id: int = Field(foreign_key="quest.id")
    status: QuestStatusEnum = Field(default=QuestStatusEnum.in_progress)

    user: 'User' = Relationship(back_populates="quests")
    quest: 'Quest' = Relationship()


class UserMission(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    mission_id: int = Field(foreign_key="mission.id")
    status: MissionStatusEnum = Field(default=MissionStatusEnum.in_progress)

    user: 'User' = Relationship(back_populates="missions")
    mission: 'Mission' = Relationship()


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

    subscriptions: list['Subscription'] = Relationship(back_populates="user")
    payments: list['Payment'] = Relationship(back_populates="user")
    quests: list['UserQuest'] = Relationship(back_populates="user")
    missions: list['UserMission'] = Relationship(back_populates="user")
    achievements: list['UserAchievement'] = Relationship(back_populates="user")

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


class Story(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(max_length=255)
    description: str | None = Field(default=None, max_length=500)
    picture_small_url: str = Field(max_length=255)  # Превью изображение (маленькое)
    picture_big_url: str = Field(max_length=255)  # Полное изображение (большое)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class ConfigDict:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }


class StoryPublic(SQLModel):
    id: int
    title: str
    description: str | None
    picture_small_url: str
    picture_big_url: str
    created_at: datetime


class StoriesPublic(SQLModel):
    data: list[StoryPublic]
    count: int


class PlaceBase(SQLModel):
    title: str
    latitude: float
    longitude: float


class Place(PlaceBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    description: str | None = Field(default=None, max_length=500)
    picture_small_url: str = Field(max_length=255)
    picture_big_url: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class ConfigDict:
        arbitrary_types_allowed = True


class PlacePublic(PlaceBase):
    picture_small_url: str


class PlaceDetailPublic(PlaceBase):
    picture_big_url: str
    description: str | None


class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(SQLModel):
    sub: int | None = None


class Message(SQLModel):
    message: str
