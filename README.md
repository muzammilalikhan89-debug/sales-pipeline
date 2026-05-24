# Sales Pipeline

A sales data pipeline project that generates raw data, cleans and loads it into SQL, performs KPI analysis, and exports a dashboard.

## Project structure

- `main.py` — runs the full pipeline
- `Generating Data S1.py` — generates raw sales data
- `Etl_Pipwline S2.py` — cleans the data and loads it into SQLite
- `Sql_Analysis S3.py` — runs SQL KPI queries against the warehouse
- `Dashboard S4.py` — builds and exports the dashboard image

## Files included

- `raw_sales_data.csv` — generated sample sales data
- `sales_warehouse.db` — SQLite warehouse database
- `etl_audit_log.txt` — ETL audit log
- `sales_dashboard.png` — exported dashboard image
- `kpi_*.csv` — KPI tables generated for dashboard input

## Usage

1. Open the project folder in VS Code.
2. Ensure Python is installed and `pandas`, `matplotlib`, and `sqlite3` are available.
3. Run:
   ```powershell
   python main.py
   ```
4. The pipeline will generate raw data, run ETL and analysis, and export the dashboard.

## Notes

- Large binary files and downloads are excluded from version control via `.gitignore`.
- The repository is set up to keep only the core project files and avoid committing large installers.

## License

This project is released under the MIT License.
