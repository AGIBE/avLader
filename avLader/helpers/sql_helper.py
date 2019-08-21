# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import cx_Oracle
import psycopg2
import sys

def readSQL(connection_string, sql_statement):
    with cx_Oracle.connect(connection_string) as conn:
        cur = conn.cursor()
        cur.execute(sql_statement)
        result_list = cur.fetchall()
    
    return result_list

def writeSQL(connection_string, sql_statement):
    with cx_Oracle.connect(connection_string) as conn:
        cur = conn.cursor()
        cur.execute(sql_statement)
        
def readSQL_PG(logger, conn_string, sql_query, fetch=False, fetchall=False):
    try:
        conn = psycopg2.connect(conn_string)
        cursor = conn.cursor()
    except psycopg2.DatabaseError as ex:
        logger.error("Verbindung zu PostgreSQL konnte nicht aufgebaut werden!")
        logger.error(ex)
        logger.error("Import wird abgebrochen!")
        sys.exit()
        
    # execute Query
    cursor.execute(sql_query)
 
    # retrieve all or one records from the database or commit
    if fetch:
        if fetchall:
            records = cursor.fetchall()
        else:
            records = cursor.fetchone()
            if records:
                records = records[0]
    else:
        conn.commit()
    
    cursor.close()
    conn.close()

    if fetch:
        return records