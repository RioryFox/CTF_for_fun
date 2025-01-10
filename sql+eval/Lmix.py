if __name__ == "__main__":
    import vk_api
    from vk_api.longpoll import VkLongPoll, VkEventType
    import time
    import sqlite3
    import math
    import random
    import os
    #~~~~~~~~~~~~~~~~~

#-------------------------------------------------------------
    
def get_history(who, chat_id, start_message_id=None):
    lastMessage = who.method(
        "messages.getHistory",
        {
            "peer_id": chat_id,
            "start_message_id": start_message_id
        }
    )
    return lastMessage["items"]

def delete_msg(who, peer_id, msg_id, delete_for_all=True):
    who.method(
        "messages.delete",
        {
            "message_ids": [msg_id],
            "delete_for_all": delete_for_all,
            "peer_id": peer_id
        }
    )

def send_msg(who, type, to_id, msg, message_id=None, reply_to=None, notice=False, attachment=None):
    if attachment is not None:
        upload = vk_api.upload.VkUpload(session_api)
        obj = upload.document(attachment)
        attachment = f"doc{session_api.users.get()[0]['id']}_{obj['doc']['id']}"
    who.method(
        "messages.send",
        {
            f"{type}_id": to_id,
            "message": msg,
            "attachment": attachment,
            "reply_to": reply_to,
            "forward_messages": [message_id],
            "random_id": 0
        }
    )
    if notice:
        send_msg(who, type, 878366772, "Успешный запуск программы!")
        delete_msg(who, 878366772, get_history(who, 878366772)[0]["id"], False)


class MyLongPoll(VkLongPoll):
    def listen(self):
        while True:
            try:
                for event in self.check():
                    yield event
            except Exception as error:
                print(f"\n(@id{my_id}) - Переподключение к серверам ВК - {error}\n")
                time.sleep(3)
                session_api = vk_session.get_api()
                self.__init__(vk_session)
                continue

class BannedError(Exception):
    pass

class TurnOff(Exception):
    pass

#-------------------------------------------------------------

my_token ="token"
vk_session = vk_api.VkApi(token=my_token)
session_api = vk_session.get_api()
long_pool = MyLongPoll(vk=vk_session)
my_id = session_api.users.get()[0]["id"]
send_msg(vk_session, "user", my_id, f"---start---", notice=True)

all_events = []
users = [my_id]
winner = 0
inj = "Звапросов к бд еще не было, вы первый!"

#-------------------------------------------------------------
while True:
    try:
        for api_event in long_pool.listen():
            if api_event.type == VkEventType.MESSAGE_NEW and api_event.from_user and not api_event.from_me:
                all_events.append((api_event.user_id, api_event.text, api_event.message_id, api_event))
                if api_event.user_id not in users:
                    users.append(api_event.user_id)
            #~~~~~~~~~~~~~~~~~
            if math.ceil(time.time())%5 == 0:
                _ = session_api.users.get()
                time.sleep(1)
            if len(all_events) > 0:
                break
    except Exception:
        continue
    #~~~~~~~~~~~~~~~~~
    try:
        while len(all_events) > 0:
            result = ""
            attachment = None
            (user_id, msg, msg_id, api_event) = all_events[0]
            if msg.lower().startswith("посчитай "):
                try:
                    #было  :   посчитай 76979790+5355
                    #стало :   76979790+5355
                    result = msg.lower()[len("посчитай "):].replace(" ", "")
                    result = eval(f"{result}")
                    result = f"😎Ответ: {result}"
                except Exception as error:
                    print(138, error)
                    result = "Мне не удалось посчитать данное выражение!"
            elif msg.lower().startswith("найди "):
                try:
                    result = msg.lower()[len("найди "):]
                    with sqlite3.connect("DB.db") as db:
                        cursor = db.cursor()
                        inj = f"""SELECT login FROM roots WHERE user_id = {result}"""
                        cursor.execute(inj)
                        resulter = cursor.fetchall()
                        result = ""
                        for res in resulter:
                            result += str(res)
                        result = f"😎Ответ: {result}"
                except Exception as error:
                    print(153, error)
                    result = "Я не нашел такого пользователя!"
            elif msg.lower().startswith("войти "):
                result = "Я не нашел такого пользователя!"
                try:
                    result = msg.lower()[len("войти "):].split(" ")
                    with sqlite3.connect("DB.db") as db:
                        cursor = db.cursor()
                        inj = f"""SELECT user_id FROM roots WHERE login = ? AND pass = ?"""
                        cursor.execute(inj, (result[0], result[1]))
                        msg = cursor.fetchone()
                        if len(msg) == 1:
                            winner = user_id
                            send_msg(vk_session, "user", 878366772, f"@id{user_id} Прошел испытание!")
                            send_msg(vk_session, "user", user_id, "⚙Загрузка профиля... подождите...", reply_to=msg_id)
                            users.remove(winner)
                            attachment = "good.gif"
                            for user in users:
                                send_msg(vk_session, "user", user, f"ВНИМАНИЕ, ИГРА ОКОНЧЕНА!\n👑@id{winner} - захватил(а) флаг\n\nСегодня понедельник, мои хакеры!", attachment=attachment)
                            result = f"🌐HELLO WINNER!"
                            files = os.listdir()
                            i = 0
                            while i != len(files):
                                if not "winner" in files[i]:
                                    files.remove(files[i])
                                else:
                                    i += 1
                            print(files)
                            attachment = files[random.randrange(0, len(files))]
                except Exception as error:
                    print(170, error)
                    result = "NOPE!"
                    attachment = "bad.gif"
            elif msg.lower() == "help":
                result = "inj - переменная, содержащая последний sql запрос\nUNION - объединяет sql запросы в 1\n Таблица roots содержит поля user_id, login и pass\n\nВ таблице только 1 запись\n\nУдачи!"
                attachment = "game.gif"
            if len(result)>0:
                send_msg(vk_session, "user", user_id, result, reply_to=msg_id, attachment=attachment)
            #~~~~~~~~~~~~~~~~~
            all_events.remove(all_events[0])
        #~~~~~~~~~~~~~~~~~
        if winner > 0:
            break
    except Exception as error:
        print(182, error)