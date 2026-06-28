from pydantic import BaseModel, Field
from app.core.errors import ErrorCode, ERROR_CODE_DESC
from typing import Optional, List, Generic, TypeVar, Any
from datetime import datetime
from app.core.middleware import request_trace_id

T = TypeVar('T')

# 生成详细的错误码描述文本
_codes_desc = "\n".join([f"- {code.value}: {desc}" for code, desc in ERROR_CODE_DESC.items()])
_code_field_desc = f"业务状态码。详细对照表：\n\n{_codes_desc}"

def get_current_trace_id():
    return request_trace_id.get()

class BaseResponse(BaseModel):
    """基础响应模型"""
    code: int = Field(ErrorCode.SUCCESS, description=_code_field_desc, example=200)
    message: str = Field("success", description="状态描述信息", example="success")
    data: Optional[Any] = Field(None, description="业务数据载荷")
    timestamp: datetime = Field(default_factory=datetime.now, description="服务器响应时间")
    trace_id: Optional[str] = Field(default_factory=get_current_trace_id, description="全链路追踪 ID", example="a1b2c3d4-e5f6-7890-1234-567890abcdef")

class ErrorResponse(BaseModel):
    """统一错误响应模型"""
    code: int = Field(..., description=_code_field_desc, example=4001)
    message: str = Field(..., description="错误简要说明", example="Invalid Parameter")
    detail: Optional[str] = Field(None, description="错误详细描述或技术细节", example="Parameter 'resource' is required")
    data: Any = Field(None, description="通常为 null")
    timestamp: datetime = Field(default_factory=datetime.now, description="错误发生时间")
    trace_id: str = Field(..., description="全链路追踪 ID", example="err-trace-001")

# 用于 OpenAPI 文档的通用响应定义
COMMON_ERROR_RESPONSES = {
    400: {"model": ErrorResponse, "description": "请求错误 (参数不合法)"},
    401: {"model": ErrorResponse, "description": "认证失败 (API Key 无效或缺失)"},
    403: {"model": ErrorResponse, "description": "权限不足 (未授权访问该资源)"},
    429: {"model": ErrorResponse, "description": "触发限流"},
    500: {"model": ErrorResponse, "description": "服务器内部错误"},
    503: {"model": ErrorResponse, "description": "服务暂时不可用 (数据库连接失败)"}
}

class DataQueryParams(BaseModel):
    """通用查询参数"""
    start_time: Optional[str] = Field(None, description="开始时间 (YYYY-MM-DD HH:MM:SS)", example="2025-01-01 00:00:00")
    end_time: Optional[str] = Field(None, description="结束时间 (YYYY-MM-DD HH:MM:SS)", example="2025-12-31 23:59:59")
    resource_id: Optional[str] = Field(None, description="资源ID（点位 id）。支持传入多个 ID，以逗号分隔。", example="res-001,res-002")
    metric_name: Optional[str] = Field(None, description="指标名称过滤", example="temperature")
    page: int = Field(1, description="页码，从 1 开始", ge=1, example=1)
    size: int = Field(20, description="每页返回数量，最大 1000", ge=1, le=1000, example=20)
    sort_by: Optional[str] = Field(None, description="排序字段名", example="metric_time")
    sort_order: Optional[str] = Field("desc", description="排序方式：`asc` (升序) 或 `desc` (降序)", example="desc")

class DonghuanRealMetricResponse(BaseModel):
    """对应 ck_fact_donghuan_real_metric_hbase"""
    rowkey: str = Field(..., description="唯一行键标识", example="row-20250101-001")
    c_datacenter_id: Optional[str] = Field(None, description="数据中心 ID", example="DC-SH-01")
    c_source_ip: Optional[str] = Field(None, description="源 IP 地址", example="192.168.1.100")
    c_source_mode: Optional[str] = Field(None, description="源采集模式", example="PULL")
    resource_id: Optional[str] = Field(None, description="资源 ID", example="UPS-A-01")
    metric_name: Optional[str] = Field(None, description="监控指标名称", example="output_voltage")
    metric_value: Optional[str] = Field(None, description="指标当前值", example="220.5")
    metric_unit: Optional[str] = Field(None, description="指标单位", example="V")
    metric_time: str = Field(..., description="指标采集时间 (时间戳)", example="1765852325")
    status: Optional[str] = Field(None, description="指标状态", example="normal")

