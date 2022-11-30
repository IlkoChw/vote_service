from dataclasses import dataclass
from functools import reduce
import logging
import pickle
import redis
from texttable import Texttable
from typing import Any, List


@dataclass
class Vote:
    """Структура для удобного создания голосования"""

    redis_id: str
    title: str
    options: List[str]


class VoteService:
    """Сервис для голосования с хранилищем в redis"""

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not VoteService._instance:
            VoteService._instance = super(VoteService, cls).__new__(cls, *args, **kwargs)
        return VoteService._instance

    def __init__(self):
        self._storage = redis.Redis(host='redis', port=6379, db=0)

    def _set(self, key: str, value: Any):
        """Обертка для записи данных в хранилище"""

        self._storage.set(key, pickle.dumps(value))

    def _get(self, key: str) -> Any:
        """Обертка для получения данных из хранилища"""

        data = self._storage.get(key)
        if data is not None:
            return pickle.loads(data)

    # :param rewrite: Флаг для перезаписи голосования с таким же идентификатором.
    def add(self, vote: Vote, rewrite: bool = True):
        """Метод для добавления нового голосования в хранилище.

            :param vote: Объект голосования.
            :param rewrite: Если True записываем в хранилище новое голосование, иначе пробуем получить существующее.
        """

        options_dict = None
        if not rewrite:
            options_dict = self._get(vote.redis_id)
            print(f'Try to get vote "{vote.redis_id}": {options_dict}')

        if options_dict is None:
            options_dict = {i: {'title': answer, 'votes': 0} for i, answer in enumerate(vote.options, 1)}
            print(f'Created vote "{vote.redis_id}": {options_dict}')
            self._set(vote.redis_id, options_dict)

    def to_vote(self, vote: Vote, option_id: int):
        """Метод для начисления голоса конкретному варианту.

            :param vote: Объект голосования.
            :param option_id: Ключ варианта за который необходимо проголосовать.
        """

        options_dict = self._get(vote.redis_id)
        if options_dict is not None:
            try:
                options_dict[option_id]['votes'] += 1
                self._set(vote.redis_id, options_dict)
                print(f'Vote "{vote.redis_id}": Voted for {options_dict[option_id]["title"]}')
                return options_dict
            except KeyError:
                logging.error(f'Option id "{option_id}" not found!')
        else:
            print(f'vote "{vote.redis_id}" not found')

    def get_result(self, vote: Vote):
        """Метод вывода результатов в консоль.

            :param vote: Объект голосования.
        """

        options = self._get(vote.redis_id)
        if options is not None:
            votes_sum = reduce(lambda x, y: x + y['votes'], options.values(), 0)

            print('\n', vote.title)

            t = Texttable()
            t.add_rows([['Option', 'Percent', 'Votes']])

            for obj in options.values():
                percentage = obj['votes'] * 100 / votes_sum
                if percentage != 0:
                    perc_view = f'{int(percentage)}%' if percentage % int(percentage) == 0 else f'{percentage:.2f}%'
                else:
                    perc_view = f'{int(percentage)}%'

                t.add_row([obj["title"], perc_view, obj["votes"]])

            t.add_row(['', '', votes_sum])
            print(t.draw())
        else:
            logging.error(f'Result error: Vote "{vote.redis_id}" not found!')
