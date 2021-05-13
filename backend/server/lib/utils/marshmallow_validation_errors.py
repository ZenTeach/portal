"""
    Conversion util for marshmallow validation exceptions
"""

from typing import Dict, List, Optional


def format_validation_for_api(validation_errors: Optional[Dict] = None) -> List[str]:
    if validation_errors is None:
        return []

    return stringify_dict_KV(validation_errors)


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
