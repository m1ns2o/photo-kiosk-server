from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import sessionmaker
import base64
# import aiofiles
import io
import datetime
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from models import Img, engine  # model.py에서 필요한 부분을 가져옵니다.

SessionLocal = sessionmaker(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ImageData(BaseModel):
    image_addr: str #이미지 qr코드 주소
    image_data: str #파일 이미지

@app.post("/")
def test():
    return {"message": "test"}

@app.post("/save")
async def save_image_async(data: ImageData):
    image_data = data.image_data.split(",")[1]
    decoded_image_data = base64.b64decode(image_data)
    # 이미지를 DB에 저장
    db_session = SessionLocal()
    new_image = Img(img=decoded_image_data, addr=data.image_addr, date=datetime.datetime.utcnow())
    db_session.add(new_image)
    db_session.commit()
    db_session.refresh(new_image)
    db_session.close()
    return {"id": new_image.id}


@app.get("/img/{addr}")
def get_image_by_addr(addr: str):
    # 데이터베이스에서 주어진 addr 값으로 이미지를 검색
    db_session = SessionLocal()
    image_record = db_session.query(Img).filter(Img.addr == addr).first()
    db_session.close()

    if not image_record:
        raise HTTPException(status_code=404, detail="Image not found")

    # 이미지 데이터를 응답으로 반환
    return StreamingResponse(io.BytesIO(image_record.img), media_type="image/jpeg")
