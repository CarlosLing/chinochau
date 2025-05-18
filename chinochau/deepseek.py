# Use langchain for structured output parsing
from openai import OpenAI
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

with open("api_key.txt", "r") as f:
    key = f.read().strip()

client = OpenAI(api_key=key, base_url="https://api.deepseek.com")



# Define a Pydantic model for structured output
class ExampleOutput(BaseModel):
    examples: list[str] = Field(..., description="A list of example sentences in Chinese.")

parser = PydanticOutputParser(pydantic_object=ExampleOutput)

def get_examples_deepseek(word: str, number_of_examples: int = 2) -> list[str]:
    prompt = (
        f"你是一位中文教师，面向HSK4水平的学生。当学生给出一个词语时，你需用中文回复{number_of_examples}个不同的例句来演示该词的用法。"
        "请以JSON格式输出，键为'examples'，值为例句组成的数组。不要编号，不要拼音、英语或任何额外解释。"
    )
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": word},
        ],
        stream=False,
        response_format={"type": "json_object"},
    )
    content = response.choices[0].message.content
    # Parse the output using langchain's PydanticOutputParser
    parsed = parser.parse(content)
    return parsed.examples



if __name__ == "__main__":
    sample_word = "提供"
    examples = get_examples_deepseek(sample_word)
    print(sample_word)
    for ex in examples:
        print(ex)
