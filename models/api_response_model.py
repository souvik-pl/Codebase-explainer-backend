from dataclasses import dataclass, asdict
from typing import Optional, Any, TypeVar, Generic


T = TypeVar("T")


@dataclass
class ErrorDetails:
    error: str
    details: Optional[str] = None


@dataclass
class APIResponse(Generic[T]):
    success: bool
    message: str
    data: Optional[T] = None
    error: Optional[ErrorDetails] = None

    def to_dict(self) -> dict:
        result: dict[str, Any] = {
            "success": self.success,
            "message": self.message,
        }

        if self.data is not None:
            if hasattr(self.data, "to_dict"):
                result["data"] = self.data.to_dict()
            elif hasattr(self.data, "__dataclass_fields__"):
                result["data"] = asdict(self.data)
            else:
                result["data"] = self.data

        if self.error is not None:
            result["error"] = asdict(self.error)

        return result

    @classmethod
    def ok(cls, message: str, data: Optional[T] = None) -> "APIResponse[T]":
        return cls(success=True, message=message, data=data)

    @classmethod
    def fail(
        cls, message: str, error: str, details: Optional[str] = None
    ) -> "APIResponse[T]":
        return cls(
            success=False,
            message=message,
            error=ErrorDetails(error=error, details=details),
        )
