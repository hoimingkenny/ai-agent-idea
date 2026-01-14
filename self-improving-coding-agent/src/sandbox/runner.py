import docker
from typing import Dict, Optional
import logging
import subprocess
import sys
import tempfile
import os

logger = logging.getLogger(__name__)

class Sandbox:
    """
    Executes code in a secure Docker container, with fallback to local execution.
    """
    def __init__(self, image: str = "python:3.10-slim", timeout: int = 10):
        self.image = image
        self.timeout = timeout
        self.use_docker = False
        try:
            self.client = docker.from_env()
            # Test connection
            self.client.ping()
            self.use_docker = True
        except Exception as e:
            logger.warning(f"Docker is not available: {e}. Switching to LOCAL execution fallback.")
            self.client = None

    def run(self, code: str) -> Dict[str, str]:
        """
        Runs the provided Python code.
        Returns a dict with 'output' and 'error'.
        """
        if self.use_docker and self.client:
            return self._run_docker(code)
        else:
            return self._run_local(code)

    def _run_docker(self, code: str) -> Dict[str, str]:
        container = None
        try:
            container = self.client.containers.run(
                self.image,
                command=["python", "-c", code],
                mem_limit="128m",
                pids_limit=20,
                network_disabled=True,
                detach=True,
            )
            
            result = container.wait(timeout=self.timeout)
            logs = container.logs(stdout=True, stderr=True).decode("utf-8")
            exit_code = result.get('StatusCode', 1)
            
            if exit_code == 0:
                return {"output": logs.strip(), "error": ""}
            else:
                return {"output": "", "error": logs.strip()}

        except Exception as e:
            return {"output": "", "error": f"Docker execution failed: {str(e)}"}
        finally:
            if container:
                try:
                    container.remove(force=True)
                except Exception:
                    pass

    def _run_local(self, code: str) -> Dict[str, str]:
        """
        Fallback for local execution. WARNING: NOT SANDBOXED.
        """
        print("⚠️  Running locally (Docker unavailable).")
        try:
            # Create a temp file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as tmp:
                tmp.write(code)
                tmp_path = tmp.name
            
            # Run with subprocess
            result = subprocess.run(
                [sys.executable, tmp_path],
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            # Clean up
            os.remove(tmp_path)
            
            if result.returncode == 0:
                return {"output": result.stdout.strip(), "error": ""}
            else:
                return {"output": result.stdout.strip(), "error": result.stderr.strip()}
                
        except subprocess.TimeoutExpired:
            return {"output": "", "error": "Execution timed out."}
        except Exception as e:
            return {"output": "", "error": f"Local execution failed: {str(e)}"}
