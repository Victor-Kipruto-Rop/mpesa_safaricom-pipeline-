# 2. M-Pesa Agent Network Analytics

## Difficulty: Intermediate | Impact: High

### Overview
Ingest CBK agent banking data and Safaricom agent locator data to build a geospatial data product mapping agent density, transaction volumes, float availability, and commission trends per ward. Identify under-served areas and model optimal new agent placement.

### Tools Required
- Python
- PostGIS
- dbt
- Apache Airflow
- Kepler.gl
- Leaflet.js
- DuckDB

### Kenyan Data Sources
- CBK Agent Banking Annual Report
- Safaricom Agent Locator API
- OpenStreetMap Kenya

### Project Structure
```
mpesa-agent-analytics/
ingestion/
  cbk_agent_scraper.py # Download CBK agent banking PDFs
  pdf_extractor.py # pdfplumber: extract agent tables
  geocoder.py # Geocode agent locations → lat/lng
dbt/models/
  staging/stg_agents.sql
  staging/stg_wards.sql # Kenya ward boundary seed
  marts/mart_agent_density.sql
  marts/mart_float_coverage.sql
spatial/
  ward_analysis.py # PostGIS spatial joins
  optimal_placement.py # KMeans clustering for new agents
maps/
  kepler_config.json # Kepler.gl map configuration
seeds/
  kenya_wards.csv # 47 counties, 290 wards reference
tests/
dags/
notebooks/
docs/
```

### Key Deliverables
- PostGIS database with agent locations
- Agent density heatmaps by ward
- Transaction volume analysis per agent
- Optimal placement recommendations
- Interactive maps (Kepler.gl & Leaflet.js)

### Next Steps
1. Download CBK agent data
2. Configure PostGIS database
3. Build data ingestion pipeline
4. Create geospatial analytics
5. Deploy interactive visualizations
