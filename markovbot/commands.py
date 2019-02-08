import asyncio
import logging
import random
import math

import markovify

from discord.ext.commands import core

from markovbot import markovbot, datastore

log = logging.getLogger(__name__)


# TODO: I wonder if there is a way to extend the way the context is passed in, and we could add our server
# context as a property on that context object.
@markovbot.command(pass_context=True, help='Generate a Markov sentence based on the server chat history.')
async def say(context, user: str = None):
    server_context = context.server_context

    if not server_context.is_ready:
        await markovbot.say('I am still learning from all your messages. Try again later.')
        return

    if user is None:
        log.debug('Bot issued say command on server %s.',
                  server_context.server.name)
        sentence = server_context.markov.make_sentence_server()

        if sentence is None:
            await markovbot.say('Unable to generate message. This is probably due to a lack of messages on the server.')
            return

    else:
        db_user = datastore.get_server_user(server_context.server.id, user)

        if db_user is None:
            await markovbot.say('The user {} does not exist. Check your spelling and try again.'.format(user))
            return

        sentence = server_context.markov.make_sentence_user(db_user)

        if sentence is None:
            await markovbot.say('Unable to generate message for {}. This is probably because they have not sent enough messages.'.format(user))
            return

    await markovbot.say(sentence)


@markovbot.command(pass_context=True, help='Mock the last specified user message.')
async def mock(context, user: str = None):
    server_context = context.server_context

    if user is None:
        await markovbot.say('Please specify a user.')
        return

    else:
        targeted_user = None
        for member in server_context.server.members:
            if member.nick == user:
                targeted_user = member
            else:
                targeted_user = server_context.server.get_member_named(user)

        if targeted_user is None:
            await markovbot.say('Could not find user. Please try another user.')
            return

        targeted_user = server_context.server.get_member_named(user)
        logs_by_user = list()

        # Get messages from user in current channel
        async for message in markovbot.logs_from(context.message.channel, limit=500):
            if message.author.id == targeted_user.id and not message.content.startswith('!cancer'):
                logs_by_user.append(message)

        # Get latest message from user
        if not logs_by_user:
            await markovbot.say('User does not have any messages in this channel')
            return

        logs_by_user.sort(key=lambda message: message.timestamp, reverse=True)

        targeted_message = logs_by_user[0]
        sentence = mock_string(targeted_message.content)

        if sentence is None:
            await markovbot.say('No alphabetic letters were found in previous message. '
                                'Make sure {} uses letters in their message next time you weeb.'.format(user))
            return

        await markovbot.say(sentence)


def mock_string(sentence: str):
    char_count = len(sentence)

    # Subtract from char_count if not a letter
    for i in sentence:
        if not i.isalpha():
            char_count -= 1

    mock_count = math.ceil(char_count - char_count / 2)
    sentence_mock = list(sentence.lower())

    index = 0
    current_mock_count = 0
    loop_limit = 4
    while current_mock_count in range(0, mock_count) and loop_limit > 0:
        capitalize = bool(random.getrandbits(1))
        val = str(sentence_mock[index])
        # Don't want to count a char mutation for spaces / integers / capitals.
        if capitalize and sentence_mock[index] != ' ' and val.isalpha() and not (val.isdigit() or val.isupper()):
            sentence_mock[index] = sentence_mock[index].upper()
            current_mock_count += 1
        index += 1
        # Restart at beginning of string if mock_count is not met.
        # Only allow # of runs set in loop_limit above.
        if index == len(sentence_mock):
            index = 0
            loop_limit -= 1

    sentence = ''.join(str(e) for e in sentence_mock)

    if current_mock_count < 1:
        return None

    return sentence
