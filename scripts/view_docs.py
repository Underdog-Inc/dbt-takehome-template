#!/usr/bin/env python3
"""
Script to download and view dbt docs from GitHub Actions artifacts.

Usage:
    python scripts/view_docs.py <pr_number>
    python scripts/view_docs.py <workflow_run_id> --run-id

Requirements:
    - GitHub CLI (gh) installed and authenticated
    - Python 3.7+

Examples:
    # View docs from a PR (uses the latest workflow run)
    python scripts/view_docs.py 2

    # View docs from a specific workflow run ID
    python scripts/view_docs.py 1234567890 --run-id
"""

import argparse
import os
import subprocess
import sys
import tempfile
import time
import webbrowser
from pathlib import Path
from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer
import zipfile
import shutil


def check_gh_cli():
    """Check if GitHub CLI is installed and authenticated."""
    try:
        subprocess.run(
            ["gh", "auth", "status"],
            check=True,
            capture_output=True,
            text=True
        )
        return True
    except subprocess.CalledProcessError:
        print("❌ GitHub CLI is not authenticated. Please run: gh auth login")
        return False
    except FileNotFoundError:
        print("❌ GitHub CLI (gh) is not installed.")
        print("Install it from: https://cli.github.com/")
        return False


def get_latest_workflow_run_for_pr(pr_number):
    """Get the latest workflow run ID for a PR."""
    try:
        result = subprocess.run(
            [
                "gh", "run", "list",
                "--json", "databaseId,event,headBranch,status,conclusion",
                "--limit", "50"
            ],
            check=True,
            capture_output=True,
            text=True
        )
        
        import json
        runs = json.loads(result.stdout)
        
        # Get the PR details to find the branch
        pr_result = subprocess.run(
            ["gh", "pr", "view", str(pr_number), "--json", "headRefName"],
            check=True,
            capture_output=True,
            text=True
        )
        pr_data = json.loads(pr_result.stdout)
        branch_name = pr_data["headRefName"]
        
        # Find the latest completed run for this PR's branch
        for run in runs:
            if (run.get("headBranch") == branch_name and 
                run.get("status") == "completed"):
                return run["databaseId"]
        
        print(f"❌ No completed workflow runs found for PR #{pr_number}")
        return None
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error getting workflow run: {e.stderr}")
        return None
    except json.JSONDecodeError:
        print("❌ Error parsing GitHub CLI output")
        return None


def download_artifact(run_id, artifact_name="dbt-target"):
    """Download artifact from a workflow run."""
    temp_dir = tempfile.mkdtemp(prefix="dbt-docs-")
    artifact_path = os.path.join(temp_dir, f"{artifact_name}.zip")
    
    print(f"📥 Downloading artifact '{artifact_name}' from run {run_id}...")
    
    try:
        # Download the artifact
        result = subprocess.run(
            [
                "gh", "run", "download", str(run_id),
                "--name", artifact_name,
                "--dir", temp_dir
            ],
            check=True,
            capture_output=True,
            text=True
        )
        
        print(f"✅ Artifact downloaded to: {temp_dir}")
        return temp_dir
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error downloading artifact: {e.stderr}")
        shutil.rmtree(temp_dir, ignore_errors=True)
        return None


def start_server(directory, port=8080):
    """Start a simple HTTP server to serve the docs."""
    os.chdir(directory)
    
    class QuietHandler(SimpleHTTPRequestHandler):
        def log_message(self, format, *args):
            # Only log errors
            if args[1][0] != '2':
                super().log_message(format, *args)
    
    try:
        with TCPServer(("", port), QuietHandler) as httpd:
            url = f"http://localhost:{port}/index.html"
            print(f"\n✅ Serving dbt docs at: {url}")
            print("📖 Opening in your default browser...")
            print("\n💡 Press Ctrl+C to stop the server\n")
            
            # Open browser after a short delay
            time.sleep(1)
            webbrowser.open(url)
            
            # Serve forever
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down server...")
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"\n❌ Port {port} is already in use.")
            print(f"💡 Try a different port: python {sys.argv[0]} --port 8081")
        else:
            print(f"\n❌ Error starting server: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Download and view dbt docs from GitHub Actions artifacts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # View docs from PR #2
  python scripts/view_docs.py 2

  # View docs from a specific workflow run
  python scripts/view_docs.py 1234567890 --run-id

  # Use a different port
  python scripts/view_docs.py 2 --port 8081
        """
    )
    
    parser.add_argument(
        "identifier",
        type=int,
        help="PR number or workflow run ID"
    )
    parser.add_argument(
        "--run-id",
        action="store_true",
        help="Treat identifier as a workflow run ID instead of PR number"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Port for the HTTP server (default: 8080)"
    )
    parser.add_argument(
        "--artifact",
        default="dbt-target",
        help="Name of the artifact to download (default: dbt-target)"
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Don't automatically open browser"
    )
    
    args = parser.parse_args()
    
    # Check prerequisites
    if not check_gh_cli():
        sys.exit(1)
    
    # Get workflow run ID
    if args.run_id:
        run_id = args.identifier
        print(f"📋 Using workflow run ID: {run_id}")
    else:
        pr_number = args.identifier
        print(f"📋 Looking up latest workflow run for PR #{pr_number}...")
        run_id = get_latest_workflow_run_for_pr(pr_number)
        if not run_id:
            sys.exit(1)
        print(f"✅ Found workflow run: {run_id}")
    
    # Download artifact
    docs_dir = download_artifact(run_id, args.artifact)
    if not docs_dir:
        sys.exit(1)
    
    # Check if index.html exists
    index_path = os.path.join(docs_dir, "index.html")
    if not os.path.exists(index_path):
        print(f"❌ index.html not found in artifact")
        print(f"📁 Contents of {docs_dir}:")
        for item in os.listdir(docs_dir):
            print(f"  - {item}")
        shutil.rmtree(docs_dir, ignore_errors=True)
        sys.exit(1)
    
    # Start server
    try:
        if args.no_browser:
            print(f"\n✅ Docs ready at: {docs_dir}")
            print(f"💡 Start server with: python3 -m http.server {args.port}")
        else:
            start_server(docs_dir, args.port)
    finally:
        # Cleanup
        print(f"\n🧹 Cleaning up temporary files...")
        shutil.rmtree(docs_dir, ignore_errors=True)


if __name__ == "__main__":
    main()
