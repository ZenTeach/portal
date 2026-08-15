"""
    Conversion util for marshmallow/pydantic validation exceptions
"""

from typing import Dict, List, Optional


def format_validation_for_api(validation_errors: Optional[Dict] = None) -> List[str]:
    if validation_errors is None:
        return []

    return stringify_dict_KV(validation_errors)


def format_pydantic_validation_for_api(exc) -> List[str]:
    """Convert a pydantic ``ValidationError`` into ``"loc - msg"`` strings.

    Mirrors :func:`format_validation_for_api`'s output shape but works on the
    list-of-error-dicts structure that pydantic's ``e.errors()`` returns.
    """
    error_strings = []

    for error in exc.errors():
        loc = ".".join(str(part) for part in error.get("loc", ()))
        if loc:
            error_strings.append(f"{loc} - {error.get('msg', '')}")
        else:
            error_strings.append(error.get("msg", ""))

    return error_strings


def stringify_dict_KV(errorsKV: Dict) -> List[str]:
    error_strings = []

    for key, value in errorsKV.items():
        if isinstance(value, list):
            [
                error_strings.append(
                    f"{key} - {sub_val}"
                )
                for sub_val in value
            ]
        else:
            error_strings.append(
                f"{key} - {value}"
            )

    return error_strings
