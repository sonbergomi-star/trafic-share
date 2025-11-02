"""User settings schemas."""

from pydantic import BaseModel


class SettingsResponse(BaseModel):
    language: str
    push_notifications: bool
    session_updates: bool
    system_updates: bool
    two_factor_enabled: bool
    single_device_mode: bool
    battery_saver: bool
    theme: str


class SettingsUpdateRequest(BaseModel):
    language: str | None = None
    push_notifications: bool | None = None
    session_updates: bool | None = None
    system_updates: bool | None = None
    two_factor_enabled: bool | None = None
    single_device_mode: bool | None = None
    battery_saver: bool | None = None
    theme: str | None = None
