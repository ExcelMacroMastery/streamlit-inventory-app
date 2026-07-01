#from data.schema import TableSchema, ColumnDef
from streamlit_crud import TableSchema, ColumnDef

CUSTOMERS = TableSchema(
    table="customers",
    primary_key="id",
    columns=[
        ColumnDef("id",      "int", required=False, default=None, widget="hidden", hide=True),
        ColumnDef("name",    "str", required=True,  default="",   widget="text",   label="Name",    width=150),
        ColumnDef("email",   "str", required=False, default="",   widget="text",   label="Email",   width=150),
        ColumnDef("phone",   "str", required=False, default="",   widget="text",   label="Phone",   width=100),
        ColumnDef("address", "str", required=False, default="",   widget="text",   label="Address", width=200),
    ]
)
