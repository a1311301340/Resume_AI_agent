from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.agent import router as agent_router
from app.api.v1.export import result_export_router, router as export_router
from app.api.v1.health import router as health_router
from app.api.v1.history import router as history_router
from app.api.v1.process import router as process_router
from app.api.v1.result import router as result_router
from app.api.v1.task import router as task_router
from app.api.v1.upload import router as upload_router
from app.core.errors import register_exception_handlers
from app.core.settings import settings

app = FastAPI(
    title="AI Job Agent Backend",
    description="AI 求职助手后端服务",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

prefix = settings.API_PREFIX
app.include_router(upload_router, prefix=prefix)
app.include_router(process_router, prefix=prefix)
app.include_router(result_router, prefix=prefix)
app.include_router(export_router, prefix=prefix)
app.include_router(result_export_router, prefix=prefix)
app.include_router(agent_router, prefix=prefix)
app.include_router(task_router, prefix=prefix)
app.include_router(history_router, prefix=prefix)
app.include_router(health_router, prefix=prefix)


@app.get("/")
def root():
    return {"message": "AI 求职助手后端服务运行中"}
