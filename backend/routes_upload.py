# Document upload routes
import logging
import uuid
from typing import Optional

from fastapi import (
    APIRouter, HTTPException, status, Depends, File, UploadFile, Form
)
from pathlib import Path

from schemas import (
    DocumentMetadata, DocumentTypeEnum, TokenPayload, DocumentUploadRequest
)
from auth import check_permission
from services import get_supabase_service
from dependencies import get_current_user
from utils import (
    FileService, ValidationService, ErrorMessages, SuccessMessages
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/upload", tags=["documents"])

supabase = get_supabase_service()


async def validate_upload(
    file: UploadFile,
    doc_type: str,
    current_user: TokenPayload
) -> tuple:
    """Validate document upload."""
    # Check permissions
    permission_map = {
        "prd": "upload:prd",
        "design": "upload:design",
        "code": "upload:code",
    }
    
    required_permission = permission_map.get(doc_type)
    if required_permission and not check_permission(current_user, required_permission):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permission denied to upload {doc_type} documents"
        )

    # Validate file extension
    if not FileService.validate_file_extension(file.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorMessages.INVALID_FILE_TYPE
        )

    # Read and validate file size
    content = await file.read()
    if len(content) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File is empty"
        )

    if not FileService.validate_file_size(len(content)):
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=ErrorMessages.FILE_TOO_LARGE
        )

    return content, len(content)


@router.post(
    "/prd",
    response_model=DocumentMetadata,
    status_code=status.HTTP_201_CREATED
)
async def upload_prd(
    file: UploadFile = File(..., description="PRD document (PDF, DOCX, or TXT)"),
    title: str = Form(..., description="Document title"),
    description: Optional[str] = Form(None, description="Document description"),
    current_user: TokenPayload = Depends(get_current_user)
) -> DocumentMetadata:
    """
    Upload Product Requirements Document (PRD).
    
    **Files accepted**: PDF, DOCX, TXT (max 50MB)
    
    **Authorization**: Requires login
    - PRD upload permission
    
    **Parameters**:
    - file: Document file
    - title: Document title (3-255 chars)
    - description: Optional description
    
    **Returns**: Document metadata with file URL
    """
    logger.info(f"PRD upload started: {file.filename} by {current_user.email}")

    try:
        # Validate title
        if not ValidationService.validate_document_title(title):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorMessages.INVALID_DOC_TITLE
            )

        # Validate upload
        content, file_size = await validate_upload(
            file, "prd", current_user
        )

        # Generate storage path
        file_ext = FileService.get_file_extension(file.filename)
        filename = f"{title[:50]}_{uuid.uuid4().hex[:8]}.{file_ext}"
        file_path = FileService.get_file_path(
            current_user.sub, "prd", filename
        )

        # Upload to Supabase storage
        file_url = await supabase.upload_file_to_storage(
            file_path=file_path,
            file_content=content,
            bucket_name="documents"
        )

        # Extract text (if supported)
        raw_text = await FileService.extract_text_from_file(
            content, file_ext
        )

        # Create document record in database
        doc = await supabase.create_document(
            user_id=current_user.sub,
            org_id=current_user.org,
            doc_type="prd",
            title=title,
            description=description,
            file_path=file_path,
            file_url=file_url,
            file_size=file_size
        )

        # Update with extracted text
        if raw_text:
            await supabase.update_document_status(
                doc.id,
                status="processed",
                raw_text=raw_text
            )
        else:
            await supabase.update_document_status(
                doc.id,
                status="uploaded"
            )

        logger.info(f"PRD uploaded successfully: {doc.id}")

        return DocumentMetadata(
            id=doc.id,
            doc_type=doc.doc_type,
            title=doc.title,
            description=doc.description,
            file_url=file_url,
            file_size=file_size,
            uploaded_by=current_user.email,
            uploaded_at=doc.created_at,
            updated_at=doc.updated_at
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"PRD upload error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorMessages.FILE_UPLOAD_FAILED
        )


