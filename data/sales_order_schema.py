#from data.schema import TableSchema, ColumnDef
from streamlit_crud import TableSchema, ColumnDef

SALES_ORDERS = TableSchema(
    table="sales_orders",
    primary_key="id",
    columns=[
        ColumnDef("id",          "int",   required=False, default=None, widget="hidden", hide=True),
        ColumnDef("customer_id", "int",   required=True,  default=None, widget="hidden", hide=True),
        ColumnDef("subtotal",    "float", required=False, default=0.0,  widget="currency", label="Subtotal"),
        ColumnDef("tax",         "float", required=False, default=0.0,  widget="currency", label="Tax"),
        ColumnDef("total",       "float", required=False, default=0.0,  widget="currency", label="Total"),
        ColumnDef("created_at",  "str",   required=False, default=None, widget="hidden", hide=True),
    ]
)

SALES_ORDER_LINES = TableSchema(
    table="sales_order_lines",
    primary_key="id",
    columns=[
        ColumnDef("id",           "int",   required=False, default=None, widget="hidden", hide=True),
        ColumnDef("order_id",     "int",   required=True,  default=None, widget="hidden", hide=True),
        ColumnDef("product_id",   "int",   required=True,  default=None, widget="hidden", hide=True),
        ColumnDef("product_name", "str",   required=True,  default="",   widget="text",   label="Product"),
        ColumnDef("price",        "float", required=True,  default=0.0,  widget="currency", label="Price"),
        ColumnDef("quantity",     "int",   required=True,  default=1,    widget="number", label="Qty"),
        ColumnDef("line_total",   "float", required=True,  default=0.0,  widget="currency", label="Total"),
    ]
)

TAX_RATE = 0.10  # 10% fixed
