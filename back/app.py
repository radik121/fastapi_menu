from fastapi import FastAPI
import uvicorn
from api import router


app = FastAPI(title='Menu')
app.include_router(router)


if __name__ == '__main__':
    uvicorn.run('app:app', reload=True)