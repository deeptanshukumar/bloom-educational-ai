import os
import shutil
from werkzeug.utils import secure_filename
import tempfile
import uuid
from datetime import datetime, timedelta

class FileService:
    def __init__(self, base_temp_dir=None):
        self.base_temp_dir = base_temp_dir or os.path.join(tempfile.gettempdir(), 'bloom_sessions')
        self.session_dirs = {}  # Map of session_id to directory and creation time
        self.cleanup_threshold = timedelta(hours=1)  # Remove sessions older than 1 hour
        
        try:
            if not os.path.exists(self.base_temp_dir):
                os.makedirs(self.base_temp_dir)
        except OSError as e:
            raise RuntimeError(f"Failed to create base temp directory: {str(e)}") from e

    def create_session(self) -> str:
        """Create a new file upload session"""
        session_id = str(uuid.uuid4())
        self.create_session_dir(session_id)
        return session_id

    def create_session_dir(self, session_id: str) -> str:
        """Create a temporary directory for a session"""
        session_dir = os.path.join(self.base_temp_dir, str(session_id))
        os.makedirs(session_dir, exist_ok=True)
        self.session_dirs[session_id] = {
            'path': session_dir,
            'created_at': datetime.now()
        }
        return session_dir

    def get_session_dir(self, session_id: str) -> str:
        """Get the temporary directory for a session"""
        if session_id not in self.session_dirs:
            return self.create_session_dir(session_id)
        return self.session_dirs[session_id]['path']

    def add_file_to_session(self, session_id: str, file) -> dict:
        """Add a file to a session"""
        try:
            file_info = self.save_file(file, session_id)
            return {
                'id': str(uuid.uuid4()),
                'original_name': file.filename,
                'path': file_info['path']
            }
        except (ValueError, IOError):
            raise
        except Exception as e:
            raise RuntimeError(f"Failed to add file to session: {str(e)}") from e

    def save_file(self, file, session_id: str) -> dict:
        """Save a file to the session's temporary directory"""
        if not file:
            raise ValueError("No file provided")
            
        if not session_id:
            raise ValueError("No session ID provided")
            
        try:
            filename = secure_filename(file.filename)
            if not filename:
                raise ValueError("Invalid filename")
                
            unique_filename = f"{uuid.uuid4()}_{filename}"
            session_dir = self.get_session_dir(session_id)
            file_path = os.path.join(session_dir, unique_filename)
            
            # Check if directory exists and is writable
            if not os.path.exists(session_dir):
                raise IOError(f"Session directory {session_dir} does not exist")
            if not os.access(session_dir, os.W_OK):
                raise IOError(f"Session directory {session_dir} is not writable")
            
            # Verify file size before saving
            file.seek(0, os.SEEK_END)
            size = file.tell()
            if size > 16 * 1024 * 1024:  # 16MB limit
                raise ValueError("File size exceeds maximum limit of 16MB")
            file.seek(0)  # Reset file pointer
            
            file.save(file_path)
            
            if not os.path.exists(file_path):
                raise IOError(f"Failed to save file {filename}")
                
            return {
                'filename': filename,
                'path': file_path,
                'size': os.path.getsize(file_path),
                'type': os.path.splitext(filename)[1][1:].lower()
            }
            
        except (OSError, IOError) as e:
            raise IOError(f"Error saving file {getattr(file, 'filename', 'unknown')}: {str(e)}") from e
        except Exception as e:
            raise RuntimeError(f"Unexpected error processing file: {str(e)}") from e

    def remove_file_from_session(self, session_id: str, file_id: str) -> bool:
        """Remove a file from a session"""
        try:
            session_dir = self.get_session_dir(session_id)
            # Find file by file_id prefix
            for filename in os.listdir(session_dir):
                if filename.startswith(file_id):
                    file_path = os.path.join(session_dir, filename)
                    os.remove(file_path)
                    return True
            return False
        except Exception as e:
            raise RuntimeError(f"Failed to remove file: {str(e)}") from e

    def cleanup_session(self, session_id: str) -> bool:
        """Remove a session's temporary directory"""
        if session_id in self.session_dirs:
            shutil.rmtree(self.session_dirs[session_id]['path'], ignore_errors=True)
            del self.session_dirs[session_id]
            return True
        return False

    def cleanup_old_sessions(self) -> None:
        """Clean up sessions older than the threshold"""
        now = datetime.now()
        for session_id, info in list(self.session_dirs.items()):
            if now - info['created_at'] > self.cleanup_threshold:
                self.cleanup_session(session_id)
    
    def get_session_files(self, session_id: str) -> list:
        """Get list of files in a session directory"""
        session_dir = self.get_session_dir(session_id)
        files = []
        for filename in os.listdir(session_dir):
            file_path = os.path.join(session_dir, filename)
            original_filename = filename.split('_', 1)[1]  # Remove UUID prefix
            files.append({
                'filename': original_filename,
                'path': file_path,
                'size': os.path.getsize(file_path),
                'type': os.path.splitext(filename)[1][1:].lower()
            })
        return files

# Create a singleton instance
file_service = FileService()