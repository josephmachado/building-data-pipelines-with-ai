## Create Data 

Open a terminal in this directory.

Create data and tables as shown below.

```bash
cd notebooks
uv run python ./generate_data.py 
uv run python ./run_ddl.py
```

## Run Pipeline

Run the pipeline that generates the table `fct_orders` using the command below.

```bash
uv run python ./fct_orders.py --start-time 1995-01-01 --end-time 1996-01-01
```

## Code Generation with LLM

Open pi agent and use the skill `design-pipeline-no-mcp` as shown below.

```bash
pi 
# trust the folder
# Since you have set connection env variable at .env file, pi agent will use that
/skill:design-pipeline-no-mcp
# copy paste the prompt at `./prompt.txt`
# exit with Ctrl + C
```

Run the pipeline, it will fail due to memory issues.

```bash 
uv run python ./fct_lineitem.py --start-time 1995-01-01 --end-time 1996-01-01
```

## Code Generation with LLM enabled by MCP

Open pi agent and use the skill `design-pipeline`.

Let's start our `iceberg-mcp` MCP and then use this skill to enable LLMs to leverage the MCP server to make better design decision.

```bash 
rm fct_lineitem.py
pi
/mcp:start iceberg-mcp 
# wait a few minutes
/skill:design-pipeline
# copy paste the prompt at `./prompt.txt`
# exit with Ctrl + C
```


Run the pipeline, it will pass, as the MCP info would enable LLM to design the pipeline appropriately.

```bash 
uv run python ./silver_fct_lineitem.py --start-time 1995-01-01 --end-time 1996-01-01
```