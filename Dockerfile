# Development Dockerfile for devcontainer
FROM mcr.microsoft.com/vscode/devcontainers/python:3.9

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    curl \
    git \
    vim \
    htop \
    tree \
    && rm -rf /var/lib/apt/lists/*

# Install Python development tools
RUN pip install --upgrade pip \
    && pip install \
        black \
        flake8 \
        pylint \
        pytest \
        pytest-cov \
        jupyter \
        ipython \
        ruff

# Set working directory
WORKDIR /workspaces/personal-codex-agent

# Copy requirements first for better caching
COPY requirements.txt .

# Install project dependencies
RUN pip install -r requirements.txt

# Create a setup.py for editable install
COPY setup.py .

# Install project in editable mode
RUN pip install -e .

# Expose Streamlit port
EXPOSE 8501

# Set up git safe directory
RUN git config --global --add safe.directory /workspaces/personal-codex-agent

# Create non-root user
RUN useradd -m -s /bin/bash vscode \
    && usermod -aG sudo vscode \
    && echo 'vscode ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

USER vscode