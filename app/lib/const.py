import pymongo

MONGO_METRIC_COLLECTION = "metric_data"
MONGO_ALARM_COLLECTION = "alarm_data"

MONGO_ORDER_ASC = pymongo.ASCENDING
MONGO_ORDER_DESC = pymongo.DESCENDING


class CustomerType:

    Vendor = "工程商"
    Project = "项目"
    Super = "管理方"


class DeviceStatus:

    STATUS_NORMAL = 0
    STATUS_WARN = 1
    STATUS_ALARM = 2
    STATUS_OFFLINE = 3
    STATUS_ERROR = 4


DeviceStatusCN = {
    DeviceStatus.STATUS_NORMAL: "正常",
    DeviceStatus.STATUS_WARN: "预警",
    DeviceStatus.STATUS_ALARM: "告警",
    DeviceStatus.STATUS_OFFLINE: "下线",
    DeviceStatus.STATUS_ERROR: "故障"
}


