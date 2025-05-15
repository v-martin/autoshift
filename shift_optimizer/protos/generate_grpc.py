import os
import sys
import grpc_tools.protoc as protoc
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
def generate_grpc():
    try:
        proto_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(proto_dir)
        python_out = root_dir
        grpc_python_out = root_dir
        proto_file = "shift_optimizer.proto"
        proto_path = os.path.join(proto_dir, proto_file)
        if not os.path.exists(proto_path):
            logger.error(f"Proto file not found: {proto_path}")
            return False
        logger.info(f"Generating gRPC files from {proto_path}")
        logger.info(f"Output directory: {root_dir}")
        result = protoc.main([
            'grpc_tools.protoc',
            f'--proto_path={proto_dir}',
            f'--python_out={python_out}',
            f'--grpc_python_out={grpc_python_out}',
            proto_path
        ])
        if result != 0:
            logger.error(f"Failed to generate gRPC files. Exit code: {result}")
            return False
        expected_files = [
            os.path.join(root_dir, f"shift_optimizer_pb2.py"),
            os.path.join(root_dir, f"shift_optimizer_pb2_grpc.py")
        ]
        for file_path in expected_files:
            if not os.path.exists(file_path):
                logger.error(f"Expected output file not found: {file_path}")
                return False
            else:
                logger.info(f"Generated file: {file_path}")
        logger.info("gRPC generation completed successfully")
        return True
    except Exception as e:
        logger.error(f"Error generating gRPC files: {str(e)}", exc_info=True)
        return False
if __name__ == "__main__":
    success = generate_grpc()
    sys.exit(0 if success else 1)