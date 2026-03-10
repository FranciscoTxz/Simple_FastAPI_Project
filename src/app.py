from fastapi.concurrency import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import user_r, project_r2, project_r, docuemnt_r
from services import DatabaseConnection
from commons.exceptions_handler import register_exception_handlers


@asynccontextmanager
async def lifespan(app: FastAPI):
    await DatabaseConnection().connect()
    yield
    await DatabaseConnection().disconnect()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,  # ty:ignore
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH", "PUT", "DELETE"],
    allow_headers=["*"],
)

register_exception_handlers(app)

app.include_router(user_r)
app.include_router(project_r2)
app.include_router(project_r)
app.include_router(docuemnt_r)


@app.get("/")
def read_root():
    """Returns Hello World."""
    return {"Hello": "World! :,)"}
