import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from router.visualizations_router import router as visualizations_router
from router.admin_router import router as admin_router

app = FastAPI()


@app.get("/healthcheck", include_in_schema=False)
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(visualizations_router)
app.include_router(admin_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run("main:app", host='0.0.0.0', port=8000, reload=True)

