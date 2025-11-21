"""
AgentBeats Integration Runner
Connects PersonaGym Green Agent to AgentBeats platform using A2A protocol
"""

import os
import sys
import argparse
from pathlib import Path

# Handle different toml libraries
try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:
    try:
        import tomli as tomllib  # Python < 3.11
    except ModuleNotFoundError:
        print("ERROR: TOML library not found. Installing...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "tomli"])
        import tomli as tomllib


def load_agent_card(card_path: str) -> dict:
    """Load agent card configuration."""
    with open(card_path, 'rb') as f:
        return tomllib.load(f)


def run_with_agentbeats(args):
    """
    Run the green agent using AgentBeats SDK.
    This integrates with the AgentBeats platform for standardized evaluation.
    """
    import subprocess
    
    # Build agentbeats run command
    cmd = [
        "agentbeats", "run",
        args.agent_card,
        "--launcher_host", args.launcher_host,
        "--launcher_port", str(args.launcher_port),
        "--agent_host", args.agent_host,
        "--agent_port", str(args.agent_port),
        "--model_type", args.model_type,
        "--model_name", args.model_name
    ]
    
    print(f"Starting AgentBeats green agent...")
    print(f"Command: {' '.join(cmd)}")
    print(f"\nAgent URL: http://{args.agent_host}:{args.agent_port}")
    print(f"Launcher URL: http://{args.launcher_host}:{args.launcher_port}")
    print("\n" + "="*60)
    print("Register your agent at: https://agentbeats.org")
    print("="*60 + "\n")
    
    # Run the agent
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running agent: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nShutting down agent...")
        sys.exit(0)


def setup_environment():
    """Setup and validate environment variables."""
    required_vars = {
        "OPENAI_API_KEY": "OpenAI API key for GPT-4o evaluation",
        "ANTHROPIC_API_KEY": "Anthropic API key for Claude evaluation (optional)"
    }
    
    missing = []
    for var, description in required_vars.items():
        if not os.getenv(var):
            if var != "ANTHROPIC_API_KEY":  # Claude is optional
                missing.append(f"{var} ({description})")
    
    if missing:
        print("ERROR: Missing required environment variables:")
        for var in missing:
            print(f"  - {var}")
        print("\nSet them with:")
        print("  export OPENAI_API_KEY='your-key'  # Linux/Mac")
        print("  $env:OPENAI_API_KEY='your-key'    # Windows PowerShell")
        sys.exit(1)
    
    print("✓ Environment variables validated")


def main():
    parser = argparse.ArgumentParser(
        description="Run PersonaGym Green Agent with AgentBeats"
    )
    
    parser.add_argument(
        "agent_card",
        help="Path to agent card TOML file"
    )
    
    parser.add_argument(
        "--launcher_host",
        required=True,
        help="Public IP for launcher (receives reset signals)"
    )
    
    parser.add_argument(
        "--launcher_port",
        type=int,
        default=8002,
        help="Port for launcher (default: 8002)"
    )
    
    parser.add_argument(
        "--agent_host",
        required=True,
        help="Public IP for agent (A2A communication)"
    )
    
    parser.add_argument(
        "--agent_port",
        type=int,
        default=8001,
        help="Port for agent (default: 8001)"
    )
    
    parser.add_argument(
        "--model_type",
        default="openai",
        choices=["openai", "anthropic"],
        help="LLM provider for agent (default: openai)"
    )
    
    parser.add_argument(
        "--model_name",
        default="gpt-4o",
        help="Model name (default: gpt-4o)"
    )
    
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Only validate setup, don't run agent"
    )
    
    args = parser.parse_args()
    
    # Validate environment
    setup_environment()
    
    # Validate agent card exists
    if not Path(args.agent_card).exists():
        print(f"ERROR: Agent card not found: {args.agent_card}")
        sys.exit(1)
    
    # Load and validate agent card
    try:
        card = load_agent_card(args.agent_card)
        print(f"✓ Loaded agent card: {card['agent']['name']}")
        print(f"  Version: {card['agent']['version']}")
        print(f"  Type: {card['agent']['type']}")
    except Exception as e:
        print(f"ERROR: Failed to load agent card: {e}")
        sys.exit(1)
    
    if args.validate_only:
        print("\n✓ Validation successful!")
        print("\nTo run the agent, remove --validate-only flag")
        return
    
    # Run with AgentBeats
    run_with_agentbeats(args)


if __name__ == "__main__":
    main()