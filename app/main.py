from fastapi import FastAPI, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from . import database, models, schemas

app = FastAPI()

#Создание таблиц
models.Base.metadata.create_all(bind = database.engine)
templates = Jinja2Templates(directory = "templates")

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, db: Session = Depends(database.get_db)):
    word_count = db.query(models.DictionaryWord).count()  # Подсчет слов
    return templates.TemplateResponse("index.html", {"request": request, "word_count": word_count})  # Передача в шаблон

@app.get("/search_word", response_class = HTMLResponse)
async def search_word(request: Request, query: str, db: Session = Depends(database.get_db)):
    results = db.query(models.DictionaryWord).filter(models.DictionaryWord.word.ilike(f"%{query}%")).all()
    return templates.TemplateResponse("result.html", {"request": request, "results": results})

@app.post("/add_word", response_class = HTMLResponse)
async def add_word(request: Request, word: str = Form(...), definition: str = Form(...), db: Session = Depends(database.get_db)):
    #Проверка на существование слова в базе
    existing_word = db.query(models.DictionaryWord).filter(models.DictionaryWord.word == word).first()
    if existing_word:
        message = "Слово уже есть в базе данных"
        #raise HTTPException(status_code = 400, detail = "Это слово уже есть в базе данных.")
    else:
    #Создание нового объекта слова
        new_word = models.DictionaryWord(word = word, definition = definition)
        db.add(new_word)
        db.commit()
        db.refresh(new_word)
        message = "Слово успешно добавлено"
    return templates.TemplateResponse("index.html", {"request": request, "message": message})

@app.post("/delete_word", response_class = HTMLResponse)
async def delete_word(request: Request, word_id: int = Form(...), db: Session = Depends(database.get_db)):
    word_to_delete = db.query(models.DictionaryWord).filter(models.DictionaryWord.id == word_id).first()
    if not word_to_delete:
        raise HTTPException(status_code=404, detail="Слово не найдено")
    db.delete(word_to_delete)
    db.commit()
    message = "Слово успешно удалено"
    return templates.TemplateResponse("index.html", {"request": request, "message": message})

# Форма для редактирования слова
@app.get("/edit_word/{word_id}", response_class=HTMLResponse)
async def edit_word(request: Request, word_id: int, db: Session = Depends(database.get_db)):
    word = db.query(models.DictionaryWord).filter(models.DictionaryWord.id == word_id).first()
    if not word:
        raise HTTPException(status_code=404, detail="Слово не найдено")
    return templates.TemplateResponse("edit_word.html", {"request": request, "word": word})

# Обработка редактирования слова
@app.post("/update_word/{word_id}", response_class=HTMLResponse)
async def update_word(request: Request, word_id: int, word: str = Form(...), definition: str = Form(...), db: Session = Depends(database.get_db)):
    db_word = db.query(models.DictionaryWord).filter(models.DictionaryWord.id == word_id).first()
    if not db_word:
        raise HTTPException(status_code=404, detail="Слово не найдено")

    db_word.word = word
    db_word.definition = definition
    db.commit()
    return templates.TemplateResponse("index.html", {"request": request, "message": "Слово успешно изменено!"})