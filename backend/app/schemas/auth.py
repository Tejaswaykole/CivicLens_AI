"""Authentication requests. Public registration cannot choose a role."""

import uuid
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.core.passwords import MAX_PASSWORD_LENGTH, MIN_PASSWORD_LENGTH, password_is_acceptable
from app.domain.enums import UserRole


class RegisterRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    display_name: str = Field(min_length=2, max_length=200)
    email: EmailStr
    password: str = Field(min_length=MIN_PASSWORD_LENGTH, max_length=MAX_PASSWORD_LENGTH)
    ward_or_zone: str | None = Field(default=None, max_length=200)

    @field_validator("display_name", "ward_or_zone", mode="before")
    @classmethod
    def strip_text(cls, value: object) -> object:
        if value is None or not isinstance(value, str):
            return value
        stripped = value.strip()
        return stripped or None

    @field_validator("password")
    @classmethod
    def password_policy(cls, value: str) -> str:
        if not password_is_acceptable(value):
            raise ValueError(
                f"Password must be {MIN_PASSWORD_LENGTH}-{MAX_PASSWORD_LENGTH} characters "
                "without leading or trailing spaces."
            )
        return value

    @field_validator("email")
    @classmethod
    def lowercase_email(cls, value: str) -> str:
        return value.strip().lower()


class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: EmailStr
    password: str = Field(min_length=1, max_length=MAX_PASSWORD_LENGTH)

    @field_validator("email")
    @classmethod
    def lowercase_email(cls, value: str) -> str:
        return value.strip().lower()


class TokenResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
    expires_in: int


class RegisterResponse(TokenResponse):
    """Registration token. The debug field is omitted from production responses."""

    dev_verification_token: str | None = None


class VerifyEmailRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    token: str = Field(min_length=20, max_length=256)


class VerificationResponse(BaseModel):
    email_verified: bool
    dev_verification_token: str | None = None


class StaffUserCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    display_name: str = Field(min_length=2, max_length=200)
    email: EmailStr
    password: str = Field(min_length=MIN_PASSWORD_LENGTH, max_length=MAX_PASSWORD_LENGTH)
    role: UserRole
    department_id: uuid.UUID | None = None
    designation: str | None = Field(default=None, max_length=200)
    ward_or_zone: str | None = Field(default=None, max_length=200)

    @field_validator("display_name", "designation", "ward_or_zone", mode="before")
    @classmethod
    def strip_text(cls, value: object) -> object:
        if value is None or not isinstance(value, str):
            return value
        stripped = value.strip()
        return stripped or None

    @field_validator("password")
    @classmethod
    def password_policy(cls, value: str) -> str:
        if not password_is_acceptable(value):
            raise ValueError(
                f"Password must be {MIN_PASSWORD_LENGTH}-{MAX_PASSWORD_LENGTH} characters "
                "without leading or trailing spaces."
            )
        return value

    @field_validator("email")
    @classmethod
    def lowercase_email(cls, value: str) -> str:
        return value.strip().lower()


class UserAdminUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    role: UserRole | None = None
    is_active: bool | None = None
    department_id: uuid.UUID | None = None
    clear_department: bool = False
    designation: str | None = Field(default=None, max_length=200)
    ward_or_zone: str | None = Field(default=None, max_length=200)

    @field_validator("designation", "ward_or_zone", mode="before")
    @classmethod
    def strip_text(cls, value: object) -> object:
        if value is None or not isinstance(value, str):
            return value
        stripped = value.strip()
        return stripped or None
