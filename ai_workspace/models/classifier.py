from typing import List
from pydantic import BaseModel


class FullCourseDescription(BaseModel):
    course_name: str
    course_id: str
    full_description: str
    course_level: str


class FullCourseDescriptionList(BaseModel):
    courses: List[FullCourseDescription]


class TopicDescription(BaseModel):
    name: str
    description: str
    discipline: List[str]


class FullTopicDescriptionList(BaseModel):
    topics: List[TopicDescription]
