from fastapi import FastAPI
import uvicorn
from api import router


app = FastAPI(
    title='Menu',
    docs_url='/api/v1/docs',
    redoc_url='/api/v1/redoc'
    )

app.include_router(router)


if __name__ == '__main__':
    uvicorn.run('app:app', host='0.0.0.0', reload=True)