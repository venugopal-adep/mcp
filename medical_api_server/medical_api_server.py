#!/usr/bin/env python3

import asyncio
import aiohttp
import json
import logging
from typing import Any, Dict, List, Optional
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("medical-api-server")

class MedicalAPIServer:
    def __init__(self):
        self.server = Server("medical-api-server")
        self.session = None
        self.setup_handlers()
        
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
        
    def setup_handlers(self):
        @self.server.list_tools()
        async def handle_list_tools() -> list[types.Tool]:
            """List available medical API tools."""
            return [
                types.Tool(
                    name="icd11_lookup",
                    description="Look up ICD-11 codes and medical conditions from WHO",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "entity_id": {
                                "type": "string",
                                "description": "ICD-11 entity ID to look up (e.g., '1435254666')"
                            },
                            "search_term": {
                                "type": "string",
                                "description": "Search term for medical conditions"
                            }
                        }
                    }
                ),
                types.Tool(
                    name="fda_drug_search",
                    description="Search FDA drug database for drug information",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "search_term": {
                                "type": "string",
                                "description": "Drug name to search for (e.g., 'aspirin')"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Number of results to return (default: 5)",
                                "default": 5
                            }
                        },
                        "required": ["search_term"]
                    }
                ),
                types.Tool(
                    name="fda_device_search",
                    description="Search FDA device database for medical device information",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "search_term": {
                                "type": "string",
                                "description": "Device name or type to search for"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Number of results to return (default: 5)",
                                "default": 5
                            }
                        },
                        "required": ["search_term"]
                    }
                ),
                types.Tool(
                    name="infermedica_diagnosis",
                    description="Get medical diagnosis suggestions from Infermedica (requires API key)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "age": {
                                "type": "integer",
                                "description": "Patient age"
                            },
                            "sex": {
                                "type": "string",
                                "enum": ["male", "female"],
                                "description": "Patient sex"
                            },
                            "symptoms": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of symptoms"
                            },
                            "api_key": {
                                "type": "string",
                                "description": "Infermedica API key"
                            }
                        },
                        "required": ["age", "sex", "symptoms", "api_key"]
                    }
                ),
                types.Tool(
                    name="nutrition_facts",
                    description="Get nutritional information for foods using Nutritionix API",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "food_query": {
                                "type": "string",
                                "description": "Food description (e.g., '1 cup rice', '100g chicken breast')"
                            },
                            "api_key": {
                                "type": "string",
                                "description": "Nutritionix API key"
                            },
                            "app_id": {
                                "type": "string",
                                "description": "Nutritionix App ID"
                            }
                        },
                        "required": ["food_query", "api_key", "app_id"]
                    }
                ),
                types.Tool(
                    name="npi_provider_lookup",
                    description="Look up healthcare provider information using NPI number or name",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "npi_number": {
                                "type": "string",
                                "description": "10-digit NPI number"
                            },
                            "provider_name": {
                                "type": "string",
                                "description": "Provider name (first and last)"
                            },
                            "state": {
                                "type": "string",
                                "description": "State abbreviation (e.g., 'CA', 'NY')"
                            }
                        }
                    }
                ),
                types.Tool(
                    name="cms_marketplace_plans",
                    description="Search CMS Marketplace for health insurance plans",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "zip_code": {
                                "type": "string",
                                "description": "ZIP code for plan search"
                            },
                            "age": {
                                "type": "integer",
                                "description": "Age for premium calculation"
                            },
                            "api_key": {
                                "type": "string",
                                "description": "CMS API key"
                            }
                        },
                        "required": ["zip_code", "api_key"]
                    }
                ),
                types.Tool(
                    name="covid_stats_global",
                    description="Get global COVID-19 statistics",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                types.Tool(
                    name="covid_stats_country",
                    description="Get COVID-19 statistics for a specific country",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "country": {
                                "type": "string",
                                "description": "Country name (e.g., 'USA', 'UK', 'India')"
                            }
                        },
                        "required": ["country"]
                    }
                ),
                types.Tool(
                    name="nhs_scotland_data",
                    description="Search NHS Scotland open data",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "resource_id": {
                                "type": "string",
                                "description": "Resource ID for the dataset"
                            },
                            "query": {
                                "type": "string",
                                "description": "Search query"
                            }
                        },
                        "required": ["resource_id"]
                    }
                )
            ]

        @self.server.call_tool()
        async def handle_call_tool(
            name: str, arguments: dict[str, Any] | None
        ) -> list[types.TextContent]:
            """Handle tool calls."""
            if arguments is None:
                arguments = {}

            try:
                if name == "icd11_lookup":
                    result = await self._icd11_lookup(
                        arguments.get("entity_id"),
                        arguments.get("search_term")
                    )
                    return [types.TextContent(type="text", text=result)]
                
                elif name == "fda_drug_search":
                    result = await self._fda_drug_search(
                        arguments.get("search_term", ""),
                        arguments.get("limit", 5)
                    )
                    return [types.TextContent(type="text", text=result)]
                
                elif name == "fda_device_search":
                    result = await self._fda_device_search(
                        arguments.get("search_term", ""),
                        arguments.get("limit", 5)
                    )
                    return [types.TextContent(type="text", text=result)]
                
                elif name == "infermedica_diagnosis":
                    result = await self._infermedica_diagnosis(
                        arguments.get("age"),
                        arguments.get("sex"),
                        arguments.get("symptoms", []),
                        arguments.get("api_key", "")
                    )
                    return [types.TextContent(type="text", text=result)]
                
                elif name == "nutrition_facts":
                    result = await self._nutrition_facts(
                        arguments.get("food_query", ""),
                        arguments.get("api_key", ""),
                        arguments.get("app_id", "")
                    )
                    return [types.TextContent(type="text", text=result)]
                
                elif name == "npi_provider_lookup":
                    result = await self._npi_provider_lookup(
                        arguments.get("npi_number"),
                        arguments.get("provider_name"),
                        arguments.get("state")
                    )
                    return [types.TextContent(type="text", text=result)]
                
                elif name == "cms_marketplace_plans":
                    result = await self._cms_marketplace_plans(
                        arguments.get("zip_code", ""),
                        arguments.get("age"),
                        arguments.get("api_key", "")
                    )
                    return [types.TextContent(type="text", text=result)]
                
                elif name == "covid_stats_global":
                    result = await self._covid_stats_global()
                    return [types.TextContent(type="text", text=result)]
                
                elif name == "covid_stats_country":
                    result = await self._covid_stats_country(arguments.get("country", ""))
                    return [types.TextContent(type="text", text=result)]
                
                elif name == "nhs_scotland_data":
                    result = await self._nhs_scotland_data(
                        arguments.get("resource_id", ""),
                        arguments.get("query")
                    )
                    return [types.TextContent(type="text", text=result)]
                
                else:
                    raise ValueError(f"Unknown tool: {name}")
                    
            except Exception as e:
                logger.error(f"Error in tool {name}: {e}")
                return [types.TextContent(type="text", text=f"Error: {str(e)}")]

    async def _ensure_session(self):
        """Ensure we have an active session."""
        if not self.session:
            self.session = aiohttp.ClientSession()

    async def _icd11_lookup(self, entity_id: Optional[str], search_term: Optional[str]) -> str:
        """Look up ICD-11 codes and conditions."""
        try:
            await self._ensure_session()
            base_url = "https://icd11restapi-developer-test.azurewebsites.net"
            
            if entity_id:
                url = f"{base_url}/icd/entity/{entity_id}"
                async with self.session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return json.dumps(data, indent=2)
                    else:
                        return f"Error: HTTP {response.status} - {await response.text()}"
            
            elif search_term:
                # Search functionality would require different endpoint
                url = f"{base_url}/icd/release/11/2024-01/mms/search"
                params = {"q": search_term}
                async with self.session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return json.dumps(data, indent=2)
                    else:
                        return f"Error: HTTP {response.status} - {await response.text()}"
            
            else:
                return "Error: Either entity_id or search_term is required"
                
        except Exception as e:
            return f"ICD-11 Lookup Error: {str(e)}"

    async def _fda_drug_search(self, search_term: str, limit: int) -> str:
        """Search FDA drug database."""
        if not search_term:
            return "Error: Search term is required"
        
        try:
            await self._ensure_session()
            url = "https://api.fda.gov/drug/label.json"
            params = {
                "search": f"openfda.brand_name:{search_term} OR openfda.generic_name:{search_term}",
                "limit": limit
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return json.dumps(data, indent=2)
                else:
                    return f"Error: HTTP {response.status} - {await response.text()}"
                    
        except Exception as e:
            return f"FDA Drug Search Error: {str(e)}"

    async def _fda_device_search(self, search_term: str, limit: int) -> str:
        """Search FDA device database."""
        if not search_term:
            return "Error: Search term is required"
        
        try:
            await self._ensure_session()
            url = "https://api.fda.gov/device/510k.json"
            params = {
                "search": f"device_name:{search_term}",
                "limit": limit
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return json.dumps(data, indent=2)
                else:
                    return f"Error: HTTP {response.status} - {await response.text()}"
                    
        except Exception as e:
            return f"FDA Device Search Error: {str(e)}"

    async def _infermedica_diagnosis(self, age: int, sex: str, symptoms: List[str], api_key: str) -> str:
        """Get diagnosis suggestions from Infermedica."""
        if not all([age, sex, symptoms, api_key]):
            return "Error: Age, sex, symptoms, and API key are required"
        
        try:
            await self._ensure_session()
            url = "https://api.infermedica.com/v3/diagnosis"
            headers = {
                "App-Id": api_key,
                "App-Key": api_key,
                "Content-Type": "application/json"
            }
            
            # Convert symptoms to evidence format (simplified)
            evidence = [{"id": symptom.lower().replace(" ", "_"), "choice_id": "present"} for symptom in symptoms]
            
            data = {
                "sex": sex,
                "age": {"value": age},
                "evidence": evidence
            }
            
            async with self.session.post(url, json=data, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    return json.dumps(result, indent=2)
                else:
                    return f"Error: HTTP {response.status} - {await response.text()}"
                    
        except Exception as e:
            return f"Infermedica Diagnosis Error: {str(e)}"

    async def _nutrition_facts(self, food_query: str, api_key: str, app_id: str) -> str:
        """Get nutritional information using Nutritionix."""
        if not all([food_query, api_key, app_id]):
            return "Error: Food query, API key, and App ID are required"
        
        try:
            await self._ensure_session()
            url = "https://trackapi.nutritionix.com/v2/natural/nutrients"
            headers = {
                "x-app-id": app_id,
                "x-app-key": api_key,
                "Content-Type": "application/json"
            }
            
            data = {"query": food_query}
            
            async with self.session.post(url, json=data, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    return json.dumps(result, indent=2)
                else:
                    return f"Error: HTTP {response.status} - {await response.text()}"
                    
        except Exception as e:
            return f"Nutrition Facts Error: {str(e)}"

    async def _npi_provider_lookup(self, npi_number: Optional[str], provider_name: Optional[str], state: Optional[str]) -> str:
        """Look up healthcare provider using NPI registry."""
        try:
            await self._ensure_session()
            url = "https://npiregistry.cms.hhs.gov/api/"
            params = {}
            
            if npi_number:
                params["number"] = npi_number
            elif provider_name:
                # Split name for first_name and last_name
                name_parts = provider_name.split()
                if len(name_parts) >= 2:
                    params["first_name"] = name_parts[0]
                    params["last_name"] = " ".join(name_parts[1:])
                else:
                    params["last_name"] = provider_name
            
            if state:
                params["state"] = state
            
            if not params:
                return "Error: Either NPI number or provider name is required"
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return json.dumps(data, indent=2)
                else:
                    return f"Error: HTTP {response.status} - {await response.text()}"
                    
        except Exception as e:
            return f"NPI Provider Lookup Error: {str(e)}"

    async def _cms_marketplace_plans(self, zip_code: str, age: Optional[int], api_key: str) -> str:
        """Search CMS Marketplace plans."""
        if not zip_code or not api_key:
            return "Error: ZIP code and API key are required"
        
        try:
            await self._ensure_session()
            url = "https://marketplace.api.healthcare.gov/api/v1/plans/search"
            headers = {"Authorization": f"Bearer {api_key}"}
            params = {
                "zipcode": zip_code,
                "market": "Individual"
            }
            
            if age:
                params["age"] = age
            
            async with self.session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return json.dumps(data, indent=2)
                else:
                    return f"Error: HTTP {response.status} - {await response.text()}"
                    
        except Exception as e:
            return f"CMS Marketplace Error: {str(e)}"

    async def _covid_stats_global(self) -> str:
        """Get global COVID-19 statistics."""
        try:
            await self._ensure_session()
            url = "https://disease.sh/v3/covid-19/all"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return json.dumps(data, indent=2)
                else:
                    return f"Error: HTTP {response.status} - {await response.text()}"
                    
        except Exception as e:
            return f"COVID Stats Global Error: {str(e)}"

    async def _covid_stats_country(self, country: str) -> str:
        """Get COVID-19 statistics for a specific country."""
        if not country:
            return "Error: Country is required"
        
        try:
            await self._ensure_session()
            url = f"https://disease.sh/v3/covid-19/countries/{country}"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return json.dumps(data, indent=2)
                else:
                    return f"Error: HTTP {response.status} - {await response.text()}"
                    
        except Exception as e:
            return f"COVID Stats Country Error: {str(e)}"

    async def _nhs_scotland_data(self, resource_id: str, query: Optional[str]) -> str:
        """Search NHS Scotland open data."""
        if not resource_id:
            return "Error: Resource ID is required"
        
        try:
            await self._ensure_session()
            url = "https://www.opendata.nhs.scot/api/3/action/datastore_search"
            params = {"resource_id": resource_id}
            
            if query:
                params["q"] = query
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return json.dumps(data, indent=2)
                else:
                    return f"Error: HTTP {response.status} - {await response.text()}"
                    
        except Exception as e:
            return f"NHS Scotland Data Error: {str(e)}"

async def main():
    """Main function to run the medical API server."""
    async with MedicalAPIServer() as medical_server:
        # Run the server using stdin/stdout streams
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await medical_server.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="medical-api-server",
                    server_version="0.1.0",
                    capabilities=medical_server.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )

if __name__ == "__main__":
    asyncio.run(main())