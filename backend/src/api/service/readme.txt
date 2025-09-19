storage/
      base.py             # StorageService interface
      local_storage.py    # Local implementation
      cloud_storage.py    # Cloud implementation (Firebase/S3/etc.)
directory_service.py  # Handles setting/creating/checking directories
question_crud.py      # DB CRUD operations for questions
question_manager.py   # Orchestrates CRUD + storage