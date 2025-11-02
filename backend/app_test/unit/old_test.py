# @pytest.mark.asyncio
# async def test_download_zip(tmp_path, local_storage, save_multiple_files):
#     """Test that download_question correctly zips and returns data."""
#     data = await local_storage.download_question("TestFolder")
#     files, name = save_multiple_files

#     assert isinstance(data, bytes)
#     assert len(data) > 0

#     buffer = io.BytesIO(data)
#     with zipfile.ZipFile(buffer, "r") as z:
#         names = z.namelist()
#         for f in files:
#             assert f"{name}/{f[0]}" in names