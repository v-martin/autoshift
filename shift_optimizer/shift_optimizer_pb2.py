# -*- coding: utf-8 -*-
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    29,
    0,
    '',
    'shift_optimizer.proto'
)
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x15shift_optimizer.proto\x12\x0fshift_optimizer\"\xa5\x01\n\x06Worker\x12\x0c\n\x04uuid\x18\x01 \x01(\t\x12\x10\n\x08username\x18\x02 \x01(\t\x12\x36\n\x0equalifications\x18\x03 \x03(\x0b\x32\x1e.shift_optimizer.Qualification\x12\x43\n\x15warehouse_preferences\x18\x04 \x03(\x0b\x32$.shift_optimizer.WarehousePreference\"P\n\rQualification\x12\x30\n\x04type\x18\x01 \x01(\x0e\x32\".shift_optimizer.QualificationType\x12\r\n\x05level\x18\x02 \x01(\x05\"Q\n\x13WarehousePreference\x12\x16\n\x0ewarehouse_uuid\x18\x01 \x01(\t\x12\x10\n\x08priority\x18\x02 \x01(\x05\x12\x10\n\x08\x64istance\x18\x03 \x01(\x02\"\xa8\x01\n\tWarehouse\x12\x0c\n\x04uuid\x18\x01 \x01(\t\x12\x0c\n\x04name\x18\x02 \x01(\t\x12\x10\n\x08\x63\x61pacity\x18\x03 \x01(\x05\x12\x13\n\x0bmin_workers\x18\x04 \x01(\x05\x12\x19\n\x11min_basic_workers\x18\x05 \x01(\x05\x12\x13\n\x0bmin_drivers\x18\x06 \x01(\x05\x12\x15\n\rmin_engineers\x18\x07 \x01(\x05\x12\x11\n\tis_active\x18\x08 \x01(\x08\"G\n\tCargoLoad\x12\x16\n\x0ewarehouse_uuid\x18\x01 \x01(\t\x12\x0c\n\x04\x64\x61te\x18\x02 \x01(\t\x12\x14\n\x0ctotal_weight\x18\x03 \x01(\x05\"\xb0\x01\n\x15OptimizeShiftsRequest\x12(\n\x07workers\x18\x01 \x03(\x0b\x32\x17.shift_optimizer.Worker\x12.\n\nwarehouses\x18\x02 \x03(\x0b\x32\x1a.shift_optimizer.Warehouse\x12/\n\x0b\x63\x61rgo_loads\x18\x03 \x03(\x0b\x32\x1a.shift_optimizer.CargoLoad\x12\x0c\n\x04\x64\x61ys\x18\x04 \x03(\t\"x\n\x0eScheduledShift\x12\x13\n\x0bworker_uuid\x18\x01 \x01(\t\x12\x16\n\x0ewarehouse_uuid\x18\x02 \x01(\t\x12\x13\n\x0b\x64\x61y_of_week\x18\x03 \x01(\t\x12\x12\n\nstart_time\x18\x04 \x01(\t\x12\x10\n\x08\x65nd_time\x18\x05 \x01(\t\"\xab\x01\n\x16OptimizeShiftsResponse\x12/\n\x06shifts\x18\x01 \x03(\x0b\x32\x1f.shift_optimizer.ScheduledShift\x12>\n\x12warehouse_staffing\x18\x02 \x03(\x0b\x32\".shift_optimizer.WarehouseStaffing\x12\x0f\n\x07success\x18\x03 \x01(\x08\x12\x0f\n\x07message\x18\x04 \x01(\t\"\x99\x02\n\x11WarehouseStaffing\x12\x16\n\x0ewarehouse_uuid\x18\x01 \x01(\t\x12\x16\n\x0ewarehouse_name\x18\x02 \x01(\t\x12\x0b\n\x03\x64\x61y\x18\x03 \x01(\t\x12\x1e\n\x16required_basic_workers\x18\x04 \x01(\x05\x12\x1f\n\x17scheduled_basic_workers\x18\x05 \x01(\x05\x12\x18\n\x10required_drivers\x18\x06 \x01(\x05\x12\x19\n\x11scheduled_drivers\x18\x07 \x01(\x05\x12\x1a\n\x12required_engineers\x18\x08 \x01(\x05\x12\x1b\n\x13scheduled_engineers\x18\t \x01(\x05\x12\x18\n\x10is_fully_staffed\x18\n \x01(\x08*E\n\x11QualificationType\x12\x10\n\x0c\x42\x41SIC_WORKER\x10\x00\x12\x10\n\x0c\x43\x41RGO_DRIVER\x10\x01\x12\x0c\n\x08\x45NGINEER\x10\x02\x32|\n\x15ShiftOptimizerService\x12\x63\n\x0eOptimizeShifts\x12&.shift_optimizer.OptimizeShiftsRequest\x1a\'.shift_optimizer.OptimizeShiftsResponse\"\x00\x62\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'shift_optimizer_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_QUALIFICATIONTYPE']._serialized_start=1378
  _globals['_QUALIFICATIONTYPE']._serialized_end=1447
  _globals['_WORKER']._serialized_start=43
  _globals['_WORKER']._serialized_end=208
  _globals['_QUALIFICATION']._serialized_start=210
  _globals['_QUALIFICATION']._serialized_end=290
  _globals['_WAREHOUSEPREFERENCE']._serialized_start=292
  _globals['_WAREHOUSEPREFERENCE']._serialized_end=373
  _globals['_WAREHOUSE']._serialized_start=376
  _globals['_WAREHOUSE']._serialized_end=544
  _globals['_CARGOLOAD']._serialized_start=546
  _globals['_CARGOLOAD']._serialized_end=617
  _globals['_OPTIMIZESHIFTSREQUEST']._serialized_start=620
  _globals['_OPTIMIZESHIFTSREQUEST']._serialized_end=796
  _globals['_SCHEDULEDSHIFT']._serialized_start=798
  _globals['_SCHEDULEDSHIFT']._serialized_end=918
  _globals['_OPTIMIZESHIFTSRESPONSE']._serialized_start=921
  _globals['_OPTIMIZESHIFTSRESPONSE']._serialized_end=1092
  _globals['_WAREHOUSESTAFFING']._serialized_start=1095
  _globals['_WAREHOUSESTAFFING']._serialized_end=1376
  _globals['_SHIFTOPTIMIZERSERVICE']._serialized_start=1449
  _globals['_SHIFTOPTIMIZERSERVICE']._serialized_end=1573