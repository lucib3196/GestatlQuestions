#  # ---------------------------
#     # File Operations
#     # ---------------------------
#     async def save_file_to_question(
#         self,
#         question_id: str | UUID,
#         session: SessionDep,
#         file: FileData,
#         overwrite: bool = False,
#     ) -> bool:
#         """Save a single file to a question directory."""
#         try:
#             await self.get_question(question_id, session)
#             identifier = await self.get_question_identifier(question_id, session)
#             if not identifier:
#                 raise ValueError("Could not resolve question identifier")

#             self.storage.save_file(identifier, file.filename, file.content, overwrite)
#             logger.info(f"Wrote file {file.filename} for question {question_id}")
#             return True
#         except Exception as e:
#             logger.error(
#                 "Failed saving file %s for question %s: %s",
#                 file.filename,
#                 question_id,
#                 e,
#             )
#             raise

#     async def save_files_to_question(
#         self,
#         question_id: str | UUID,
#         session: SessionDep,
#         files: List[FileData],
#         overwrite: bool = False,
#     ) -> bool:
#         """Save multiple files to a question directory."""
#         try:
#             await asyncio.gather(
#                 *[
#                     self.save_file_to_question(question_id, session, f, overwrite)
#                     for f in files
#                 ]
#             )
#             return True
#         except Exception as e:
#             logger.error("Failed to save files to question %s: %s", question_id, e)
#             raise

#     async def read_file(
#         self, question_id: str | UUID, session: SessionDep, filename: str
#     ) -> bytes | None:
#         """Retrieve a file from a question directory."""
#         try:
#             qidentifier = await self.get_question_identifier(question_id, session)
#             if not qidentifier:
#                 raise ValueError("Could not resolve question identifier")
#             return self.storage.get_file(qidentifier, filename)
#         except Exception as e:
#             logger.error("Failed to get file %s for question %s", filename, question_id)
#             raise

#     async def get_all_files(
#         self, question_id: str | UUID, session: SessionDep
#     ) -> List[str]:
#         """Retrieve all file names for a given question."""
#         try:
#             qidentifier = await self.get_question_identifier(question_id, session)
#             if not qidentifier:
#                 raise ValueError("Could not resolve question identifier")
#             return self.storage.list_file_names(qidentifier)
#         except Exception as e:
#             logger.error("Failed to get files for question %s", question_id)
#             raise

#     async def read_all_files(
#         self, question_id: str | UUID, session: SessionDep
#     ) -> List[FileData]:
#         try:
#             files = await self.get_all_files(question_id, session)

#             # Await to actually run and collect results
#             contents = await asyncio.gather(
#                 *[self.read_file(question_id, session, f) for f in files]
#             )

#             # Pair each filename with its content
#             file_data = [
#                 FileData(filename=f, content=c) for f, c in zip(files, contents)
#             ]
#             return file_data

#         except Exception as e:
#             logger.error(
#                 "Failed to read all files for question %s Error: %s",
#                 question_id,
#                 str(e),
#             )
#             raise

#     # ---------------------------
#     # Deletion
#     # ---------------------------

#     async def delete_question_file(
#         self, question_id: str | UUID, session: SessionDep, filename: str
#     ):
#         """Delete a single file from a question."""
#         try:
#             qidentifier = await self.get_question_identifier(question_id, session)
#             if not qidentifier:
#                 raise ValueError("Could not resolve question identifier")
#             self.storage.delete_file(qidentifier, filename)
#         except Exception as e:
#             logger.error("Failed to delete file %s %s: %s", question_id, filename, e)
#             raise

#     # Download
#     # TODO: Test
#     async def download_question(
#         self, session: SessionDep, question_id: UUID | str
#     ) -> bytes | io.BytesIO:
#         qidentifier = await self.get_question_identifier(question_id, session)
#         if not qidentifier:
#             raise ValueError("Could not resolve question identifier")
#         return await self.storage.download_question(qidentifier)

#     # TODO Fix this and add a test for this
#     async def download_starter_templates(self) -> Dict[str, bytes]:
#         try:
#             adaptive_template = (
#                 Path(settings.ROOT_PATH) / "starter_templates" / "AdaptiveStarter"
#             )
#             nonadaptive_template = (
#                 Path(settings.ROOT_PATH) / "starter_templates" / "NonAdaptive"
#             )
#             adaptive_bytes = await self.file_service.download_zip(
#                 [p for p in adaptive_template.iterdir()],
#                 folder_name="Adaptive Template",
#             )
#             nonadaptive_bytes = await self.file_service.download_zip(
#                 [p for p in nonadaptive_template.iterdir()],
#                 folder_name="NonAdaptiveStarter",
#             )
#             return {
#                 "adaptiveTemplate": adaptive_bytes,
#                 "NonAdaptiveTemplate": nonadaptive_bytes,
#             }
#         except Exception as e:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail=f"Could not download starter template {str(e)}",
#             )




# # --- Download Helpers ---
#     # TODO: Make this a function of the filehandler
#     async def download_question(self, identifier: str) -> io.BytesIO:
#         """Download all files for an identifier as a zipped BytesIO stream."""
#         prefix = self.get_storage_path(identifier).as_posix()
#         blobs = list(self.bucket.list_blobs(prefix=prefix))

#         if not blobs:
#             logger.warning("No files to download")
#             return io.BytesIO()

#         buffer = io.BytesIO()
#         manifest: list[dict] = []

#         with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as z:
#             for blob in blobs:
#                 # strip prefix to avoid double-nested paths
#                 relative_name = blob.name[len(prefix) :].lstrip("/")
#                 data = blob.download_as_bytes()
#                 z.writestr(f"downloads/{identifier}/{relative_name}", data)
#                 manifest.append({"file": relative_name, "size": len(data)})

#             z.writestr(
#                 "MANIFEST.json",
#                 json.dumps({"count": len(manifest), "files": manifest}, indent=2),
#             )

#         buffer.seek(0)
#         return buffer
