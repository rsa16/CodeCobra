"""
Database helper functions
"""

import sqlite3
from sqlite3 import Connection, Cursor
import os
from typing import Any


def loadDatabase() -> Connection:
    """
    Will automatically create database if doesn't exist, otherwise will load it (connect). Afterwards it'll return the connection
    """
    con = sqlite3.connect("giveaways.db", detect_types=sqlite3.PARSE_DECLTYPES)
    return con

# helper func
def getCursor(con: Connection) -> Cursor:
    return con.cursor()

def getTables(con: Connection):
    cur = getCursor(con)
    res = cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    return res.fetchall()

def tableExists(tableName: str, con: Connection):
    cur = getCursor(con)
    print("bob")
    res = cur.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{tableName}'")
    print("fetchall", res.fetchall())
    return res.fetchall() != []

def updateRow(tableName: str, uuid: str, data: dict, con: Connection):
    cur = getCursor(con)
    thingsToChange = ', '.join([name+'='+str(value) if type(value) is int else name+'='+f"'{value}'" for name, value in data.items()])
    print(thingsToChange)
    cur.execute(f"UPDATE {tableName} SET {thingsToChange} WHERE uuid='{uuid}'")
    con.commit()

def updateDb(db: dict[str, list[dict[str, list]]], con: Connection):
    """
    Returns -1 if table is not valid (has to be in a certain format to be written, because well... obviously)
    You are required 
    """
    # table name is table[0], table is table[1]
    cur = getCursor(con)
    print("hiii")
    for tableName, tables in db.items():
        print("looping through tabkes")
        for table in tables:
            # check if table exists so we dont create unnecessary vars
            print("exists", tableExists(tableName, con))
            if not (tableExists(tableName, con)):
                columnNames = []
                print("creating column types")
                types = []
                for columnName, tableVal in table.items():
                    types.append(tableVal[1])
                    columnNames.append(columnName)

                print("stuff")
                # not sure if we need uppercase, will leave it in case
                print("column names", list(zip(columnNames, types)))
                columnNames = ', '.join([value+' '+type.upper() for value, type in zip(columnNames, types)]) 
                cur.execute(f"CREATE TABLE IF NOT EXISTS {tableName} ({columnNames})")
                print("ew")
                con.commit()

            # theres a more efficient way to do this but this is easier to understand so i went with it
            columns = list(table.keys())
            rows =  [item[0] for item in list(table.values())] 
            if len(columns) == len(rows):
                data = list(zip(columns, rows))
                print(tuple(rows))
                questionFields = ','.join(['?' for i in range(len(columns))])
                print(questionFields)
                cur.execute(f"INSERT OR REPLACE INTO {tableName} VALUES({questionFields})", tuple(rows))
            else:
                print("death")
                return -1

            # commit everything to database
            con.commit()

def getColumn(tableName:str, columnName: str, con: Connection) -> list[Any]:
    cur = getCursor(con)
    try:
        res = cur.execute(f"SELECT {columnName} FROM {tableName}")
        return [item[0] for item in res.fetchall()]
    except:
        return []

def getRow(tableName: str, uuid: str, con: Connection) -> dict[Any, Any]:
    cur = getCursor(con)
    res = cur.execute(f"SELECT * FROM {tableName} WHERE uuid='{uuid}'")
    return dict(zip(getColNames(tableName, con), res.fetchone()))

def getColNames(tableName: str, con:Connection):
    cur = getCursor(con)
    res = cur.execute(f"PRAGMA table_info({tableName})")
    return [param[1] for param in res.fetchall()] 




