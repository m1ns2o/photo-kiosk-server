from fastapi import FastAPI, HTTPException, Depends, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import sessionmaker
import base64
import datetime
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os
import uuid
from models import Img, engine  # model.py에서 필요한 부분을 가져옵니다.
import json

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

# 이미지를 로컬 디렉토리에 저장하기 위한 경로 설정
IMAGE_DIR = ""

@app.on_event("startup")
async def run_on_startup():
    with open('settings.json', 'r') as file:
        data = json.load(file)
    global IMAGE_DIR
    IMAGE_DIR = data["dir"]
    if not os.path.exists(IMAGE_DIR):
        os.makedirs(IMAGE_DIR)


@app.post("/save")
async def save_image_async(data: ImageData):
    image_data = data.image_data.split(",")[1]
    decoded_image_data = base64.b64decode(image_data)

    # 고유한 .jpg 파일 이름 생성
    unique_filename = f"{uuid.uuid4()}.jpg"
    file_path = os.path.join(IMAGE_DIR, unique_filename).replace("\\", "/")
    print(unique_filename)
    print(file_path)
    # 이미지를 로컬 디렉토리에 .jpg 형식으로 저장
    with open(file_path, 'wb') as image_file:
        image_file.write(decoded_image_data)

    # 이미지 파일 경로를 DB에 저장
    db_session = SessionLocal()
    new_image = Img(img=file_path, addr=data.image_addr, date=datetime.datetime.utcnow())
    db_session.add(new_image)
    db_session.commit()
    db_session.refresh(new_image)
    db_session.close()

    return {"id": new_image.id}


@app.get("/img/{addr}")
def get_image_by_addr(addr: str):
    db_session = SessionLocal()
    image_record = db_session.query(Img).filter(Img.addr == addr).first()
    db_session.close()

    if not image_record:
        raise HTTPException(status_code=404, detail="Image not found")

    # 이미지 파일을 FileResponse로 반환
    return FileResponse(image_record.img, media_type="image/jpeg")