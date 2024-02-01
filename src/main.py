from fastapi import FastAPI
from routers import pvt_router
import uvicorn
from config import server_settings

app = FastAPI()
app.include_router(pvt_router)


if __name__ == "__main__":
    uvicorn.run(
        "main:app", host=server_settings.host, port=server_settings.port, reload=True
    )
