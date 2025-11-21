import json
from openrouter import OpenRouter
from ..config import settings

class Knowledge:
  def __init__(self):
    self.sections = ["personal", "education", "projects", "work", "productivity", "goals", "philosophy"]
    self.client = OpenRouter(api_key=settings.openrouter_api_key)

  def search(self, query):
    pass

  async def index(self, content: str, section: str):
    question_prompt = f"""
    Given the following content about "{section}", generate a list of 5-10 distinct questions a user might ask.
    Format your response as a JSON array of strings.

    Content:
    {content}
    """
    
    question_response = await self.client.beta.responses.asend(
        model=settings.model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant that generates questions based on provided content."},
            {"role": "user", "content": question_prompt}
        ],
        response_format={"type": "json_object"}
    )
    
    try:
        generated_questions = json.loads(question_response.choices[0].message.content)
        if not isinstance(generated_questions, list) or not all(isinstance(q, str) for q in generated_questions):
            generated_questions = [question_response.choices[0].message.content]
    except json.JSONDecodeError:
        generated_questions = [question_response.choices[0].message.content]

    if generated_questions:
        embeddings_response = await self.client.embeddings.create(
            model="embed-english-v3.1",
            input=generated_questions
        )
        return {
            "section": section,
            "content": content,
            "indexed_questions": [
                {"question": q, "embedding": embeddings_response.data[i].embedding}
                for i, q in enumerate(generated_questions)
            ]
        }
    return None
