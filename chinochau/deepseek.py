from openai import OpenAI

# TODO: Use langchain to enforce stricter typing. -> Get a list of examples instead of a string
with open("api_key.txt", "r") as f:
    key = f.read()

client = OpenAI(api_key=key, base_url="https://api.deepseek.com")


def get_examples_deepseek(word: str, number_of_examples: int = 2):

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {
                "role": "system",
                "content": f"你是一位中文教师，面向HSK4水平的学生。当学生给出一个词语时，你需用中文回复{number_of_examples}个不同的例句来演示该词的用法。每个例句单独一行，不要编号。不要使用拼音、英语或任何额外解释，仅提供符合HSK4水平的例句",
            },
            {"role": "user", "content": word},
        ],
        stream=False,
    )

    return response.choices[0].message.content


if __name__ == "__main__":
    sample_word = "提供"
    example = get_examples_deepseek(sample_word)
    print(sample_word)
    print(example)
