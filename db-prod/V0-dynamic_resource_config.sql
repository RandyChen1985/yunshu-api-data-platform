-- V0: Initialize Complete Database Schema
-- Date: 2025-12-30
-- Description: Create core tables (api_users, api_access_logs) and sys_resource_meta table with initial data.

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Create database if not exists
-- ----------------------------
CREATE DATABASE IF NOT EXISTS yunshu_api_data_platform;
USE yunshu_api_data_platform;

-- ----------------------------
-- 1. Table: api_users
-- ----------------------------
DROP TABLE IF EXISTS api_users;
CREATE TABLE api_users (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_name VARCHAR(64) NOT NULL UNIQUE,
    api_key_encrypted TEXT COMMENT '加密存储的 API Key（Fernet 加密，可解密）',
    api_key_hash VARCHAR(64) NOT NULL UNIQUE COMMENT 'SHA256 哈希值（用于快速验证）',
    role VARCHAR(32) DEFAULT 'user' COMMENT 'admin or user',
    remark VARCHAR(500) DEFAULT NULL COMMENT '备注',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    status TINYINT DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- 2. Table: api_access_logs
-- ----------------------------
DROP TABLE IF EXISTS api_access_logs;
CREATE TABLE api_access_logs (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    trace_id VARCHAR(64) NOT NULL,
    user_id BIGINT,
    user_name VARCHAR(64),
    endpoint VARCHAR(255) NOT NULL,
    method VARCHAR(10) NOT NULL,
    query_params TEXT,
    status_code INT NOT NULL,
    process_time_ms FLOAT NOT NULL,
    client_ip VARCHAR(45),
    request_params TEXT COMMENT '请求参数(JSON格式)',
    response_body TEXT COMMENT '响应内容(JSON格式)',
    error_message TEXT COMMENT '错误信息',
    user_agent VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_trace_id (trace_id),
    INDEX idx_logs_created_at (created_at),
    INDEX idx_logs_status_code (status_code),
    INDEX idx_logs_method (method),
    INDEX idx_logs_user_name (user_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Table structure for sys_resource_meta
-- ----------------------------
DROP TABLE IF EXISTS `sys_resource_meta`;
CREATE TABLE `sys_resource_meta` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT 'Primary Key',
  `resource_key` varchar(100) NOT NULL COMMENT 'Unique resource key used in API',
  `resource_name` varchar(100) NOT NULL COMMENT 'Human readable name',
  `resource_group` varchar(50) NOT NULL DEFAULT 'Default' COMMENT 'Group name for documentation and permission categorization',
  `data_source` varchar(50) NOT NULL DEFAULT 'default_clickhouse' COMMENT 'Data source type (clickhouse, mysql, etc.)',
  `resource_mode` varchar(20) NOT NULL DEFAULT 'TABLE' COMMENT 'Mode: TABLE or SQL',
  `table_name` varchar(200) DEFAULT NULL COMMENT 'Physical table name (used if mode=TABLE)',
  `custom_sql` text DEFAULT NULL COMMENT 'Custom SQL query (used if mode=SQL). Subquery logic will be applied.',
  `fields_config` json NOT NULL COMMENT 'List of fields to select/return',
  `allowed_filters` json NOT NULL COMMENT 'List of allowed filter fields',
  `default_sort` varchar(100) NOT NULL DEFAULT 'rowkey' COMMENT 'Default sort field',
  `status` tinyint(4) NOT NULL DEFAULT '1' COMMENT 'Status: 1-Active, 0-Inactive',
  `remarks` text DEFAULT NULL COMMENT '备注',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation time',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Update time',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_resource_key` (`resource_key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Dynamic Resource Configuration Metadata';

-- ----------------------------
-- Records of sys_resource_meta
-- ----------------------------
BEGIN;

-- 1. 动环实时指标 (Donghuan Real Metrics)
INSERT INTO `sys_resource_meta` (`resource_key`, `resource_name`, `resource_group`, `data_source`, `table_name`, `fields_config`, `allowed_filters`, `default_sort`, `status`) VALUES (
    'donghuan_real_metrics', 
    '动环实时指标', 
    '动环数据', 
    'default_clickhouse', 
    'ck_fact_donghuan_real_metric_hbase', 
    '[{"name": "rowkey", "label": "行键", "type": "String"}, {"name": "c_datacenter_id", "label": "数据中心ID", "type": "String"}, {"name": "c_source_ip", "label": "源IP", "type": "String"}, {"name": "c_source_mode", "label": "源模式", "type": "String"}, {"name": "resource_id", "label": "资源ID", "type": "String"}, {"name": "metric_name", "label": "指标名称", "type": "String"}, {"name": "metric_value", "label": "指标值", "type": "String"}, {"name": "metric_unit", "label": "指标单位", "type": "String"}, {"name": "metric_time", "label": "指标时间(时间戳)", "type": "String"}, {"name": "status", "label": "状态", "type": "String"}]',
    '[{"name": "c_datacenter_id", "label": "数据中心ID", "type": "String"}, {"name": "resource_id", "label": "资源ID", "type": "String"}, {"name": "metric_name", "label": "指标名称", "type": "String"}]',
    'metric_time',
    1
);

-- 2. 动环告警事件 (Donghuan Events)
INSERT INTO `sys_resource_meta` (`resource_key`, `resource_name`, `resource_group`, `data_source`, `table_name`, `fields_config`, `allowed_filters`, `default_sort`, `status`) VALUES (
    'donghuan_events', 
    '动环告警事件', 
    '动环数据', 
    'default_clickhouse', 
    'ck_fact_donghuan_event_detail_hbase', 
    '[{"name": "rowkey", "label": "行键", "type": "String"}, {"name": "c_datacenter_id", "label": "数据中心ID", "type": "String"}, {"name": "c_source_ip", "label": "源IP", "type": "String"}, {"name": "c_source_mode", "label": "源模式", "type": "String"}, {"name": "event_id", "label": "事件ID", "type": "String"}, {"name": "resource_id", "label": "资源ID", "type": "String"}, {"name": "resource_name", "label": "资源名称", "type": "String"}, {"name": "event_type", "label": "事件类型", "type": "String"}, {"name": "event_level", "label": "事件等级", "type": "String"}, {"name": "event_message", "label": "事件内容", "type": "String"}, {"name": "event_time", "label": "发生时间(时间戳)", "type": "String"}, {"name": "event_status", "label": "事件状态", "type": "String"}, {"name": "event_location", "label": "位置", "type": "String"}, {"name": "event_location_name", "label": "位置名称", "type": "String"}, {"name": "event_device_type", "label": "设备类型", "type": "String"}, {"name": "event_snapshot", "label": "快照", "type": "String"}, {"name": "confirm_time", "label": "确认时间", "type": "String"}, {"name": "confirm_by", "label": "确认人", "type": "String"}, {"name": "confirm_description", "label": "确认描述", "type": "String"}, {"name": "recover_time", "label": "恢复时间(时间戳)", "type": "String"}, {"name": "recover_by", "label": "恢复人", "type": "String"}, {"name": "recover_snapshot", "label": "恢复快照", "type": "String"}, {"name": "remove_time", "label": "清除时间", "type": "String"}, {"name": "remove_by", "label": "清除人", "type": "String"}, {"name": "remove_description", "label": "清除描述", "type": "String"}, {"name": "accept_time", "label": "受理时间", "type": "String"}, {"name": "accept_by", "label": "受理人", "type": "String"}]',
    '[{"name": "c_datacenter_id", "label": "数据中心ID", "type": "String"}, {"name": "resource_id", "label": "资源ID", "type": "String"}, {"name": "event_level", "label": "事件等级", "type": "String"}, {"name": "event_status", "label": "事件状态", "type": "String"}]',
    'event_time',
    1
);

-- 3. 云枢机房 (Yunshu Rooms)
INSERT INTO `sys_resource_meta` (`resource_key`, `resource_name`, `resource_group`, `data_source`, `table_name`, `fields_config`, `allowed_filters`, `default_sort`, `status`) VALUES (
    'yunshu_rooms', 
    '机房列表', 
    '智服平台', 
    'default_clickhouse', 
    'ck_fact_yunshu_resroom_hbase', 
    '[{"name": "rowkey", "label": "行键", "type": "String"}, {"name": "id", "label": "ID", "type": "String"}, {"name": "ywzx", "label": "业务中心", "type": "String"}, {"name": "jgzs", "label": "机柜总数", "type": "String"}, {"name": "modedatamodifydatetime", "label": "修改时间", "type": "String"}, {"name": "sjjfs", "label": "设计机房数", "type": "String"}, {"name": "sykss", "label": "使用颗数", "type": "String"}, {"name": "gxqy", "label": "管辖区域", "type": "String"}, {"name": "jfmc", "label": "机房名称", "type": "String"}, {"name": "belongmidperiod", "label": "-", "type": "String"}, {"name": "yeszjid", "label": "YesZjID", "type": "String"}, {"name": "jfbm", "label": "机房编码", "type": "String"}, {"name": "modeuuid", "label": "-", "type": "String"}, {"name": "jfjc", "label": "机房简称", "type": "String"}, {"name": "bkys", "label": "板块映射", "type": "String"}, {"name": "yqys", "label": "园区映射", "type": "String"}, {"name": "yjfs", "label": "已建机房数", "type": "String"}, {"name": "dz", "label": "地址", "type": "String"}, {"name": "form_biz_id", "label": "表单业务ID", "type": "String"}, {"name": "outkey", "label": "外部键", "type": "String"}, {"name": "belongship", "label": "-", "type": "String"}, {"name": "nbjys", "label": "内部简易数", "type": "String"}, {"name": "co", "label": "-", "type": "String"}, {"name": "modedatacreatetime", "label": "创建时间", "type": "String"}, {"name": "bz", "label": "备注", "type": "String"}, {"name": "requestid", "label": "请求ID", "type": "String"}, {"name": "modedatamodifier", "label": "修改人", "type": "String"}, {"name": "kss", "label": "颗数", "type": "String"}, {"name": "cc", "label": "-", "type": "String"}, {"name": "kqzt", "label": "考勤状态", "type": "String"}, {"name": "gsbs", "label": "公司标识", "type": "String"}, {"name": "modedatacreatedate", "label": "创建日期", "type": "String"}, {"name": "px", "label": "排序", "type": "String"}, {"name": "khmc", "label": "客户名称", "type": "String"}, {"name": "modedatacreater", "label": "创建人", "type": "String"}, {"name": "jfzdl", "label": "机房总电力", "type": "String"}, {"name": "dhjkkqzt", "label": "动环监控考勤状态", "type": "String"}, {"name": "formmodeid", "label": "表单模式ID", "type": "String"}, {"name": "modedatacreatertype", "label": "创建人类型", "type": "String"}]',
    '[{"name": "jfbm", "label": "机房编码", "type": "String"}, {"name": "jfmc", "label": "机房名称", "type": "String"}, {"name": "ywzx", "label": "业务中心", "type": "String"}]',
    'rowkey',
    1
);

-- 4. 云枢机架 (Yunshu Racks)
INSERT INTO `sys_resource_meta` (`resource_key`, `resource_name`, `resource_group`, `data_source`, `table_name`, `fields_config`, `allowed_filters`, `default_sort`, `status`) VALUES (
    'yunshu_racks', 
    '机架列表', 
    '智服平台', 
    'default_clickhouse', 
    'ck_fact_yunshu_resjj_hbase', 
    '[{"name": "rowkey", "label": "行键", "type": "String"}, {"name": "id", "label": "ID", "type": "String"}, {"name": "jjbmyh", "label": "机架编码(原有)", "type": "String"}, {"name": "kh", "label": "客户", "type": "String"}, {"name": "akg", "label": "A路开关", "type": "String"}, {"name": "form_biz_id", "label": "表单业务ID", "type": "String"}, {"name": "ywzx", "label": "业务中心", "type": "String"}, {"name": "modedatacreatedate", "label": "创建日期", "type": "String"}, {"name": "nbjjsfsd", "label": "内部机架是否锁定", "type": "String"}, {"name": "sfwc", "label": "是否完成", "type": "String"}, {"name": "ac19", "label": "A路C19", "type": "String"}, {"name": "wdslaxx", "label": "温度数量下限", "type": "String"}, {"name": "dhzt", "label": "动环状态", "type": "String"}, {"name": "modedatacreatertype", "label": "创建人类型", "type": "String"}, {"name": "bkgzt", "label": "板块更状态", "type": "String"}, {"name": "formmodeid", "label": "表单模式ID", "type": "String"}, {"name": "ac13", "label": "A路C13", "type": "String"}, {"name": "jfmc", "label": "机房名称(ID)", "type": "String"}, {"name": "sdslaxx", "label": "湿度数量下限", "type": "String"}, {"name": "col", "label": "列", "type": "String"}, {"name": "mk", "label": "模块", "type": "String"}, {"name": "ztsm", "label": "状态说明", "type": "String"}, {"name": "jjzt", "label": "机架状态", "type": "String"}, {"name": "akgzt", "label": "A路开关状态", "type": "String"}, {"name": "modeuuid", "label": "-", "type": "String"}, {"name": "jjbm", "label": "机架编码", "type": "String"}, {"name": "modedatamodifydatetime", "label": "修改时间", "type": "String"}, {"name": "sdzt", "label": "锁定状态", "type": "String"}, {"name": "jjbmyys", "label": "机架编码(运营商)", "type": "String"}, {"name": "wdslasx", "label": "温度数量上限", "type": "String"}, {"name": "bkg", "label": "B路开关", "type": "String"}, {"name": "modedatacreater", "label": "创建人", "type": "String"}, {"name": "bc13", "label": "B路C13", "type": "String"}, {"name": "requestid", "label": "请求ID", "type": "String"}, {"name": "modedatamodifier", "label": "修改人", "type": "String"}, {"name": "htbm", "label": "合同编码", "type": "String"}, {"name": "bzdl", "label": "标准电力", "type": "String"}, {"name": "sddl", "label": "锁定电力", "type": "String"}, {"name": "pdulx", "label": "PDU类型", "type": "String"}, {"name": "outkey", "label": "外部键", "type": "String"}, {"name": "zzkh", "label": "最终客户", "type": "String"}, {"name": "apdu", "label": "A路PDU", "type": "String"}, {"name": "sfzy", "label": "是否占用", "type": "String"}, {"name": "jjlx", "label": "机架类型", "type": "String"}, {"name": "khmc", "label": "客户名称", "type": "String"}, {"name": "bpdu", "label": "B路PDU", "type": "String"}, {"name": "dhztrq", "label": "动环状态日期", "type": "String"}, {"name": "xnjj", "label": "虚拟机架", "type": "String"}, {"name": "sdrq", "label": "锁定日期", "type": "String"}, {"name": "bc19", "label": "B路C19", "type": "String"}, {"name": "sdslasx", "label": "湿度数量上限", "type": "String"}, {"name": "srlx", "label": "散热类型", "type": "String"}, {"name": "lc", "label": "楼层", "type": "String"}, {"name": "modedatacreatetime", "label": "创建时间", "type": "String"}, {"name": "zzkhbm", "label": "最终客户编码", "type": "String"}, {"name": "jfbm", "label": "机房编码", "type": "String"}]',
    '[{"name": "jfmc", "label": "机房名称(ID)", "type": "String"}, {"name": "jjbm", "label": "机架编码", "type": "String"}, {"name": "jjzt", "label": "机架状态", "type": "String"}]',
    'rowkey',
    1
);

-- 5. 云枢设备点位 (Yunshu Device Points)
INSERT INTO `sys_resource_meta` (`resource_key`, `resource_name`, `resource_group`, `data_source`, `table_name`, `fields_config`, `allowed_filters`, `default_sort`, `status`) VALUES (
    'yunshu_device_points', 
    '设备点位', 
    '智服平台', 
    'default_clickhouse', 
    'ck_fact_yunshu_devicepoint_hbase', 
    '[{"name": "rowkey", "label": "行键", "type": "String"}, {"name": "id", "label": "ID", "type": "String"}, {"name": "modedatamodifier", "label": "修改人", "type": "String"}, {"name": "dwmc", "label": "点位名称", "type": "String"}, {"name": "modedatacreatetime", "label": "创建时间", "type": "String"}, {"name": "modedatacreatertype", "label": "创建人类型", "type": "String"}, {"name": "szwz", "label": "所在位置", "type": "String"}, {"name": "jf", "label": "机房(ID)", "type": "String"}, {"name": "modedatacreater", "label": "创建人", "type": "String"}, {"name": "modedatamodifydatetime", "label": "修改时间", "type": "String"}, {"name": "sztd", "label": "所在通道", "type": "String"}, {"name": "requestid", "label": "请求ID", "type": "String"}, {"name": "jc", "label": "简称", "type": "String"}, {"name": "dyztid", "label": "对应状态ID", "type": "String"}, {"name": "xgsb", "label": "相关设备", "type": "String"}, {"name": "modeuuid", "label": "-", "type": "String"}, {"name": "form_biz_id", "label": "表单业务ID", "type": "String"}, {"name": "sbjc", "label": "设备简称", "type": "String"}, {"name": "jjbm", "label": "机架编码(ID)", "type": "String"}, {"name": "dwid", "label": "点位ID(OID)", "type": "String"}, {"name": "formmodeid", "label": "表单模式ID", "type": "String"}, {"name": "szlc", "label": "所在楼层", "type": "String"}, {"name": "dwlx", "label": "点位类型", "type": "String"}, {"name": "modedatacreatedate", "label": "创建日期", "type": "String"}, {"name": "szmk", "label": "所在模块", "type": "String"}, {"name": "metric_time", "label": "指标时间", "type": "String"}, {"name": "metric_value", "label": "指标值", "type": "String"}]',
    '[{"name": "jf", "label": "机房(ID)", "type": "String"}, {"name": "jjbm", "label": "机架编码(ID)", "type": "String"}, {"name": "dwid", "label": "点位ID(OID)", "type": "String"}]',
    'rowkey',
    1
);

-- 6. CCG 资源 (CCG Resources - Placeholder)
INSERT INTO `sys_resource_meta` (`resource_key`, `resource_name`, `resource_group`, `data_source`, `table_name`, `fields_config`, `allowed_filters`, `default_sort`, `status`) VALUES (
    'ccg_resources', 
    'CCG资源', 
    'CCG数据', 
    'default_clickhouse', 
    'ck_fact_ccg_resource_hbase', 
    '[{"name": "resource_id", "label": "资源ID", "type": "String"}, {"name": "resource_name", "label": "资源名称", "type": "String"}, {"name": "resource_type", "label": "资源类型", "type": "String"}, {"name": "status", "label": "状态", "type": "String"}, {"name": "cpu_cores", "label": "CPU核心", "type": "Int32"}, {"name": "memory_gb", "label": "内存(GB)", "type": "Int32"}, {"name": "disk_gb", "label": "磁盘(GB)", "type": "Int32"}, {"name": "ip_address", "label": "IP地址", "type": "String"}]',
    '[{"name": "resource_type", "label": "资源类型", "type": "String"}, {"name": "status", "label": "状态", "type": "String"}]',
    'resource_id',
    1
);

-- 7. CCG 虚拟机 (CCG Virtual Machines - Placeholder)
INSERT INTO `sys_resource_meta` (`resource_key`, `resource_name`, `resource_group`, `data_source`, `table_name`, `fields_config`, `allowed_filters`, `default_sort`, `status`) VALUES (
    'ccg_virtual_machines', 
    'CCG虚拟机', 
    'CCG数据', 
    'default_clickhouse', 
    'ck_fact_ccg_vm_hbase', 
    '[{"name": "vm_id", "label": "虚拟机ID", "type": "String"}, {"name": "vm_name", "label": "虚拟机名称", "type": "String"}, {"name": "vm_status", "label": "状态", "type": "String"}, {"name": "vm_type", "label": "类型", "type": "String"}]',
    '[{"name": "vm_status", "label": "状态", "type": "String"}, {"name": "vm_type", "label": "类型", "type": "String"}]',
    'vm_id',
    1
);

-- 8. CCG 容器 (CCG Containers - Placeholder)
INSERT INTO `sys_resource_meta` (`resource_key`, `resource_name`, `resource_group`, `data_source`, `table_name`, `fields_config`, `allowed_filters`, `default_sort`, `status`) VALUES (
    'ccg_containers', 
    'CCG容器', 
    'CCG数据', 
    'default_clickhouse', 
    'ck_fact_ccg_container_hbase', 
    '[{"name": "container_id", "label": "容器ID", "type": "String"}, {"name": "container_name", "label": "容器名称", "type": "String"}, {"name": "namespace", "label": "命名空间", "type": "String"}, {"name": "status", "label": "状态", "type": "String"}]',
    '[{"name": "namespace", "label": "命名空间", "type": "String"}, {"name": "status", "label": "状态", "type": "String"}]',
    'container_id',
    1
);

COMMIT;

SET FOREIGN_KEY_CHECKS = 1;