class DonghuanEventResponse(BaseModel):
    """对应 ck_fact_donghuan_event_detail_hbase"""
    rowkey: str = Field(..., description="唯一行键标识", example="evt-20250101-999")
    c_datacenter_id: Optional[str] = Field(None, description="数据中心 ID", example="DC-BJ-02")
    c_source_ip: Optional[str] = Field(None, description="源 IP 地址")
    c_source_mode: Optional[str] = Field(None, description="源采集模式")
    event_id: Optional[str] = Field(None, description="事件 ID", example="EVT-100200")
    resource_id: Optional[str] = Field(None, description="关联资源 ID", example="TEMP-SENSOR-05")
    resource_name: Optional[str] = Field(None, description="资源名称", example="2号机房温湿度传感器")
    event_type: Optional[str] = Field(None, description="事件类型", example="threshold_alarm")
    event_level: Optional[str] = Field(None, description="事件级别 (1-5)", example="3")
    event_message: Optional[str] = Field(None, description="事件详细描述", example="Temperature exceeded 35°C")
    event_time: str = Field(..., description="事件发生时间 (时间戳)", example="1765480784")
    event_status: Optional[str] = Field(None, description="事件当前状态 (0/1)", example="0")
    event_location: Optional[str] = Field(None, description="位置 ID")
    event_location_name: Optional[str] = Field(None, description="事件发生位置名称", example="Beijing Room 2, Rack A05")
    event_device_type: Optional[str] = Field(None, description="设备类型编码")
    event_snapshot: Optional[str] = Field(None, description="事件快照数据")
    confirm_time: Optional[str] = Field(None, description="确认时间")
    confirm_by: Optional[str] = Field(None, description="确认人")
    confirm_description: Optional[str] = Field(None, description="确认描述")
    recover_time: Optional[str] = Field(None, description="恢复时间")
    recover_by: Optional[str] = Field(None, description="恢复人")
    recover_snapshot: Optional[str] = Field(None, description="恢复快照")
    remove_time: Optional[str] = Field(None, description="清除时间")
    remove_by: Optional[str] = Field(None, description="清除人")
    remove_description: Optional[str] = Field(None, description="清除描述")
    accept_time: Optional[str] = Field(None, description="受理时间")
    accept_by: Optional[str] = Field(None, description="受理人")

class YunshuRoomResponse(BaseModel):
    """对应 ck_fact_yunshu_resroom_hbase 机房"""
    rowkey: str = Field(..., description="唯一行键标识", example="room-bj-01")
    id: Optional[str] = Field(None, description="机房 ID")
    ywzx: Optional[str] = Field(None, description="所属业务中心", example="华北业务中心")
    jgzs: Optional[str] = Field(None, description="机柜总数", example="1550")
    modedatamodifydatetime: Optional[str] = Field(None, description="修改时间")
    sjjfs: Optional[str] = Field(None, description="设计机房数")
    sykss: Optional[str] = Field(None, description="使用颗数")
    gxqy: Optional[str] = Field(None, description="管辖区域")
    jfmc: Optional[str] = Field(None, description="机房名称", example="北京亦庄一号机房")
    belongmidperiod: Optional[str] = Field(None, description="所属中期")
    yeszjid: Optional[str] = Field(None, description="YesZjID")
    jfbm: Optional[str] = Field(None, description="机房编码", example="BJ-ROOM-001")
    modeuuid: Optional[str] = Field(None, description="Mode UUID")
    jfjc: Optional[str] = Field(None, description="机房简称")
    bkys: Optional[str] = Field(None, description="板块映射")
    yqys: Optional[str] = Field(None, description="园区映射")
    yjfs: Optional[str] = Field(None, description="已建机房数")
    dz: Optional[str] = Field(None, description="地址")
    form_biz_id: Optional[str] = Field(None, description="表单业务 ID")
    outkey: Optional[str] = Field(None, description="外部键")
    belongship: Optional[str] = Field(None, description="归属关系")
    nbjys: Optional[str] = Field(None, description="内部简易数")
    co: Optional[str] = Field(None, description="CO")
    modedatacreatetime: Optional[str] = Field(None, description="创建时间")
    bz: Optional[str] = Field(None, description="备注")
    requestid: Optional[str] = Field(None, description="请求 ID")
    modedatamodifier: Optional[str] = Field(None, description="修改人")
    kss: Optional[str] = Field(None, description="颗数")
    cc: Optional[str] = Field(None, description="CC")
    kqzt: Optional[str] = Field(None, description="考勤状态")
    gsbs: Optional[str] = Field(None, description="公司标识", example="Yovole")
    modedatacreatedate: Optional[str] = Field(None, description="创建日期")
    px: Optional[str] = Field(None, description="排序")
    khmc: Optional[str] = Field(None, description="客户名称")
    modedatacreater: Optional[str] = Field(None, description="创建人")
    jfzdl: Optional[str] = Field(None, description="机房总电力")
    dhjkkqzt: Optional[str] = Field(None, description="动环监控考勤状态")
    formmodeid: Optional[str] = Field(None, description="表单模式 ID")
    modedatacreatertype: Optional[str] = Field(None, description="创建人类型")

