# Cincinnati 311 Dataset Provenance & Metadata

- **Dataset Name**: Cincinnati 311 (Non-Emergency) Service Requests
- **Source Portal**: City of Cincinnati Open Data Portal (Socrata)
- **Portal Landing Page**: https://data.cincinnati-oh.gov/efficient-service-delivery/Cincinnati-311-Non-Emergency-Service-Requests/gcej-gmiw
- **API Endpoint**: https://data.cincinnati-oh.gov/resource/gcej-gmiw.json
- **Metadata Endpoint**: https://data.cincinnati-oh.gov/api/views/gcej-gmiw.json
- **License**: Public Domain (No copyright restrictions)
- **Attribution**: City of Cincinnati
- **Retrieval Date**: 2026-10-20
- **Sampling Method**: First 1,000 active service request records fetched directly via public Socrata API query.
- **Local Raw File**: `ai-ml/data/raw/cincinnati_311_sample.csv` (1,000 rows, 67 columns)
- **Privacy & Security Notes**:
  - Contains municipal address numbers, street names, neighborhoods, and geographic coordinates.
  - Does NOT include citizen names, phone numbers, email addresses, or free-text personal grievance narratives.
