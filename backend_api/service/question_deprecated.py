async def get_question_topics(session: SessionDep, question_id: str) -> list[str]:
    """Return list of topic names for a question."""
    qid: UUID = get_question_id_UUID(question_id)

    stmt = (
        select(Question)
        .options(selectinload(Question.topics))  # eager-load topics # type: ignore
        .where(Question.id == qid)
    )
    question = session.exec(stmt).first()
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Question not found"
        )

    return [t.name for t in question.topics]  # or return question.topics


async def get_question_qmeta(question_id: str, session: SessionDep):
    """Fetch and validate qmeta.json for a question, returning QuestionMetaNew."""
    question_uuid = get_question_id_UUID(question_id)

    result = session.exec(
        select(File)
        .where(File.question_id == question_uuid)
        .where(File.filename == "qmeta.json")
    ).first()

    # Checking to see if there is any content
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Question has no qmeta"
        )
    if result.content is None or (
        isinstance(result.content, str) and not result.content.strip()
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="qmeta.json exists but has no content.",
        )

    try:
        raw: Union[dict, list]
        if isinstance(result.content, (dict, list)):
            raw = result.content
        elif isinstance(result.content, str):
            raw = json.loads(result.content)
        else:
            # Unexpected type (e.g., bytes)
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"Unsupported content type for qmeta.json: {type(result.content).__name__}",
            )
    except JSONDecodeError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid JSON in qmeta.json: {e.msg} at pos {e.pos}",
        )

    try:
        qmeta = QuestionMetaNew(**raw)  # type: ignore
    except ValidationError as e:
        # Return Pydantic errors cleanly
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"message": "qmeta failed validation", "errors": e.errors()},
        )

    return qmeta


async def filter_questions(session: SessionDep, qfilter: QuestionDict):
    """Apply dynamic filters to Question based on qfilter."""
    filters = []
    for key, value in qfilter.items():
        logger.debug("Filter: %s = %r", key, value)

        col = getattr(Question, key, None)
        if not col or value in (None, "", []):
            continue

        # For not full search just alike
        if key == "title":
            vals = value if isinstance(value, (list, tuple, set)) else [value]
            filters.append(or_(*[Question.title.ilike(f"%{v}%") for v in vals if v]))  # type: ignore
            continue

        # handle cases where there is a list
        if isinstance(value, (list, tuple, set)):
            filters.append(or_(*[col == v for v in value]))
            logger.debug("Value %s", value)
        else:
            filters.append(col == value)

    stmt = select(Question)
    if filters:
        stmt = stmt.where(*filters)  # AND across keys, OR within each key
    return session.exec(stmt).all()


# =========================
# Update
# =========================


async def add_topic_to_question(
    question_id: str,
    topic_name: str,
    session: SessionDep,
) -> Question:
    """Attach a Topic (creating if necessary) to a Question."""
    # normalize inputs
    name = (topic_name or "").strip()
    if not name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Topic name must be a non-empty string.",
        )

    # resolve / validate question id
    question_uuid: UUID = get_question_id_UUID(question_id)

    # fetch question
    question: Optional[Question] = session.exec(
        select(Question).where(Question.id == question_uuid)
    ).first()
    if question is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Question {question_uuid} not found.",
        )

    # get or create topic (unique by name)
    topic: Optional[Topic] = session.exec(
        select(Topic).where(Topic.name == name)
    ).first()

    if topic is None:
        topic = Topic(name=name)
        session.add(topic)
        try:
            session.commit()
        except IntegrityError:
            # another request may have created it concurrently
            session.rollback()
            topic = session.exec(select(Topic).where(Topic.name == name)).one()
        finally:
            session.refresh(topic)

    # make sure question.topics is a list (older schemas might have Optional)
    if getattr(question, "topics", None) is None:
        question.topics = []

    # avoid duplicate link
    if not any(t.id == topic.id for t in question.topics):
        question.topics.append(topic)
        session.add(question)
        session.commit()
        session.refresh(question)

    return question


# =========================
# Delete
# =========================


# =========================
# Composite Ops
# =========================


async def add_question_and_files(
    question: Question, files: dict[str, Union[str, dict]], session: SessionDep
) -> Question:
    """Create a question and (conditionally) add files."""
    question = await add_question(question, session)
    for filename, contents in files.items():
        if isinstance(contents, (dict, list)):
            contents = json.dumps(contents)

            file_obj = File(
                filename=filename, content=contents, question_id=question.id
            )

            await add_file(file_obj, session)
    return question


