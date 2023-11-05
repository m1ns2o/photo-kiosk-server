from fastapi import FastAPI, HTTPException, Request, UploadFile
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy.orm import sessionmaker
import base64
from datetime import datetime, timedelta
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os
import uuid
from models import Img, engine
import json
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import timezone

SessionLocal = sessionmaker(bind=engine)

app = FastAPI()




app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def db_clear():
    db_session = SessionLocal()
    try:
        three_days_ago = datetime.now(timezone('Asia/Seoul')) - timedelta(days=3)
        image_records = db_session.query(Img).filter(Img.date <= three_days_ago).all()
        for record in image_records:
            file_path = IMAGE_DIR + record.img
            img_file = file_path+".jpg"
            mp4_file = file_path+".mp4"
            if os.path.exists(img_file):
                os.remove(img_file)
            if os.path.exists(mp4_file):
                os.remove(mp4_file)
            db_session.delete(record)
        # image_records.delete(synchronize_session='fetch')
        db_session.commit()
    finally:
        db_session.close()


scheduler = BackgroundScheduler()
scheduler.add_job(db_clear, trigger="interval", hours=1)  # 30초마다 실행
# scheduler.add_job(job_function, trigger="cron", hour=17, minute=30)  # 매일 오후 5시 30분에 실행

scheduler.start()

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
                                      {"request": request, "image_path": image_record.img})

    # return templates.TemplateResponse("index.html", {"request": request, "image_path": image_record.img})

@app.on_event("startup")
async def run_on_startup():
    with open('settings.json', 'r') as file:
        data = json.load(file)
    global IMAGE_DIR
    IMAGE_DIR = data["dir"]
    if not os.path.exists(IMAGE_DIR):
        os.makedirs(IMAGE_DIR)
    db_clear()


@app.post("/save")
async def save_image_async(data: ImageData):
    image_data = data.image_data.split(",")[1]
    decoded_image_data = base64.b64decode(image_data)

    # 고유한 .jpg 파일 이름 생성
    file_uuid = str(uuid.uuid4())
    unique_filename = f"{file_uuid}.jpg"
    # file_path = os.path.join(IMAGE_DIR[:-1], unique_filename).replace("\\", "/")
    file_path = IMAGE_DIR + unique_filename
    print(unique_filename)
    print(file_path)
    # 이미지를 로컬 디렉토리에 .jpg 형식으로 저장
    with open(file_path, 'wb') as image_file:
        image_file.write(decoded_image_data)

    # 이미지 파일 경로를 DB에 저장
    db_session = SessionLocal()
    new_image = Img(img=file_uuid, addr=data.image_addr, date=datetime.now(timezone('Asia/Seoul')))
    db_session.add(new_image)
    db_session.commit()
    db_session.refresh(new_image)
    db_session.close()

    return {"file_name": file_uuid}


# @app.get("/img/{addr}")
# def get_image_by_addr(addr: str):
#     db_session = SessionLocal()
#     #uuid를 db에 저장했기 때문에
#     image_record = db_session.query(Img).filter(Img.addr == addr).first()
#     db_session.close()
#
#     if not image_record:
#         raise HTTPException(status_code=404, detail="Image not found")
#     # 이미지 파일을 FileResponse로 반환
#     return FileResponse(IMAGE_DIR+"/"+image_record.img+".JPG")


@app.get("/download/{file_name}")
async def download_file(file_name: str):
    file_path = IMAGE_DIR + file_name  # 실제 파일 경로 지정
    return FileResponse(file_path, headers={"Content-Disposition": f"attachment; filename={file_name}"})


@app.post("/receive")
def receive_file(file: UploadFile):
    print('call')
    try:
        # file_path = os.path.join(IMAGE_DIR[:-1], file.filename).replace("\\", "/")
        file_path = IMAGE_DIR + file.filename
        with open(file_path + ".mp4", "wb+") as buffer:
            buffer.write(file.file.read())
        return {"detail": "File received successfully."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"File receive failed: {str(e)}")


