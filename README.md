
Code for blog at > [How to Use AI to 10x Data Pipeline Dev Speed](https://www.startdataengineering.com/post/build-data-pipelines-with-ai/)

## Setup 

**Prerequisites**

1. [git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
2. [Docker](https://docs.docker.com/engine/install/) and [Docker Compose](https://docs.docker.com/compose/install/)
3. [OpenCode Zen](https://opencode.ai/auth)

**Windows users**: Please use WSL and Install Ubuntu using this [document](https://documentation.ubuntu.com/wsl/stable/howto/install-ubuntu-wsl2/#). In your ubuntu terminal install the prerequisites above.

If you already use an LLM provider, see how to use that with [pi agent](https://pi.dev/docs/latest/providers).

Clone the repo & start the containers as shown below.

```bash 
git clone https://github.com/josephmachado/building-data-pipelines-with-ai.git
cd building-data-pipelines-with-ai
cp .env.template .env
# update the env file with your Opencode API key or use an existing LLM API key env variable from https://pi.dev/docs/latest/providers
```

## Run Code

Open the repo in VSCode, press `Ctrl + Shift + P` and select `Dev Containers: Rebuild and Reopen in Container`.

First time can take about 10 minutes or more.

Follow the steps at [workshop.md](./notebooks/workshop.md) to generate code with LLMs.