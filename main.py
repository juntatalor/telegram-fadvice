from tornado import gen, ioloop
from telezombie import api
from urllib.parse import quote
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
import re
import json

from api_token import API_TOKEN


class FAdvice(api.TeleLich):
    TAGS = ['дизайнеру', 'кодеру', 'верстальщику', 'фотографу', 'копирайтеру', 'маркетологу', 'сеошнику', 'водителю',
            'музыканту', 'фокуснику', 'врачу', 'студенту', 'за жизнь', 'для него', 'для неё']

    fa = re.compile(r'(/fa)|(@fadvicebot)')
    hlp = re.compile(r'help')
    tgs = re.compile('(' + ')|('.join(TAGS) + ')')

    def __init__(self, api_token):
        super(FAdvice, self).__init__(api_token)

    @gen.coroutine
    def on_text(self, message):

        lt = message.text.lower()

        fa = self.fa.search(lt)
        if not fa:
            # Не принимаем команды для других ботов
            return

        hlp, tgs = self.hlp.search(lt), self.tgs.search(lt)

        if hlp:
            # /fa help (@FAdviceBot help) - список категорий
            m = 'Ты можешь получить охуенный, блять, совет просто так (/fa, @FAdviceBot)\n' \
                'или по тегам (/fa тег, @FAdviceBot тег): \n' + ', '.join(self.TAGS)
        else:
            if tgs:
                # /fa категория (@FAdviceBot категория) - совет по категории
                tag = lt[slice(*tgs.span())]
                request = Request('http://fucking-great-advice.ru/api/random_by_tag/%s' % quote(tag))
            else:
                # /fa (@FAdviceBot) - случайный совет
                request = Request('http://fucking-great-advice.ru/api/random')

            try:
                response = urlopen(request)
            except (HTTPError, URLError):
                # ToDo: вероятно, стоит как-то обрабатывать ошибку
                return

            try:
                data = response.read().decode('utf-8')
                m = json.loads(data)['text']
                # Пост обработка. Сервис иногда выдает html
                m = m.replace('&nbsp;', ' ')
            except (ValueError, KeyError):
                # ToDo: вероятно, стоит как-то обрабатывать ошибку
                return

        yield self.send_message(message.chat.id_, m)


@gen.coroutine
def forever():
    f_advice = FAdvice(API_TOKEN)

    yield f_advice.poll()


if __name__ == "__main__":
    main_loop = ioloop.IOLoop.instance()
    main_loop.run_sync(forever)
