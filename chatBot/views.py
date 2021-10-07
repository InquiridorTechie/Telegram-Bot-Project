from django.views import generic
from django.views.decorators.csrf import csrf_exempt
import json
import requests
import random
from django.utils.decorators import method_decorator
from django.http.response import HttpResponse

from count_calls.models import User_Model


class TelegramBotView(generic.View):
    '''
    csrf_exempt is necessary because the request
    comes from the Telegram server.
    '''

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        print(request)
        return generic.View.dispatch(self, request, *args, **kwargs)

    # Post function to handle messages in whatever format they come
    def post(self, request, *args, **kwargs):
        TELEGRAM_TOKEN = "<Telegram Bot Token>";

        message = get_message_from_request(request)
        print(message)
        send_messages(message, TELEGRAM_TOKEN)

        return HttpResponse()


def get_message_from_request(request):
    received_message = {}
    decoded_request = json.loads(request.body.decode('utf-8'))

    if 'message' in decoded_request:
        received_message = decoded_request['message']

    return received_message


def send_messages(message, token):
    # Ideally process message in some way. For now, let's just respond

    User = User_Model.objects.all()
    result_message = {}

    user_id = message['from']['id']
    user_name = message['chat']['first_name']
    fat, stupid, dumb = 0, 0, 0
    userExist = False

    if User.filter(user_id=user_id).exists():
        user = User.get(user_id=user_id)
        fat = user.fat_count
        stupid = user.stupid_count
        dumb = user.dumb_count
        userExist = True

    jokes = {
        'stupid': ["""Yo' Mama is so stupid, she needs a recipe to make ice cubes.""",
                   """Yo' Mama is so stupid, she thinks DNA is the National Dyslexics Association."""],
        'fat':    ["""Yo' Mama is so fat, when she goes to a restaurant, instead of a menu, she gets an estimate.""",
                   """ Yo' Mama is so fat, when the cops see her on a street corner, they yell, "Hey you guys, break it up!" """],
        'dumb':   ["""THis is fun""",
                   """THis isn't fun"""],
        '/start': 'Hello Welcome to Yo Mama Jokes.'
    }

    post_message_url = "https://api.telegram.org/bot{0}/sendMessage".format(
        token)

    '''
    The response needs to contain just a chat_id
    and text field for  telegram to accept it.
    '''

    result_message['chat_id'] = message['chat']['id']
    keyword = message.get('text')

    if keyword:
        result_message['text'] = random.choice(jokes[keyword])
    else:
        result_message['text'] = "I don't know any responses for that. If you're interested in yo mama jokes tell me fat, stupid or dumb."

    fat = fat + 1 if keyword == 'fat' else fat
    stupid = stupid + 1 if keyword == 'stupid' else stupid
    dumb = dumb + 1 if keyword == 'dumb' else dumb

    reply_markup = {
                 'keyboard': [['fat'], ['dumb'], ['stupid']],
                 'resize_keyboard': True, 'one_time_keyboard': True
                }

    result_message['reply_markup'] = json.dumps(reply_markup)

    response_msg = json.dumps(result_message)
    requests.post(post_message_url, headers={
        "Content-Type": "application/json"}, data=response_msg)

    if userExist:
        User.filter(user_id=user_id).update(
            fat_count=fat,
            stupid_count=stupid,
            dumb_count=dumb
        )

    else:
        User_Model(
            user_id=user_id,
            user_name=user_name,
            fat_count=fat,
            stupid_count=stupid,
            dumb_count=dumb
        ).save()
