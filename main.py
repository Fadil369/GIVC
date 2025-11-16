#!/usr/bin/env python3
"""
GIVC Healthcare Platform - Unified Entry Point
Consolidates CLI and API server modes into a single entry point

Usage:
    # Start API server (default)
    python main.py

    # Start API server with specific host/port
    python main.py --mode api --host 0.0.0.0 --port 8000

    # Run CLI mode for NPHIES operations
    python main.py --mode cli --command check-status

    # Run CLI commands
    python main.py --mode cli --command submit-claim --file claim.json
    python main.py --mode cli --command check-eligibility --member-id 12345

Author: Dr. Al Fadil (BRAINSAIT LTD)
License: GPL-3.0
Version: 3.0.0
"""
import sys
import argparse
from pathlib import Path
from typing import Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))


def run_api_server(host: str = "0.0.0.0", port: int = 8000, reload: bool = False):
    """
    Run the FastAPI server

    Args:
        host: Host to bind to
        port: Port to bind to
        reload: Enable auto-reload (development mode)
    """
    import uvicorn
    from fastapi_app import app

    print(f"""
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║   🏥  GIVC Healthcare Platform API Server                           ║
║                                                                      ║
║   Starting FastAPI Backend...                                       ║
║   URL: http://{host}:{port}                                    ║
║   Docs: http://{host}:{port}/api/docs                          ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
    """)

    uvicorn.run(
        "fastapi_app:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )


def run_cli_mode(command: str, **kwargs):
    """
    Run CLI mode for NPHIES operations

    Args:
        command: CLI command to execute
        **kwargs: Additional command arguments
    """
    from main_enhanced import (
        print_enhanced_banner,
        check_enhanced_system_status,
        run_interactive_menu
    )

    print_enhanced_banner()

    if command == "check-status":
        check_enhanced_system_status()
    elif command == "interactive":
        run_interactive_menu()
    elif command == "submit-claim":
        from services.claims import ClaimsService
        claims_service = ClaimsService()
        # Implement claim submission logic
        print("Claim submission functionality")
    elif command == "check-eligibility":
        from services.eligibility import EligibilityService
        eligibility_service = EligibilityService()
        # Implement eligibility check logic
        print("Eligibility check functionality")
    else:
        print(f"Unknown command: {command}")
        print("Available commands: check-status, interactive, submit-claim, check-eligibility")
        sys.exit(1)


def main():
    """Main entry point with argument parsing"""
    parser = argparse.ArgumentParser(
        description="GIVC Healthcare Platform - Unified Entry Point",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start API server (default)
  python main.py

  # Start API server with custom settings
  python main.py --mode api --host 0.0.0.0 --port 8080 --reload

  # Check system status
  python main.py --mode cli --command check-status

  # Interactive CLI menu
  python main.py --mode cli --command interactive

  # Submit a claim
  python main.py --mode cli --command submit-claim --file claim.json

For more information, visit: https://givc.thefadil.site
        """
    )

    parser.add_argument(
        "--mode",
        choices=["api", "cli"],
        default="api",
        help="Execution mode: 'api' for server, 'cli' for command-line operations (default: api)"
    )

    # API mode arguments
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="API server host (default: 0.0.0.0)"
    )

    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="API server port (default: 8000)"
    )

    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload for development (API mode only)"
    )

    # CLI mode arguments
    parser.add_argument(
        "--command",
        help="CLI command to execute (required for CLI mode)"
    )

    parser.add_argument(
        "--file",
        help="Input file path for CLI commands"
    )

    parser.add_argument(
        "--member-id",
        help="Member ID for eligibility checks"
    )

    parser.add_argument(
        "--output",
        help="Output file path for results"
    )

    args = parser.parse_args()

    # Execute based on mode
    if args.mode == "api":
        run_api_server(
            host=args.host,
            port=args.port,
            reload=args.reload
        )
    elif args.mode == "cli":
        if not args.command:
            parser.error("--command is required for CLI mode")

        run_cli_mode(
            command=args.command,
            file=args.file,
            member_id=args.member_id,
            output=args.output
        )
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down gracefully...")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
