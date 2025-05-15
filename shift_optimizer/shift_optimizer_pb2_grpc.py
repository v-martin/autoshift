import grpc
import warnings
import shift_optimizer_pb2 as shift__optimizer__pb2
GRPC_GENERATED_VERSION = '1.71.0'
GRPC_VERSION = grpc.__version__
_version_not_supported = False
try:
    from grpc._utilities import first_version_is_lower
    _version_not_supported = first_version_is_lower(GRPC_VERSION, GRPC_GENERATED_VERSION)
except ImportError:
    _version_not_supported = True
if _version_not_supported:
    raise RuntimeError(
        f'The grpc package installed is at version {GRPC_VERSION},'
        + f' but the generated code in shift_optimizer_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
    )
class ShiftOptimizerServiceStub(object):
    
    def __init__(self, channel):
        
        self.OptimizeShifts = channel.unary_unary(
                '/shift_optimizer.ShiftOptimizerService/OptimizeShifts',
                request_serializer=shift__optimizer__pb2.OptimizeShiftsRequest.SerializeToString,
                response_deserializer=shift__optimizer__pb2.OptimizeShiftsResponse.FromString,
                _registered_method=True)
class ShiftOptimizerServiceServicer(object):
    
    def OptimizeShifts(self, request, context):
        
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')
def add_ShiftOptimizerServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'OptimizeShifts': grpc.unary_unary_rpc_method_handler(
                    servicer.OptimizeShifts,
                    request_deserializer=shift__optimizer__pb2.OptimizeShiftsRequest.FromString,
                    response_serializer=shift__optimizer__pb2.OptimizeShiftsResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'shift_optimizer.ShiftOptimizerService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('shift_optimizer.ShiftOptimizerService', rpc_method_handlers)
class ShiftOptimizerService(object):
    
    @staticmethod
    def OptimizeShifts(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/shift_optimizer.ShiftOptimizerService/OptimizeShifts',
            shift__optimizer__pb2.OptimizeShiftsRequest.SerializeToString,
            shift__optimizer__pb2.OptimizeShiftsResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)