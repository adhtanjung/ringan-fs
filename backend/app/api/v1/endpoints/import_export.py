"""
Import/Export API Endpoints
Handles file import/export operations with template generation
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query, UploadFile, File, Form
from fastapi.responses import StreamingResponse
import io

from app.services.import_export_service import import_export_service
from app.services.dataset_management_service import dataset_management_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/import-export", tags=["Import/Export"])


@router.get("/health")
async def health_check():
    """Health check for import/export service"""
    try:
        # Check database status
        db_status = "connected" if dataset_management_service.db is not None else "disconnected"

        # Check data counts
        data_counts = {}
        for data_type in import_export_service.data_types.keys():
            try:
                data = await dataset_management_service.get_all_data(data_type)
                data_counts[data_type] = len(data)
            except Exception as e:
                data_counts[data_type] = f"error: {str(e)}"

        return {
            "status": "healthy",
            "service": "import-export",
            "database_status": db_status,
            "supported_data_types": list(import_export_service.data_types.keys()),
            "supported_formats": import_export_service.supported_formats,
            "data_counts": data_counts
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/test-data/{data_type}")
async def test_data_retrieval(data_type: str):
    """Test data retrieval for debugging"""
    try:
        if data_type not in import_export_service.data_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid data type. Supported types: {list(import_export_service.data_types.keys())}"
            )

        logger.info(f"Testing data retrieval for {data_type}")
        data = await dataset_management_service.get_all_data(data_type)

        return {
            "data_type": data_type,
            "count": len(data),
            "sample_data": data[:2] if data else [],
            "database_connected": dataset_management_service.db is not None
        }

    except Exception as e:
        logger.error(f"Test data retrieval failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/template/{data_type}")
async def generate_template(
    data_type: str,
    format: str = Query("csv", description="Template format: csv, xlsx, or json")
):
    """Generate import template for a specific data type"""
    try:
        logger.info(f"Generating template for data_type={data_type}, format={format}")

        if data_type not in import_export_service.data_types:
            logger.error(f"Invalid data type: {data_type}")
            raise HTTPException(
                status_code=400,
                detail=f"Invalid data type. Supported types: {list(import_export_service.data_types.keys())}"
            )

        if format not in import_export_service.supported_formats:
            logger.error(f"Invalid format: {format}")
            raise HTTPException(
                status_code=400,
                detail=f"Invalid format. Supported formats: {import_export_service.supported_formats}"
            )

        logger.info(f"Generating {format} template for {data_type}")
        template_content = import_export_service.generate_template(data_type, format)
        logger.info(f"Template generated successfully: {len(template_content)} bytes")

        # Determine content type and filename
        content_types = {
            'csv': 'text/csv',
            'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'json': 'application/json'
        }

        extensions = {
            'csv': 'csv',
            'xlsx': 'xlsx',
            'json': 'json'
        }

        filename = f"{data_type}_template.{extensions[format]}"

        return StreamingResponse(
            io.BytesIO(template_content),
            media_type=content_types[format],
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    except Exception as e:
        logger.error(f"Template generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/import/{data_type}")
async def import_data(
    data_type: str,
    file: UploadFile = File(...),
    overwrite: bool = Form(False),
    validate: bool = Form(True)
):
    """Import data from uploaded file"""
    try:
        if data_type not in import_export_service.data_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid data type. Supported types: {list(import_export_service.data_types.keys())}"
            )

        # Read file content
        file_content = await file.read()

        # Import data
        result = await import_export_service.import_data(
            file_content=file_content,
            filename=file.filename,
            data_type=data_type,
            overwrite=overwrite,
            validate=validate
        )

        return {
            "success": result["success"],
            "message": result.get("message", "Import completed"),
            "imported_count": result.get("imported_count", 0),
            "failed_count": result.get("failed_count", 0),
            "errors": result.get("errors", []),
            "warnings": result.get("warnings", [])
        }

    except Exception as e:
        logger.error(f"Import failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export/{data_type}")
async def export_data(
    data_type: str,
    format: str = Query("csv", description="Export format: csv, xlsx, or json"),
    domain: Optional[str] = Query(None, description="Filter by domain"),
    is_active: Optional[bool] = Query(None, description="Filter by active status")
):
    """Export data to file"""
    try:
        if data_type not in import_export_service.data_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid data type. Supported types: {list(import_export_service.data_types.keys())}"
            )

        if format not in import_export_service.supported_formats:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid format. Supported formats: {import_export_service.supported_formats}"
            )

        # Build filters
        filters = {}
        if domain:
            filters["domain"] = domain
        if is_active is not None:
            filters["is_active"] = is_active

        logger.info(f"Exporting {data_type} in {format} format with filters: {filters}")

        # Export data
        file_content = await import_export_service.export_data(
            data_type=data_type,
            format=format,
            filters=filters if filters else None
        )

        logger.info(f"Export completed: {len(file_content)} bytes generated")

        # Determine content type and filename
        content_types = {
            'csv': 'text/csv',
            'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'json': 'application/json'
        }

        extensions = {
            'csv': 'csv',
            'xlsx': 'xlsx',
            'json': 'json'
        }

        filename = f"{data_type}_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{extensions[format]}"

        return StreamingResponse(
            io.BytesIO(file_content),
            media_type=content_types[format],
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    except Exception as e:
        logger.error(f"Export failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/supported-types")
async def get_supported_types():
    """Get list of supported data types and formats"""
    return {
        "data_types": list(import_export_service.data_types.keys()),
        "formats": import_export_service.supported_formats,
        "descriptions": {
            "problems": "Mental health problem categories",
            "assessments": "Assessment questions and responses",
            "suggestions": "Therapeutic suggestions and interventions",
            "feedback_prompts": "User feedback collection prompts",
            "next_actions": "Recommended follow-up actions",
            "training_examples": "Fine-tuning examples for AI models"
        }
    }


@router.get("/field-schema/{data_type}")
async def get_field_schema(data_type: str):
    """Get field schema and validation rules for a data type"""
    try:
        if data_type not in import_export_service.data_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid data type. Supported types: {list(import_export_service.data_types.keys())}"
            )

        model_class = import_export_service.data_types[data_type]
        schema = model_class.model_json_schema()

        return {
            "data_type": data_type,
            "schema": schema,
            "field_instructions": import_export_service._get_field_instructions(data_type),
            "sample_data": import_export_service._create_template_data(data_type)
        }

    except Exception as e:
        logger.error(f"Schema retrieval failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
