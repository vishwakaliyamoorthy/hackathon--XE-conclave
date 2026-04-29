# Supabase Database Service Layer
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

from supabase import create_client, Client
from postgrest.exceptions import APIError

from config import get_settings
from schemas import (
    UserDB, DocumentDB, AnalysisDB, DocumentTypeEnum, AnalysisStatusEnum
)

logger = logging.getLogger(__name__)
settings = get_settings()


class SupabaseService:
    """Supabase database service for all operations."""

    def __init__(self):
        """Initialize Supabase client."""
        try:
            supabase_url = settings.SUPABASE_URL
            # Use service role key if available (to bypass RLS for backend operations), otherwise fallback to anon key
            supabase_key = settings.SUPABASE_SERVICE_ROLE_KEY or settings.SUPABASE_KEY
            
            if not supabase_url or not supabase_key:
                logger.warning("Supabase credentials not fully configured")
                
            self.client: Client = create_client(supabase_url, supabase_key)
            logger.info("Supabase client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            raise

    async def health_check(self) -> bool:
        """Check Supabase connection health."""
        try:
            response = self.client.table("users").select("count", count="exact").limit(1).execute()
            return response is not None
        except Exception as e:
            logger.error(f"Supabase health check failed: {e}")
            return False

    # ==== USER OPERATIONS ====

    async def create_user(
        self,
        email: str,
        password_hash: str,
        full_name: str,
        organization: str,
        role: str
    ) -> UserDB:
        """Create new user in database."""
        try:
            user_id = str(uuid.uuid4())
            now = datetime.utcnow().isoformat()

            data = {
                "id": user_id,
                "email": email,
                "password_hash": password_hash,
                "full_name": full_name,
                "organization": organization,
                "role": role,
                "is_active": True,
                "created_at": now,
                "updated_at": now,
            }

            response = self.client.table("users").insert(data).execute()
            logger.info(f"User created: {email}")
            return UserDB(**response.data[0])

        except APIError as e:
            logger.error(f"Error creating user: {e}")
            raise

    async def get_user_by_email(self, email: str) -> Optional[UserDB]:
        """Get user by email."""
        try:
            response = self.client.table("users").select("*").eq("email", email).execute()
            
            if response.data:
                return UserDB(**response.data[0])
            return None

        except APIError as e:
            logger.error(f"Error fetching user: {e}")
            raise

    async def get_user_by_id(self, user_id: str) -> Optional[UserDB]:
        """Get user by ID."""
        try:
            response = self.client.table("users").select("*").eq("id", user_id).execute()
            
            if response.data:
                return UserDB(**response.data[0])
            return None

        except APIError as e:
            logger.error(f"Error fetching user by ID: {e}")
            raise

    async def user_exists(self, email: str) -> bool:
        """Check if user exists."""
        try:
            response = self.client.table("users").select("id", count="exact").eq("email", email).execute()
            return len(response.data) > 0

        except APIError as e:
            logger.error(f"Error checking user existence: {e}")
            raise

    # ==== DOCUMENT OPERATIONS ====

    async def create_document(
        self,
        user_id: str,
        org_id: str,
        doc_type: str,
        title: str,
        description: Optional[str],
        file_path: str,
        file_url: str,
        file_size: int
    ) -> DocumentDB:
        """Create new document record."""
        try:
            doc_id = str(uuid.uuid4())
            now = datetime.utcnow().isoformat()

            data = {
                "id": doc_id,
                "user_id": user_id,
                "org_id": org_id,
                "doc_type": doc_type,
                "title": title,
                "description": description,
                "file_path": file_path,
                "file_url": file_url,
                "file_size": file_size,
                "status": "processing",
                "created_at": now,
                "updated_at": now,
            }

            response = self.client.table("documents").insert(data).execute()
            logger.info(f"Document created: {doc_id}")
            return DocumentDB(**response.data[0])

        except APIError as e:
            logger.error(f"Error creating document: {e}")
            raise

    async def get_document(self, doc_id: str) -> Optional[DocumentDB]:
        """Get document by ID."""
        try:
            response = self.client.table("documents").select("*").eq("id", doc_id).execute()
            
            if response.data:
                return DocumentDB(**response.data[0])
            return None

        except APIError as e:
            logger.error(f"Error fetching document: {e}")
            raise

    async def get_user_documents(
        self,
        user_id: str,
        org_id: str,
        doc_type: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[DocumentDB]:
        """Get user's documents with optional filtering."""
        try:
            query = self.client.table("documents").select("*").eq("user_id", user_id).eq("org_id", org_id)
            
            if doc_type:
                query = query.eq("doc_type", doc_type)
            
            response = query.order("created_at", desc=True).limit(limit).offset(offset).execute()
            
            return [DocumentDB(**doc) for doc in response.data]

        except APIError as e:
            logger.error(f"Error fetching user documents: {e}")
            raise

    async def update_document_status(
        self,
        doc_id: str,
        status: str,
        raw_text: Optional[str] = None
    ) -> DocumentDB:
        """Update document status and raw text."""
        try:
            data = {
                "status": status,
                "updated_at": datetime.utcnow().isoformat(),
            }
            
            if raw_text:
                data["raw_text"] = raw_text

            response = self.client.table("documents").update(data).eq("id", doc_id).execute()
            
            if response.data:
                return DocumentDB(**response.data[0])
            raise ValueError(f"Document not found: {doc_id}")

        except APIError as e:
            logger.error(f"Error updating document: {e}")
            raise

    async def create_document_version(
        self,
        document_id: str,
        content: str,
        changes: str,
        updated_by: str = "AI"
    ) -> Dict[str, Any]:
        """Create a new version for a document and update the main document text."""
        try:
            # Get current document to find current version number
            # We can query existing versions to get the max version number
            versions_resp = self.client.table("versions").select("version_number").eq("document_id", document_id).order("version_number", desc=True).limit(1).execute()
            
            next_version = 1
            if versions_resp.data and len(versions_resp.data) > 0:
                next_version = versions_resp.data[0]["version_number"] + 1

            version_id = str(uuid.uuid4())
            now = datetime.utcnow().isoformat()

            version_data = {
                "id": version_id,
                "document_id": document_id,
                "version_number": next_version,
                "content": content,
                "changes": changes,
                "updated_by": updated_by,
                "timestamp": now
            }

            # Insert into versions table
            self.client.table("versions").insert(version_data).execute()
            
            # Update main document to point to latest content
            self.client.table("documents").update({
                "raw_text": content,
                "updated_at": now
            }).eq("id", document_id).execute()
            
            logger.info(f"Created version {next_version} for document {document_id}")
            return version_data

        except Exception as e:
            logger.error(f"Error creating document version: {e}")
            # If versions table doesn't exist yet, fallback to just updating the document
            logger.warning("Fallback: Updating document directly without versioning record.")
            try:
                self.client.table("documents").update({
                    "raw_text": content,
                    "updated_at": datetime.utcnow().isoformat()
                }).eq("id", document_id).execute()
                return {"version_number": 1, "content": content}
            except Exception as inner_e:
                logger.error(f"Fallback update failed: {inner_e}")
                raise

    # ==== ANALYSIS OPERATIONS ====

    async def create_analysis(
        self,
        user_id: str,
        org_id: str,
        title: str,
        description: Optional[str] = None
    ) -> AnalysisDB:
        """Create new analysis record."""
        try:
            analysis_id = str(uuid.uuid4())
            now = datetime.utcnow().isoformat()

            data = {
                "id": analysis_id,
                "user_id": user_id,
                "org_id": org_id,
                "title": title,
                "description": description,
                "status": "pending",
                "created_at": now,
                "updated_at": now,
            }

            response = self.client.table("analyses").insert(data).execute()
            logger.info(f"Analysis created: {analysis_id}")
            return AnalysisDB(**response.data[0])

        except APIError as e:
            logger.error(f"Error creating analysis: {e}")
            raise

    async def get_analysis(self, analysis_id: str) -> Optional[AnalysisDB]:
        """Get analysis by ID."""
        try:
            response = self.client.table("analyses").select("*").eq("id", analysis_id).execute()
            
            if response.data:
                return AnalysisDB(**response.data[0])
            return None

        except APIError as e:
            logger.error(f"Error fetching analysis: {e}")
            raise

    async def link_documents_to_analysis(
        self,
        analysis_id: str,
        prd_doc_id: Optional[str] = None,
        design_doc_id: Optional[str] = None,
        code_doc_id: Optional[str] = None
    ) -> AnalysisDB:
        """Link documents to analysis."""
        try:
            data = {
                "prd_doc_id": prd_doc_id,
                "design_doc_id": design_doc_id,
                "code_doc_id": code_doc_id,
                "updated_at": datetime.utcnow().isoformat(),
            }

            response = self.client.table("analyses").update(data).eq("id", analysis_id).execute()
            
            if response.data:
                return AnalysisDB(**response.data[0])
            raise ValueError(f"Analysis not found: {analysis_id}")

        except APIError as e:
            logger.error(f"Error linking documents: {e}")
            raise

    async def update_analysis_status(
        self,
        analysis_id: str,
        status: str,
        results: Optional[Dict[str, Any]] = None
    ) -> AnalysisDB:
        """Update analysis status and results."""
        try:
            data = {
                "status": status,
                "updated_at": datetime.utcnow().isoformat(),
            }
            
            if results:
                data["results"] = results
                data["consistency_score"] = results.get("consistency_score")
                data["total_conflicts"] = results.get("total_conflicts")
                data["completed_at"] = datetime.utcnow().isoformat()

            response = self.client.table("analyses").update(data).eq("id", analysis_id).execute()
            
            if response.data:
                return AnalysisDB(**response.data[0])
            raise ValueError(f"Analysis not found: {analysis_id}")

        except APIError as e:
            logger.error(f"Error updating analysis: {e}")
            raise

    async def get_user_analyses(
        self,
        user_id: str,
        org_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[AnalysisDB]:
        """Get user's analyses."""
        try:
            response = (
                self.client.table("analyses")
                .select("*")
                .eq("user_id", user_id)
                .eq("org_id", org_id)
                .order("created_at", desc=True)
                .limit(limit)
                .offset(offset)
                .execute()
            )
            
            return [AnalysisDB(**analysis) for analysis in response.data]

        except APIError as e:
            logger.error(f"Error fetching user analyses: {e}")
            raise

    # ==== STORAGE OPERATIONS ====

    async def upload_file_to_storage(
        self,
        file_path: str,
        file_content: bytes,
        bucket_name: str = "documents"
    ) -> str:
        """Upload file to Supabase storage."""
        try:
            response = self.client.storage.from_(bucket_name).upload(
                path=file_path,
                file=file_content,
                file_options={"content-type": "application/octet-stream"},
            )
            
            file_url = self.client.storage.from_(bucket_name).get_public_url(file_path)
            logger.info(f"File uploaded: {file_path}")
            return file_url

        except Exception as e:
            logger.error(f"Error uploading file: {e}")
            raise

    async def delete_file_from_storage(
        self,
        file_path: str,
        bucket_name: str = "documents"
    ) -> bool:
        """Delete file from Supabase storage."""
        try:
            self.client.storage.from_(bucket_name).remove([file_path])
            logger.info(f"File deleted: {file_path}")
            return True

        except Exception as e:
            logger.error(f"Error deleting file: {e}")
            return False


# Singleton instance
_supabase_service: Optional[SupabaseService] = None


def get_supabase_service() -> SupabaseService:
    """Get Supabase service singleton."""
    global _supabase_service
    if _supabase_service is None:
        _supabase_service = SupabaseService()
    return _supabase_service
