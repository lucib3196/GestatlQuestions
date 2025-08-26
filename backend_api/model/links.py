from uuid import UUID

from sqlmodel import SQLModel, Field


# Association table for many-to-many
class QuestionTopicLink(SQLModel, table=True):
    __tablename__ = "question_topic_link"  # type: ignore
    question_id: UUID = Field(foreign_key="question.id", primary_key=True, index=True)
    topic_id: UUID = Field(foreign_key="topic.id", primary_key=True, index=True)


class QuestionLanguageLink(SQLModel, table=True):
    __tablename__ = "question_language_link"  # type: ignore
    question_id: UUID = Field(foreign_key="question.id", primary_key=True, index=True)
    language_id: UUID = Field(foreign_key="language.id", primary_key=True, index=True)


class QuestionQTypeLink(SQLModel, table=True):
    __tablename__ = "question_qtype_link"  # type: ignore
    question_id: UUID = Field(foreign_key="question.id", primary_key=True, index=True)
    qtype_id: UUID = Field(foreign_key="qtype.id", primary_key=True, index=True)
