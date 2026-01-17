from flask import Blueprint, Response, request, jsonify

from models.api_response_model import APIResponse
from models.query_model import QueryResponse
from services.query_service import query_service

query_bp = Blueprint("query", __name__, url_prefix="/api/query")


@query_bp.route("/", methods=["GET"])
def ask_question() -> tuple[Response, int]:
    question = request.args.get("q", "").strip()

    if not question:
        response: APIResponse[None] = APIResponse.fail(
            message="Query failed",
            error="Empty query",
            details="Question cannot be empty",
        )
        return jsonify(response.to_dict()), 400

    try:
        answer_html: str = query_service.ask_agent(question)
        result = QueryResponse(question=question, answer_html=answer_html)

        response: APIResponse[QueryResponse] = APIResponse.ok(
            message="Success!", data=result
        )

        return jsonify(response.to_dict()), 200

    except Exception as e:
        response: APIResponse[None] = APIResponse.fail(
            message="Query failed",
            error="Agent error",
            details=str(e),
        )
        return jsonify(response.to_dict()), 500
