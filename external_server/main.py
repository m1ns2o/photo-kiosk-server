from fastapi import FastAPI, HTTPException, Request, UploadFile
from fastapi.templating import Jinja2Templates
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

templates = Jinja2Templates(directory="templates")

@app.get("/{addr}")
async def read_img(request: Request, addr: str):
    # 이미지를 DB에서 조회
    db_session = SessionLocal()
    image_record = db_session.query(Img).filter(Img.addr == addr).first()
    db_session.close()

    if not image_record:
        raise HTTPException(status_code=404, detail="Image not found")

    # 이미지의 경로를 템플릿에 전달
    return templates.TemplateResponse("index.html",
                                      {"request": request, "image_path": os.path.basename(image_record.addr)})

    # return templates.TemplateResponse("index.html", {"request": request, "image_path": image_record.img})

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
    file_uuid = str(uuid.uuid4())
    unique_filename = f"{file_uuid}.jpg"
    file_path = os.path.join(IMAGE_DIR, unique_filename).replace("\\", "/")
    print(unique_filename)
    print(file_path)
    # 이미지를 로컬 디렉토리에 .jpg 형식으로 저장
    with open(file_path, 'wb') as image_file:
        image_file.write(decoded_image_data)

    # 이미지 파일 경로를 DB에 저장
    db_session = SessionLocal()
    new_image = Img(img=file_uuid, addr=data.image_addr, date=datetime.datetime.utcnow())
    db_session.add(new_image)
    db_session.commit()
    db_session.refresh(new_image)
    db_session.close()

    return {"file_name": file_uuid}


@app.get("/img/{addr}")
def get_image_by_addr(addr: str):
    db_session = SessionLocal()
    #uuid를 db에 저장했기 때문에
    image_record = db_session.query(Img).filter(Img.addr == addr).first()
    db_session.close()

    if not image_record:
        raise HTTPException(status_code=404, detail="Image not found")
    # 이미지 파일을 FileResponse로 반환
    return FileResponse(IMAGE_DIR+"/"+image_record.img+".JPG", media_type="image/jpeg")

@app.post("/receive")
def receive_file(file: UploadFile):
    print('call')
    try:
        file_path = os.path.join(IMAGE_DIR, file.filename).replace("\\", "/")
        with open(file_path + ".mp4", "wb+") as buffer:
            buffer.write(file.file.read())
        return {"detail": "File received successfully."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"File receive failed: {str(e)}")


