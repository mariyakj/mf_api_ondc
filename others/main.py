from fastapi import FastAPI
from tasks import search, select, submit_form

app = FastAPI()

@app.get("/search")
def trigger_search():
    search.delay()  # Run search task in background
    return {"message": "Search started"}

@app.get("/select")
def trigger_select():
    select.delay()  # Run select task in background
    return {"message": "Select started"}

@app.get("/submit")
def trigger_submit():
    submit_form.delay()  # Run submit form task in background
    return {"message": "Submit started"}
