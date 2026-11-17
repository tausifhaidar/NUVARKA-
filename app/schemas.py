from pydantic import BaseModel, Field, HttpUrl

class YoutubeClipRequest(BaseModel):
    url: HttpUrl
    clips: int = Field(default=5, ge=1, le=10)
