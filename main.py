import openai
import telebot

from settings import *

bot = telebot.TeleBot(TOKEN)
openai.api_key = OPENAI_TOKEN
start_message = [{"role": "system", "content": "you are a very smart assistant bot"}]
role_now = "you are a very smart assistant bot"
history = {}
client = openai.OpenAI
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id,
                     "Привет! Это chatGPT бот.\nЭтот бот сам запоминает историю ваших запросов, чтобы начать диалог с чистого листа можете использовать команду /clean\nМожно поменять стиль бота написав команду /behavior и через пробел написать один из типов. Сейчас существуют такие типы: ученый, публицист, веселый. Например '/behavior ученый'")


@bot.message_handler(commands=['clean'])
def clean(message):
    history[str(message.chat.id)] = start_message.copy()
    bot.send_message(message.chat.id, "История стерта!")

@bot.message_handler(commands=['sand_info'])
def sand_info(message):
    with open('data_base.txt', 'r') as f:
        bot.send_document(message.chat.id, f)



@bot.message_handler(commands=['info'])
def info(message):
    with open("data_base.txt", 'r') as f:
        s = f.read().split('\n')
        un = {}
        print(s)
        for i in reversed(s):
            print(i.split())
            try:
                if not i.split()[0] in un.keys():
                    un[f'{i.split()[0]}'] =  f'{i.split()[1]} {i.split()[2]} {i.split()[3]} {i.split()[4]}'
                    print(un)
            except IndexError:
                continue
        response = ''
        for i in un.keys():
            y = un[i]
            response+=f'@{y}\n'
        bot.send_message(message.chat.id, text = response)


@bot.message_handler(commands=['null'])
def null(message):
    with open("data_base.txt", 'w') as f:
        f.write(f"{message.chat.id} {message.from_user.username} {message.from_user.first_name} 0\n")
    bot.send_message(message.chat.id, "Обнулено!")


@bot.message_handler(commands=['behavior'])
def behavior(message):
    try:
        txt = message.text.lower().split()[1]
        if txt == "ученый":
            history[str(message.chat.id)][0] = {"role": "system", "content": "you are a very smart assistant bot"}
            response = "Выбран режим бота ученого!"
        elif txt == 'веселый':
            history[str(message.chat.id)][0] = {"role": "system", "content": "you are a very funny assistant bot"}
            response = "Выбран режим веселого бота!"
        elif txt == "публицист":
            history[str(message.chat.id)][0] = {"role": "system", "content": "you are a bot publicist"}
            response = "Выбран режим бота публициста!"
        else:
            response = "Пока нет такого режима! Оставлен старый режим.\nСейчас существуют такие типы: ученый, публицист, веселый."
    except IndexError:
        response = "Не введен режим :("
    bot.send_message(message.chat.id, text=response)


@bot.message_handler(content_types='text')
def main(message):
    if not str(message.chat.id) in history.keys():
        if str(message.text) == 'parolotbota':
            history[str(message.chat.id)] = start_message.copy()
        else:
            bot.send_message(message.chat.id, text="Не авторизованный пользователь")
    else:

        history[str(message.chat.id)].append({'role': 'user', 'content': message.text})
        print(history)

        try:
            completions = client.chat.completions.create(
                model='gpt-3.5-turbo',
                messages=history[str(message.chat.id)],
            )
            response = completions['choices'][0]['message']['content']
            history[str(message.chat.id)].append({'role': 'assistant', 'content': response})
            if str(message.chat.id)!='681930364':
                with open("data_base.txt", 'r') as f:
                    strings = f.read().split("\n")
                    for s in reversed(strings):
                        if f"{message.chat.id}" in s:
                            print(int(completions["usage"]["total_tokens"]))
                            count = int(s.split()[-1]) + int(completions["usage"]["total_tokens"])
                            break
                    else:
                        count = int(completions["usage"]["total_tokens"])
                with open("data_base.txt", 'a') as f:
                    f.write(f"\n{message.chat.id} {message.from_user.username} {message.from_user.first_name} {count}\n")
                # print(completions["usage"]["total_tokens"])
        except BaseException as e:
            response = 'Попробуйте еще раз'
            # if "overloaded with other requests" in e:
            #     response = "Модель перегружена, попробуйте позже"
            print(e)
        bot.send_message(message.chat.id, text=response)
        print(history)



print('Let`s go!')

bot.infinity_polling()
