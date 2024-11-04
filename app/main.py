
from fastapi import  FastAPI
from . import models
from .database import  engine
from .routers import  user, auth, post, vote
from .config import settings

from fastapi.middleware.cors import CORSMiddleware



# create when start again - no longer need it
# models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# for everyone, at least for the testing porpuse
origins = [
#     "https://www.google.com",
#     "http://localhost",
#     "http://localhost:8080",
     "*"
 ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=[], # origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(vote.router)

@app.get("/")
async def root():
    return {"message": "Hello Sebas !!!"}


