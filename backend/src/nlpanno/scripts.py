import uvicorn
import nlpanno.server
import nlpanno.database
import uvicorn


app = None


def start_server(db: nlpanno.database.Database, port: int = 8000):
    global app
    app = nlpanno.server.create_app(port, db)
    uvicorn.run("nlpanno.scripts:app")
