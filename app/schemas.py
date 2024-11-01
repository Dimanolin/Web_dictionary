from pydantic import BaseModel

class WordCreate(BaseModel):
    word: str
    definition: str