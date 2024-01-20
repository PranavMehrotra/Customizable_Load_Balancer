# Assignment-1 Distributed Systems
This repository contains the code for the Assignment-1 of Distributed Systems(CS60002) course of Spring, 2024.


# Table of Contents

- [Prerequisites](#prerequisites)
- [Getting Started](#getting-started)
  - [Building Docker Images](#building-docker-images)
  - [Running Docker Containers](#running-docker-containers)
- [Troubleshooting](#troubleshooting)
  - [Docker Exit with Code 137](#docker-exit-with-code-137-ram-memory-issue)
  - [Removing Docker Containers](#removing-docker-containers)
- [Group_details](#Group_details)

<a name="prerequisites"></a>
# Prerequisite

### 1. Docker: latest

    sudo apt-get update

    sudo apt-get install \
        ca-certificates \
        curl \
        gnupg \
        lsb-release

    sudo mkdir -p /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

    echo \
    "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
    $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

    sudo apt-get update

    sudo apt-get install docker-ce docker-ce-cli containerd.io

### 2. Docker-compose standalone 
    sudo curl -SL https://github.com/docker/compose/releases/download/v2.15.1/docker-compose-linux-x86_64 -o /usr/local/bin/docker-compose
    
    sudo chmod +x /usr/local/bin/docker-compose
    
    sudo ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose

<a name="getting-started"></a>
# Getting Started

### To run load balancer and server docker containers:

```
  docker-compose build
  docker-compose up
```

<a name="troubleshooting"></a>
# Troubleshooting

### 1. Docker Exit with Code 137
code 137 indicated RAM memory related issue. Stop and remove already runining container to free up space.

### 2. Removing Docker Containers

#### 1. Stop docker container
```
Particular container: docker stop container_id
Stop all runing container: docker stop $(docker ps -a -q)
```

#### 2. remove docker container
```
Particular container: docker rm container_id
Stop all runing container: docker rm $(docker ps -a -q)
```




<a name="Group_details"></a>
# Group Information
1. Pranav Mehrotra (20CS10085)
2. Saransh Sharma (20CS30065)
3. Pranav Nyati (20CS30037)
4. Shreyas Jena (20CS30049)
