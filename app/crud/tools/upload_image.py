import cloudinary
import cloudinary.uploader
import cloudinary.api
cloudinary.config(
    cloud_name="dagw7pro6",
    api_key="886223283645899",
    api_secret="mxPv-VTh8V4viM4nqmxJDQjzXvc"
)


def upload_image_to_cloudinary(image, name):
    # Upload the image to Cloudinary
    result = cloudinary.uploader.upload(
        image, public_id=name
    )
    image_url = result['url']

    return image_url


def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
