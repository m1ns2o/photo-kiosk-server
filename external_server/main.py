from fastapi import FastAPI
from pydantic import BaseModel
import base64
import aiofiles
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173"],  # 모든 출처를 허용하거나 특정 도메인들의 리스트를 제공하십시오.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ImageData(BaseModel):
    file_name: str
    image_data: str
@app.post("/save")
async def save_image_async(data:ImageData):
    image_data = data.image_data.split(",")[1]
    image_data += "=" * ((4 - len(image_data) % 4) % 4)
    async with aiofiles.open(data.file_name, "wb") as f:
        await f.write(base64.b64decode(image_data))
    return {"message": "Image saved successfully!"}
