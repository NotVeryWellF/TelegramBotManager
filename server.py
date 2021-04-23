import uvicorn
import config

if __name__ == "__main__":
    uvicorn.run("backend.api.api:app", host=config.HOST, port=config.PORT, reload=True)