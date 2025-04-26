from clients.postgres import Database
from app.entities.user import UserToWelcome


class Repository:

    def __init__(self):
        self.db = Database()

    def check_user_welcome(self, tg_id: int) -> bool:
        """Возвращает флаг о том что пользователя приветствовали в чате"""
        query = """
            select 1 from user_welcomes where tg_id = %s;
        """

        try:
            result = self.db.select(query, (tg_id,))
            if len(result) == 1:
                return True
        except Exception as e:
            print(f"Error fetching Instagram channels: {str(e)}")
            raise

    def create_new_welcome(self, user: UserToWelcome):
        """
       Сохраняет информацию о отправленном приветствии пользователю
       :param user: Данные пользователя
       :return: True если запись успешно создана
       """

        query = """
            insert into user_welcomes (tg_id, first_name, username) VALUES ( %s, %s, %s);
            """

        try:
            self.db.execute(query, (user.tg_id, user.first_name, user.username))
        except Exception as e:
            print(f"Error saving welcome: {e}")
            return False
