import cloudinary.uploader
from app.core.exceptions import InvalidImageTypeError, FileTooLargeError
import logging

logger = logging.getLogger(__name__)

class UploadServices:

    MAX_SIZE = 5*1024*1024
    ALLOWED_TYPES = ["image/png","image/jpg"]

    @staticmethod
    async def upload_profile_pic(file) -> str:
        """
        uploading profile pic in cloudinary
        Args:
            file = profile pic of user
        Returns:
            image_url = cloudinary url of pic
        """

        logger.info("getting url of profile pic after uploading image")

        if file.content_type not in UploadServices.ALLOWED_TYPES:
            raise InvalidImageTypeError()

        content = await file.read()

        if len(content) > UploadServices.MAX_SIZE:
            raise FileTooLargeError()
        
        file.file.seek(0)
        
        result = cloudinary.uploader.upload(file.file)
        image_url = result["secure_url"]

        logger.info("successfully get the image url")
        return image_url


        