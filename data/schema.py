# data/schema.py
from dataclasses import dataclass, field
from typing import Any

class ValidationError(Exception):
    def __init__(self, errors: list[str]):
        self.errors = errors
        super().__init__("\n".join(errors))

@dataclass
class ColumnDef:
    name: str
    dtype: str          # 'str', 'int', 'float'
    required: bool = True
    default: Any = None
    widget: str = "text"
    # Grid display
    label: str = ""
    width: int = 100
    hide: bool = False
    format: str = ""    

def __post_init__(self):
        if not self.label:
            self.label = self.name.title()  # default label from name if not provided

@dataclass
class TableSchema:
    table: str
    primary_key: int
    columns: list[ColumnDef]
    categories: dict[str, list[str]] = field(default_factory=dict)  # categorical columns and their valid values

    def col_names(self, exclude_pk: bool = False) -> list[str]:
        return [c.name for c in self.columns if not exclude_pk or c.name != self.primary_key]

    
    def col_names_commas(self, exclude_pk: bool = False) -> list[str]:
        cols = self.col_names(exclude_pk)
        return ", ".join(f"[{c}]" for c in cols if c != self.primary_key) # list of table names

    def col_names_clause(self, exclude_pk: bool = False) -> list[str]:
        cols = self.col_names(exclude_pk)
        return ", ".join(f"{c} = ?" for c in cols)

    def col_by_name(self, name: str) -> ColumnDef:
        return next(c for c in self.columns if c.name == name)

    def col_values(self, row: dict, exclude_pk: bool = False) -> tuple:
        cols = self.col_names(exclude_pk)
        return tuple(row[c] for c in cols if c != self.primary_key)

    def required_cols(self, exclude_pk: bool = False) -> list[str]:
        return [c.name for c in self.columns if c.required and c.name != self.primary_key]
        
    def missing_col_values(self, row: dict, exclude_pk: bool = False) -> list[str]:
        return [c for c in self.required_cols(exclude_pk=exclude_pk) if not row.get(c)]

    def defaults(self) -> dict[str, Any]:
        return {c.name: c.default for c in self.columns}
    
    def validate(self, row: dict, exclude_pk: bool = False) -> None:
        """Raises ValidationError if row is invalid."""
        errors = []
        for col in self.columns:
            if exclude_pk and col.name == self.primary_key:
                continue
            if col.required and not row.get(col.name):
                errors.append(f"{col.name.title()} is required.")
            if col.dtype == "int" and row.get(col.name) is not None:
                if not isinstance(row[col.name], int):
                    errors.append(f"{col.name.title()} must be a whole number.")
            if col.dtype == "float" and row.get(col.name) is not None:
                if not isinstance(row[col.name], (int, float)):
                    errors.append(f"{col.name.title()} must be a number.")
        if errors:
            raise ValidationError(errors)      
    


