# Medical API MCP Server

A Model Context Protocol (MCP) server that provides access to various medical and healthcare APIs.

## Features

This server integrates with multiple medical APIs to provide comprehensive healthcare data access:

### Available APIs

1. **WHO ICD-11** - International Classification of Diseases
   - Look up medical conditions and codes
   - Free developer endpoint (test/dev only)

2. **openFDA** - FDA drug and device databases
   - Search drug information
   - Search medical device information
   - No API key required

3. **Infermedica** - Medical diagnosis assistance
   - Get diagnosis suggestions based on symptoms
   - Requires API key (free trial available)

4. **Nutritionix** - Nutritional information
   - Get detailed nutrition facts for foods
   - Requires API key and App ID

5. **NPPES** - Healthcare provider registry
   - Look up healthcare providers by NPI number or name
   - No API key required

6. **CMS Marketplace** - Health insurance plans
   - Search marketplace insurance plans
   - Requires API key

7. **COVID-19 APIs** - Disease statistics
   - Global and country-specific COVID-19 data
   - No API key required

8. **NHS Scotland Open Data** - Scottish health data
   - Access NHS Scotland datasets
   - No API key required

## Installation

1. Navigate to the medical_api_server directory:
```bash
cd servers/medical_api_server
```

2. Install dependencies:
```bash
uv sync
```

## Configuration

### Claude Desktop Integration

To use this server with Claude Desktop, add the following configuration to your `claude_desktop_config.json` file:

```json
{
    "mcpServers": {
        "medical_api": {
            "command": "/opt/anaconda3/bin/uv",
            "args": [
                "--directory", "/Users/venugopal.adep/mcp/servers/medical_api_server",
                "run", 
                "medical_api_server.py"
            ]
        }
    }
}
```

**Configuration file location:**
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

After updating the configuration, restart Claude Desktop to load the medical API server.

## Usage

### Running the Server

```bash
uv run medical_api_server.py
```

### Available Tools

#### `icd11_lookup`
Look up ICD-11 medical conditions and codes.
- `entity_id` (optional): Specific ICD-11 entity ID
- `search_term` (optional): Search term for conditions

#### `fda_drug_search`
Search FDA drug database.
- `search_term` (required): Drug name to search for
- `limit` (optional): Number of results (default: 5)

#### `fda_device_search`
Search FDA medical device database.
- `search_term` (required): Device name or type
- `limit` (optional): Number of results (default: 5)

#### `infermedica_diagnosis`
Get medical diagnosis suggestions.
- `age` (required): Patient age
- `sex` (required): "male" or "female"
- `symptoms` (required): Array of symptom descriptions
- `api_key` (required): Infermedica API key

#### `nutrition_facts`
Get nutritional information for foods.
- `food_query` (required): Food description (e.g., "1 cup rice")
- `api_key` (required): Nutritionix API key
- `app_id` (required): Nutritionix App ID

#### `npi_provider_lookup`
Look up healthcare providers.
- `npi_number` (optional): 10-digit NPI number
- `provider_name` (optional): Provider name
- `state` (optional): State abbreviation

#### `cms_marketplace_plans`
Search health insurance marketplace plans.
- `zip_code` (required): ZIP code for search
- `age` (optional): Age for premium calculation
- `api_key` (required): CMS API key

#### `covid_stats_global`
Get global COVID-19 statistics.
- No parameters required

#### `covid_stats_country`
Get COVID-19 statistics for a specific country.
- `country` (required): Country name (e.g., "USA", "UK")

#### `nhs_scotland_data`
Search NHS Scotland open data.
- `resource_id` (required): Dataset resource ID
- `query` (optional): Search query within dataset

## API Keys

Some APIs require authentication:

- **Infermedica**: Sign up at https://developer.infermedica.com/
- **Nutritionix**: Get keys at https://www.nutritionix.com/business/api
- **CMS Marketplace**: Register at https://marketplace.api.healthcare.gov/

## Example Usage

```python
# Search for aspirin information
fda_drug_search(search_term="aspirin", limit=3)

# Look up a healthcare provider
npi_provider_lookup(provider_name="John Smith", state="CA")

# Get global COVID-19 stats
covid_stats_global()

# Get nutrition facts
nutrition_facts(
    food_query="1 medium apple",
    api_key="your_nutritionix_key",
    app_id="your_app_id"
)
```

## Error Handling

The server includes comprehensive error handling for:
- Network connectivity issues
- API rate limits
- Invalid parameters
- Authentication failures
- Malformed responses

## License

This project is licensed under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Disclaimer

This server is for educational and development purposes. Always consult qualified healthcare professionals for medical advice. The APIs integrated may have usage limitations and terms of service that users must comply with.