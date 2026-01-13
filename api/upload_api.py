from flask import Blueprint, Response, request, jsonify

from models.api_response_model import APIResponse
from models.upload_model import UploadResponse
from services.upload_service import upload_service

upload_bp = Blueprint("upload", __name__, url_prefix="/api/upload")


@upload_bp.route("/folder", methods=["POST"])
def upload_folder() -> tuple[Response, int]:
    if "files" not in request.files:
        response: APIResponse[None] = APIResponse.fail(
            message="Upload failed",
            error="No files provided",
            details="Request must include 'files' field with files to upload",
        )
        return jsonify(response.to_dict()), 400

    files = request.files.getlist("files")
    if not files or all(f.filename == "" for f in files):
        response: APIResponse[None] = APIResponse.fail(
            message="Upload failed",
            error="Empty file list",
            details="At least one file must be provided",
        )
        return jsonify(response.to_dict()), 400

    folder_name = request.form.get("folder_name", "uploaded_folder")

    result = upload_service.upload_folder(files, folder_name)

    status_code = 200 if result.status.value == "success" else 207
    response: APIResponse[UploadResponse] = APIResponse.ok(
        message=result.message, data=result
    )
    return jsonify(response.to_dict()), status_code
