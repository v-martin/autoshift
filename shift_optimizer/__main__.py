#!/usr/bin/env python
import os
import sys
import argparse
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
def parse_args():
    parser = argparse.ArgumentParser(description='Shift Optimizer CLI')
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    server_parser = subparsers.add_parser('server', help='Start the gRPC server')
    server_parser.add_argument('--port', type=int, default=50051, help='Port number (default: 50051)')
    server_parser.add_argument('--host', type=str, default='[::]', help='Host address (default: [::])')
    
    generate_parser = subparsers.add_parser('generate', help='Generate gRPC files from proto')
    
    help_parser = subparsers.add_parser('help', help='Show help')
    
    return parser.parse_args()
def main():
    args = parse_args()
    
    if args.command == 'server':
        logger.info(f"Starting gRPC server on {args.host}:{args.port}")
        try:
            from shift_optimizer.server.server import serve
            serve(port=args.port)
        except ImportError:
            logger.error("Failed to import server module. Make sure gRPC files are generated.")
            print("Error: Failed to import server module. Run 'python -m shift_optimizer generate' first.")
            sys.exit(1)
    
    elif args.command == 'generate':
        logger.info("Generating gRPC files from proto")
        try:
            from shift_optimizer.protos.generate_grpc import generate_grpc
            success = generate_grpc()
            if success:
                logger.info("Successfully generated gRPC files")
                print("gRPC files successfully generated!")
            else:
                logger.error("Failed to generate gRPC files")
                print("Error: Failed to generate gRPC files. Check logs for details.")
                sys.exit(1)
        except ImportError:
            logger.error("Failed to import generate_grpc module")
            print("Error: Failed to import generate_grpc module. Make sure the package is installed correctly.")
            sys.exit(1)
    
    elif args.command == 'help' or args.command is None:
        print("Shift Optimizer CLI")
        print("\nUsage:")
        print("  python -m shift_optimizer <command> [options]")
        print("\nCommands:")
        print("  server    Start the gRPC server")
        print("  generate  Generate gRPC files from proto")
        print("  help      Show this help message")
        print("\nFor command-specific help, use: python -m shift_optimizer <command> --help")
    
    else:
        print(f"Unknown command: {args.command}")
        print("Use 'python -m shift_optimizer help' for usage information.")
        sys.exit(1)
if __name__ == "__main__":
    main()
