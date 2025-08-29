"""
Data Import API Endpoints
Handles importing and processing Excel mental health datasets
"""

import logging
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Query

from app.services.data_import_service import data_import_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/import/all")
async def import_all_data():
    """Import and process all mental health datasets"""
    try:
        logger.info("🔄 Starting import of all mental health data")

        result = await data_import_service.import_all_data()

        if result.get("success", False):
            return {
                "message": "Data import completed successfully",
                "results": result
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Data import failed: {result.get('error', 'Unknown error')}"
            )

    except Exception as e:
        logger.error(f"❌ Data import failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/import/{domain}")
async def import_domain_data(domain: str):
    """Import and process data for a specific domain"""
    try:
        logger.info(f"🔄 Starting import for domain: {domain}")

        result = await data_import_service.import_domain_data(domain)

        if result.get("success", False):
            return {
                "message": f"Data import completed successfully for {domain}",
                "results": result
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Data import failed for {domain}: {result.get('error', 'Unknown error')}"
            )

    except Exception as e:
        logger.error(f"❌ Data import failed for {domain}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/domains")
async def get_available_domains():
    """Get list of available domains for import"""
    try:
        return {
            "domains": list(data_import_service.excel_files.keys()),
            "files": data_import_service.excel_files
        }
    except Exception as e:
        logger.error(f"❌ Failed to get domains: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_import_status():
    """Get current import status and statistics"""
    try:
        # Get collection stats
        await data_import_service.initialize()

        # Import vector_service directly
        from app.services.vector_service import vector_service
        stats = await vector_service.get_collection_stats()

        return {
            "status": "ready",
            "available_domains": list(data_import_service.excel_files.keys()),
            "collection_stats": stats,
            "data_directory": str(data_import_service.data_dir)
        }
    except Exception as e:
        logger.error(f"❌ Failed to get import status: {str(e)}")
        return {
            "status": "error",
            "error": str(e)
        }


@router.post("/validate")
async def validate_excel_files():
    """Validate Excel files and return file information"""
    try:
        validation_results = {}

        for domain, filename in data_import_service.excel_files.items():
            file_path = data_import_service.data_dir / filename

            if file_path.exists():
                try:
                    # Try to read the file
                    sheets = data_import_service.read_excel_file(file_path)

                    validation_results[domain] = {
                        "file_exists": True,
                        "filename": filename,
                        "sheets": list(sheets.keys()),
                        "sheet_count": len(sheets),
                        "status": "valid"
                    }

                    # Check for required sheets
                    required_sheets = [
                        "1.1 Problems", "1.2 Self Assessment",
                        "1.3 Suggestions", "1.4 Feedback Prompts",
                        "1.5 Next Action After Feedback", "1.6 FineTuning Examples"
                    ]

                    missing_sheets = [sheet for sheet in required_sheets if sheet not in sheets]
                    if missing_sheets:
                        validation_results[domain]["missing_sheets"] = missing_sheets
                        validation_results[domain]["status"] = "incomplete"

                except Exception as e:
                    validation_results[domain] = {
                        "file_exists": True,
                        "filename": filename,
                        "status": "error",
                        "error": str(e)
                    }
            else:
                validation_results[domain] = {
                    "file_exists": False,
                    "filename": filename,
                    "status": "missing"
                }

        return {
            "validation_results": validation_results,
            "total_domains": len(validation_results)
        }

    except Exception as e:
        logger.error(f"❌ File validation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/initialize")
async def initialize_services():
    """Initialize vector database and embedding services"""
    try:
        success = await data_import_service.initialize()

        if success:
            return {
                "message": "Services initialized successfully",
                "status": "ready"
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to initialize services"
            )

    except Exception as e:
        logger.error(f"❌ Service initialization failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def data_import_health_check():
    """Check data import service health"""
    try:
        # Check if data directory exists
        data_dir_exists = data_import_service.data_dir.exists()

        # Check if Excel files exist
        file_status = {}
        for domain, filename in data_import_service.excel_files.items():
            file_path = data_import_service.data_dir / filename
            file_status[domain] = {
                "exists": file_path.exists(),
                "filename": filename
            }

        return {
            "status": "healthy" if data_dir_exists else "unhealthy",
            "data_directory": str(data_import_service.data_dir),
            "data_directory_exists": data_dir_exists,
            "file_status": file_status,
            "available_domains": list(data_import_service.excel_files.keys())
        }

    except Exception as e:
        logger.error(f"❌ Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }
