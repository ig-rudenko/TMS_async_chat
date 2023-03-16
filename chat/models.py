from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, select
from database import async_db_session, Base, ModelManagerMixin
from users.models import User


class Room(Base, ModelManagerMixin):
    __tablename__ = "rooms"
    __mapper_args__ = {"eager_defaults": True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)

    @classmethod
    async def all_rooms(cls) -> list:
        rooms = await async_db_session.execute(select(cls))
        result = [r[0] for r in rooms]
        return result

    async def all_messages(self) -> list:
        res = await Message.filter(room_id=self.id)
        return [await msg.as_dict() for msg in res]

    def __str__(self):
        return self.name


class Message(Base, ModelManagerMixin):
    __tablename__ = "messages"
    __mapper_args__ = {"eager_defaults": True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    room_id = Column(ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False, index=True)
    text = Column(Text())
    created_at = Column(DateTime())

    async def as_dict(self) -> dict:
        if self.user_id:
            user = await User.get(id=self.user_id)
            username = user.username
        else:
            username = None

        return {
            "text": self.text,                    # 20:22:59 16.03.2023
            "created_at": self.created_at.strftime("%H:%M:%S %d.%m.%Y"),
            "user": username,
        }
