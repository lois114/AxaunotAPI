from datetime import datetime
from pathlib import Path
from openpyxl.styles import Font
from openpyxl.utils import get_column_letter
import pandas as pd


def export_workbook(sheets: dict):
    output_dir = Path("exports")
    output_dir.mkdir(exist_ok=True)

    filename = output_dir / f"export_axonaut_{datetime.now().strftime('%Y-%m-%d')}.xlsx"

    with pd.ExcelWriter(filename, engine="openpyxl") as writer:
        for sheet_name, df in sheets.items():
            safe_sheet_name = sheet_name[:31]
            df.to_excel(writer, sheet_name=safe_sheet_name, index=False)

            ws = writer.book[safe_sheet_name]

            for cell in ws[1]:
                cell.font = Font(bold=True)

            ws.auto_filter.ref = ws.dimensions
            ws.freeze_panes = "A2"

            for col_idx, column_cells in enumerate(ws.columns, start=1):
                max_length = 0
                for cell in column_cells:
                    value = "" if cell.value is None else str(cell.value)
                    max_length = max(max_length, len(value))
                ws.column_dimensions[get_column_letter(col_idx)].width = min(max_length + 2, 40)

    print(f"Fichier généré : {filename}")
    return str(filename)
