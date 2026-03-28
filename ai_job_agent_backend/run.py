try:
    import uvicorn
except ModuleNotFoundError:
    raise SystemExit(
        "缺少依赖 uvicorn。请先执行：\n"
        "1) .\\start_backend.ps1\n"
        "或 2) python -m pip install -r requirements.txt"
    )


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8010,
        reload=True,
    )
