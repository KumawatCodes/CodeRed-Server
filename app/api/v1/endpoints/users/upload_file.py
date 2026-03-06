import cloudinary.uploader
from fastapi import APIRouter,UploadFile,File,HTTPException
router = APIRouter()

@router.post("/upload-image")
async def upload_image(file:UploadFile = File(...)):
    if file.content_type not in ["image/jpeg","image/png"]:
        raise HTTPException(status_code=400,detail="Invalid image type")    
    result = cloudinary.uploader.upload(file.file)
    return {"image_url":result["secure_url"]}