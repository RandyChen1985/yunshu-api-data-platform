from .base import DataSourceAdapter
from .clickhouse import ClickHouseAdapter
from .mysql import MySQLAdapter
from .oracle import OracleAdapter
import logging

logger = logging.getLogger(__name__)

async def get_adapter(data_source_name: str = "default_clickhouse") -> DataSourceAdapter:
    """
    Get appropriate adapter for a data source by name.
    Looks up the data source config and returns the correct adapter type.
    """
    from app.services.datasource_service import DataSourceService
    
    # Get data source config
    datasource = await DataSourceService.get_datasource_by_name(data_source_name)
    if not datasource:
        logger.error(f"Data source not found: {data_source_name}")
        raise ValueError(f"Data source '{data_source_name}' not found")
    
    if datasource.status != 1:
        logger.warning(f"Data source is inactive: {data_source_name}")
        raise ValueError(f"Data source '{data_source_name}' is inactive")
    
    logger.debug(f"Selecting adapter for source: {data_source_name} (Type: {datasource.source_type}, ID: {datasource.id})")

    # Return appropriate adapter
    if datasource.source_type == "clickhouse":
        return ClickHouseAdapter(datasource.id)
    elif datasource.source_type == "mysql":
        return MySQLAdapter(datasource.id)
    elif datasource.source_type == "oracle":
        return OracleAdapter(datasource.id)
    else:
        logger.error(f"Unsupported data source type: {datasource.source_type}")
        raise NotImplementedError(f"Adapter for {datasource.source_type} is not implemented.")
