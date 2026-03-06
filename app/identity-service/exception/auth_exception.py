from fastapi import HTTPException


class UserNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(status_code=404, detail="User not found")


class UserAlreadyExistsException(HTTPException):
    def __init__(self):
        super().__init__(status_code=409, detail="User with this email already exists")


class WrongPasswordException(HTTPException):
    def __init__(self):
        super().__init__(status_code=401, detail="Entered password is incorrect")