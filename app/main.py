from random import randint
from service import Vote, VoteService


def scenario_1(vote_service: VoteService):
    """Демонстрационный сценарий процесса голосования со случайным распределением голосов"""

    vote = Vote(
        redis_id='new_president',
        title='Who will be the new US President?',
        options=[
            'Kanye West',
            'Kim Jong-un',
            'Rick Sanchez',
        ]
    )

    vote_service.add(vote)

    for i in range(randint(5, 15)):
        vote_service.to_vote(vote, randint(1, len(vote.options)))

    vote_service.get_result(vote)


if __name__ == '__main__':
    vote_service_instance = VoteService()
    scenario_1(vote_service_instance)
