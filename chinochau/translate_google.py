from typing import List
from pinyin.cedict import translate_word
from googletrans import Translator

example_input = "数不清的"
# Uncountable
# Example: 我花了数不清的时间
# (I have spent countless time)


async def translate_google(word: str) -> List[str]:
    async with Translator() as translator:
        definition = translate_word(word)
        if definition is None:
            print("Definition is none, querying Translation service")
            translation = await translator.translate(text=word, src="zh-CN", dest="en")
            return [translation.text]
        else:
            return definition


if __name__ == "__main__":
    import asyncio

    x = asyncio.run(translate_google(example_input))
    print(x)
