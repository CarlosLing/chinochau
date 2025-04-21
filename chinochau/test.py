import pinyin
from pinyin.cedict import translate_word

with open("input.txt", "r") as f:
    raw = f.read().replace("- ", "")
    examples = raw.split("\n")

with open("output_pretty.txt", "w") as f:
    for example in examples:
        translations = translate_word(example)
        if translations is not None:
            translations = "\n - ".join(translations)
        f.write(f"{example}\n{pinyin.get(example)}\n - {translations}\n\n")

examples = list(set(examples))
with open("output.txt", "w") as f:
    for example in examples:
        translations = translate_word(example)
        if translations is not None:
            translations = "<br>".join(translations)
        f.write(f"{example};{pinyin.get(example)}<br><br><br>{translations}\n")
