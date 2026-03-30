from fastapi import HTTPException


def validation_error(field: str, msg: str, type_: str = 'value_error', status: int = 422):
    raise HTTPException(
        status_code=status,
        detail=[{
            "loc": ["body", field],
            "msg": msg,
            "type": type_,
        }]
    )