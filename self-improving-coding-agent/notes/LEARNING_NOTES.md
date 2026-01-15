# Learning Notes

## Docker: Sibling Containers (Docker-outside-of-Docker)

### Concept
The configuration `- /var/run/docker.sock:/var/run/docker.sock` in `docker-compose.yml` implements a pattern known as **Sibling Containers** (often confused with Docker-in-Docker, but distinct).

### Mechanism
*   **Host Socket:** `/var/run/docker.sock` is the Unix socket the Docker daemon listens on.
*   **Mount:** By mounting this socket from the host into the container, the container's Docker client communicates directly with the **host's** Docker daemon.
*   **Result:** When the container runs `docker run`, it doesn't create a nested container *inside* itself. Instead, it instructs the host daemon to spawn a new container alongside itself (a "sibling").

### Use Case in this Project
*   **Sandboxing:** The Agent needs to execute untrusted code. Instead of running it locally (risky), it asks the host to spin up a temporary, isolated "Sandbox" container.
*   **Resource Management:** Since the sibling lives on the host, it's easier to manage its lifecycle and resources compared to nested containers.

### Security Implications
*   **Root Privilege:** Granting access to the Docker socket is equivalent to giving root access to the host. The container can launch privileged containers, mount any host path, and modify the host system.
*   **Trust:** This pattern assumes the "Agent" container is trusted code, even if the code it *runs* (in the sibling sandbox) is not.
