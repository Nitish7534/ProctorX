from deepface import DeepFace
import base64
import tempfile
import shutil

def verify_face(
    registered_image,
    live_image
):

    reg_data = registered_image.split(",")[1]
    live_data = live_image.split(",")[1]

    reg_file = tempfile.NamedTemporaryFile(
        suffix=".jpg",
        delete=False
    )

    live_file = tempfile.NamedTemporaryFile(
        suffix=".jpg",
        delete=False
    )

    reg_file.write(
        base64.b64decode(reg_data)
    )

    live_file.write(
        base64.b64decode(live_data)
    )

    reg_file.close()
    live_file.close()

    print("Registered File:", reg_file.name)
    print("Live File:", live_file.name)

   

    shutil.copy(
        reg_file.name,
        "registered_debug.jpg"
    )

    shutil.copy(
        live_file.name,
        "live_debug.jpg"
    )

    result = DeepFace.verify(
        img1_path=reg_file.name,
        img2_path=live_file.name,
        model_name="ArcFace",
        detector_backend="retinaface",
        enforce_detection=True
    )

    print(result)

    print("Distance:", result["distance"])

    if result["distance"] < 0.30:
        return True

    return False