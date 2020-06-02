import re


async def check_if_spelled_right(redis, words: list, english_dict: str = "dict:all") -> list:
    wrong_words = []
    for word in words:
        if not await redis.sismember(english_dict, word) and re.match(
                '^[a-z]*$', word
        ):
            print(word)
            wrong_words.append(word)
    return wrong_words
