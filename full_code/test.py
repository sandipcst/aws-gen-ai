
import streamlit as st
import sqlparse, re

import sqlvalidator

# sql_query = sqlvalidator.parse("SELECT * from table")

promptinput = st.text_input("Enter your SQL to convert")

output = []

sql = sqlvalidator.parse(promptinput)

if sql.is_valid():
    output.append(promptinput)
else:
    ddls = sqlparse.split(promptinput)
    import re

    #tables_regex = re.compile("CREATE TABLE.*\(", re.IGNORECASE)

    tables_regex = re.compile(r"^(CREATE|ALTER|DROP|GRANT|REVOKE)\s+(TABLE|VIEW|PROCEDURE|)", re.IGNORECASE)
    for ddl in ddls:
        if tables_regex.match(ddl):
            output.append(ddl)
    
    st.write(text for text in output)