class YunshuRackResponse(BaseModel):
    """对应 ck_fact_yunshu_resjj_hbase 机架"""
    rowkey: str = Field(..., description="唯一行键标识", example="rack-bj-01-a01")
    id: Optional[str] = Field(None, description="机架 ID")
    jjbmyh: Optional[str] = Field(None, description="机架编码 (原有)")
    kh: Optional[str] = Field(None, description="客户 ID", example="CUST-001")
    akg: Optional[str] = Field(None, description="A 路开关")
    form_biz_id: Optional[str] = Field(None, description="表单业务 ID")
    ywzx: Optional[str] = Field(None, description="业务中心")
    modedatacreatedate: Optional[str] = Field(None, description="创建日期")
    nbjjsfsd: Optional[str] = Field(None, description="内部机架是否锁定")
    sfwc: Optional[str] = Field(None, description="是否完成")
    ac19: Optional[str] = Field(None, description="A 路 C19")
    wdslaxx: Optional[str] = Field(None, description="温度数量下限")
    dhzt: Optional[str] = Field(None, description="动环状态")
    modedatacreatertype: Optional[str] = Field(None, description="创建人类型")
    bkgzt: Optional[str] = Field(None, description="B 路开关状态")
    formmodeid: Optional[str] = Field(None, description="表单模式 ID")
    ac13: Optional[str] = Field(None, description="A 路 C13")
    jfmc: Optional[str] = Field(None, description="所属机房名称", example="北京亦庄一号机房")
    sdslaxx: Optional[str] = Field(None, description="湿度数量下限")
    col: Optional[str] = Field(None, description="列")
    mk: Optional[str] = Field(None, description="模块")
    ztsm: Optional[str] = Field(None, description="状态说明")
    jjzt: Optional[str] = Field(None, description="机架状态", example="已分配")
    akgzt: Optional[str] = Field(None, description="A 路开关状态")
    modeuuid: Optional[str] = Field(None, description="Mode UUID")
    jjbm: Optional[str] = Field(None, description="机架编码", example="A01")
    modedatamodifydatetime: Optional[str] = Field(None, description="修改时间")
    sdzt: Optional[str] = Field(None, description="锁定状态")
    jjbmyys: Optional[str] = Field(None, description="机架编码 (运营商)")
    wdslasx: Optional[str] = Field(None, description="温度数量上限")
    bkg: Optional[str] = Field(None, description="B 路开关")
    modedatacreater: Optional[str] = Field(None, description="创建人")
    bc13: Optional[str] = Field(None, description="B 路 C13")
    requestid: Optional[str] = Field(None, description="请求 ID")
    modedatamodifier: Optional[str] = Field(None, description="修改人")
    htbm: Optional[str] = Field(None, description="合同编码")
    bzdl: Optional[str] = Field(None, description="标准电力")
    sddl: Optional[str] = Field(None, description="锁定电力")
    pdulx: Optional[str] = Field(None, description="PDU 类型")
    outkey: Optional[str] = Field(None, description="外部键")
    zzkh: Optional[str] = Field(None, description="最终客户")
    apdu: Optional[str] = Field(None, description="A 路 PDU")
    sfzy: Optional[str] = Field(None, description="是否占用")
    jjlx: Optional[str] = Field(None, description="机架类型")
    khmc: Optional[str] = Field(None, description="客户名称", example="某互联网大厂")
    bpdu: Optional[str] = Field(None, description="B 路 PDU")
    dhztrq: Optional[str] = Field(None, description="动环状态日期")
    xnjj: Optional[str] = Field(None, description="虚拟机架")
    sdrq: Optional[str] = Field(None, description="锁定日期")
    bc19: Optional[str] = Field(None, description="B 路 C19")
    sdslasx: Optional[str] = Field(None, description="湿度数量上限")
    srlx: Optional[str] = Field(None, description="散热类型")
    lc: Optional[str] = Field(None, description="楼层")
    modedatacreatetime: Optional[str] = Field(None, description="创建时间")
    zzkhbm: Optional[str] = Field(None, description="最终客户编码")
    jfbm: Optional[str] = Field(None, description="机房编码")

