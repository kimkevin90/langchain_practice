import sqlite3
from pydantic import BaseModel
from typing import List
from langchain.tools import Tool

conn = sqlite3.connect("db.sqlite")


def list_tables():
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table';")
    rows = c.fetchall()
    return "\n".join(row[0] for row in rows if row[0] is not None)


def run_sqlite_query(query):
    c = conn.cursor()
    try:
        c.execute(query)
        return c.fetchall()
    # 에러 처리시 chatGpt는 해당 에러를 확인
    except sqlite3.OperationalError as err:
        return f"The following error occured: {str(err)}"

# BaseModel을 활용하여 tool에 대한 좀더 정확한 정보 제공
class RunQueryArgsSchema(BaseModel):
    query: str

# Tool 클래스는 특정 작업을 수행하는 함수를 캡슐화합니다. 이를 통해 에이전트가 다양한 작업을 수행할 수 있게 해줍니다.
run_query_tool = Tool.from_function(
    name="run_sqlite_query",
    description="Run a sqlite query.",
    func=run_sqlite_query,
    args_schema=RunQueryArgsSchema
)

def describe_tables(table_names):
    c = conn.cursor()
    tables = ', '.join("'" + table + "'" for table in table_names)
    rows = c.execute(f"SELECT sql FROM sqlite_master WHERE type='table' and name IN ({tables});")
    return '\n'.join(row[0] for row in rows if row[0] is not None)


class DescribeTablesArgsSchema(BaseModel):
    tables_names: List[str]


describe_tables_tool = Tool.from_function(
    name="describe_tables",
    description="Given a list of table names, returns the schema of those tables",
    func=describe_tables,
    args_schema=DescribeTablesArgsSchema
)