@router.post(
    "/design",
    response_model=DocumentMetadata,
    status_code=status.HTTP_201_CREATED
)
async def upload_design(
    file: UploadFile = File(..., description="Design document (PDF, DOCX, or TXT)"),
    title: str = Form(..., description="Document title"),
    description: Optional[str] = Form(None, description="Document description"),
    current_user: TokenPayload = Depends(get_current_user)
) -> DocumentMetadata:
    """
    Upload Design Documentation.
    
    **Files accepted**: PDF, DOCX, TXT (max 50MB)
    
    **Authorization**: Requires login
    
    **Parameters**:
    - file: Design document file
    - title: Document title (3-255 chars)
    - description: Optional description
    
    **Returns**: Document metadata with file URL
    """
    logger.info(f"Design document upload started: {file.filename} by {current_user.email}")

    try:
        # Validate title
        if not ValidationService.validate_document_title(title):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorMessages.INVALID_DOC_TITLE
            )

        # Validate upload
        content, file_size = await validate_upload(
            file, "design", current_user
        )

        # Generate storage path
        file_ext = FileService.get_file_extension(file.filename)
        filename = f"{title[:50]}_{uuid.uuid4().hex[:8]}.{file_ext}"
        file_path = FileService.get_file_path(
            current_user.sub, "design", filename
        )

        # Upload to Supabase storage
        file_url = await supabase.upload_file_to_storage(
            file_path=file_path,
            file_content=content,
            bucket_name="documents"
        )

        # Extract text
        raw_text = await FileService.extract_text_from_file(
            content, file_ext
        )

        # Create document record
        doc = await supabase.create_document(
            user_id=current_user.sub,
            org_id=current_user.org,
            doc_type="design",
            title=title,
            description=description,
            file_path=file_path,
            file_url=file_url,
            file_size=file_size
        )

        # Update with extracted text
        if raw_text:
            await supabase.update_document_status(
                doc.id,
                status="processed",
                raw_text=raw_text
            )
        else:
            await supabase.update_document_status(
                doc.id,
                status="uploaded"
            )

        logger.info(f"Design document uploaded successfully: {doc.id}")

        return DocumentMetadata(
            id=doc.id,
            doc_type=doc.doc_type,
            title=doc.title,
            description=doc.description,
            file_url=file_url,
            file_size=file_size,
            uploaded_by=current_user.email,
            uploaded_at=doc.created_at,
            updated_at=doc.updated_at
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Design upload error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorMessages.FILE_UPLOAD_FAILED
        )


@router.post(
    "/code",
    response_model=DocumentMetadata,
    status_code=status.HTTP_201_CREATED
)
async def upload_code(
    file: UploadFile = File(..., description="Code summary document (PDF, DOCX, or TXT)"),
    title: str = Form(..., description="Document title"),
    description: Optional[str] = Form(None, description="Document description"),
    current_user: TokenPayload = Depends(get_current_user)
) -> DocumentMetadata:
    """
    Upload Code Summary/Architecture Documentation.
    
    **Files accepted**: PDF, DOCX, TXT (max 50MB)
    
    **Authorization**: Requires login
    
    **Parameters**:
    - file: Code summary document file
    - title: Document title (3-255 chars)
    - description: Optional description
    
    **Returns**: Document metadata with file URL
    """
    logger.info(f"Code document upload started: {file.filename} by {current_user.email}")

    try:
        # Validate title
        if not ValidationService.validate_document_title(title):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorMessages.INVALID_DOC_TITLE
            )

        # Validate upload
        content, file_size = await validate_upload(
            file, "code", current_user
        )

        # Generate storage path
        file_ext = FileService.get_file_extension(file.filename)
        filename = f"{title[:50]}_{uuid.uuid4().hex[:8]}.{file_ext}"
        file_path = FileService.get_file_path(
            current_user.sub, "code", filename
        )

        # Upload to Supabase storage
        file_url = await supabase.upload_file_to_storage(
            file_path=file_path,
            file_content=content,
            bucket_name="documents"
        )

        # Extract text
        raw_text = await FileService.extract_text_from_file(
            content, file_ext
        )

        # Create document record
        doc = await supabase.create_document(
            user_id=current_user.sub,
            org_id=current_user.org,
            doc_type="code",
            title=title,
            description=description,
            file_path=file_path,
            file_url=file_url,
            file_size=file_size
        )

        # Update with extracted text
        if raw_text:
            await supabase.update_document_status(
                doc.id,
                status="processed",
                raw_text=raw_text
            )
        else:
            await supabase.update_document_status(
                doc.id,
                status="uploaded"
            )

        logger.info(f"Code document uploaded successfully: {doc.id}")

        return DocumentMetadata(
            id=doc.id,
            doc_type=doc.doc_type,
            title=doc.title,
            description=doc.description,
            file_url=file_url,
            file_size=file_size,
            uploaded_by=current_user.email,
            uploaded_at=doc.created_at,
            updated_at=doc.updated_at
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Code upload error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorMessages.FILE_UPLOAD_FAILED
        )
