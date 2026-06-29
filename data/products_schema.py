from data.schema import TableSchema, ColumnDef

PRODUCTS = TableSchema(
    table="products",
    primary_key="id",
    categories={
        "category": ["Apparel", "Electronics", "Furniture", "Groceries", "Home"]
    },
    columns=[
        ColumnDef("id",       "int",   required=False, default=None,  widget="hidden", hide=True),
        ColumnDef("name",     "str",   required=True,  default="",    widget="text",   label="Name",     width=130),
        ColumnDef("sku",      "str",   required=True,  default="",    widget="text",   label="SKU",      width=100),
        ColumnDef("category", "str",   required=True,  default="Home",widget="select", label="Category", width=100),
        ColumnDef("quantity", "int",   required=False,  default=0,     widget="number", label="Quantity", width=65),
        ColumnDef("price",    "float", required=True,  default=0.0,   widget="currency",label="Price",   width=65,  format="currency"),
    ]
)