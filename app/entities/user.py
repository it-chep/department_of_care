from pydantic import BaseModel


class UserToWelcome(BaseModel):
    tg_id: int
    first_name: str
    username: str