class YunshuDevicePointResponse(BaseModel):
    """对应 ck_fact_yunshu_devicepoint_hbase 设备点位"""
    rowkey: str = Field(..., description="唯一行键标识", example="point-sh-02-ups-1")
    id: Optional[str] = Field(None, description="点位 ID")
    modedatamodifier: Optional[str] = Field(None, description="修改人")
    dwmc: Optional[str] = Field(None, description="点位名称", example="进线A相电压")
    modedatacreatetime: Optional[str] = Field(None, description="创建时间")
    modedatacreatertype: Optional[str] = Field(None, description="创建人类型")
    szwz: Optional[str] = Field(None, description="所在位置")
    jf: Optional[str] = Field(None, description="所属机房", example="上海一号机房")
    modedatacreater: Optional[str] = Field(None, description="创建人")
    modedatamodifydatetime: Optional[str] = Field(None, description="修改时间")
    sztd: Optional[str] = Field(None, description="所在通道")
    requestid: Optional[str] = Field(None, description="请求 ID")
    jc: Optional[str] = Field(None, description="简称")
    dyztid: Optional[str] = Field(None, description="对应状态 ID")
    xgsb: Optional[str] = Field(None, description="相关设备")
    modeuuid: Optional[str] = Field(None, description="Mode UUID")
    form_biz_id: Optional[str] = Field(None, description="表单业务 ID")
    sbjc: Optional[str] = Field(None, description="设备简称")
    jjbm: Optional[str] = Field(None, description="机架编码", example="B05")
    dwid: Optional[str] = Field(None, description="点位 ID", example="P-102030")
    formmodeid: Optional[str] = Field(None, description="表单模式 ID")
    szlc: Optional[str] = Field(None, description="所在楼层")
    dwlx: Optional[str] = Field(None, description="点位类型", example="智能电表")
    modedatacreatedate: Optional[str] = Field(None, description="创建日期")
    szmk: Optional[str] = Field(None, description="所在模块")
    metric_time: Optional[str] = Field(None, description="指标时间")
    metric_value: Optional[str] = Field(None, description="指标值")

class EventQueryParams(DataQueryParams):
    """事件查询专用参数"""
    event_level: Optional[str] = Field(None, description="事件级别筛选 (warning/error/critical)", example="critical")
    event_type: Optional[str] = Field(None, description="事件类型筛选", example="threshold_alarm")
    event_status: Optional[str] = Field(None, description="事件状态筛选 (active/resolved)", example="active")

class MetricTimeRange(BaseModel):
    start_time: str = Field(..., example="2025-01-01 00:00:00")
    end_time: str = Field(..., example="2025-01-02 00:00:00")

class DonghuanMetricSummaryData(BaseModel):
    average_temperature: float = Field(..., description="平均温度", example=24.5)
    min_temperature: float = Field(..., description="最低温度", example=20.1)
    max_temperature: float = Field(..., description="最高温度", example=28.3)
    count: int = Field(..., description="采样点数量", example=1440)
    time_range: MetricTimeRange

class DonghuanMetricSummaryResponse(BaseResponse):
    data: DonghuanMetricSummaryData

class PageData(BaseModel, Generic[T]):
    items: List[T] = Field(..., description="当前页的数据项列表")
    total: int = Field(..., description="总记录数", example=100)
    page: int = Field(..., description="当前页码", example=1)
    size: int = Field(..., description="每页大小", example=20)
    pages: int = Field(..., description="总页数", example=5)

class DataPageResponse(BaseResponse, Generic[T]):
    data: PageData[T]
