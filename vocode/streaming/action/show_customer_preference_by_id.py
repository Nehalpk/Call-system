import aiohttp
from typing import Type, Optional
from pydantic.v1 import BaseModel, Field

from vocode.streaming.action.base_action import BaseAction
from vocode.streaming.models.actions import (
    ActionConfig,
    ActionInput,
    ActionOutput,
    ActionType,
)

class FetchOptionsByIdsActionConfig(ActionConfig, type=ActionType.FETCH_OPTIONS_BY_IDS):
    token: str
    url: str

class FetchOptionsByIdsParameters(BaseModel):
    option_ids: list[str] = Field(..., description="A list of option IDs to fetch.")

class FetchOptionsByIdsResponse(BaseModel):
    matching_options: Optional[list[dict]]
    success: bool
    error: Optional[str] = None

class FetchOptionsByIds(
    BaseAction[
        FetchOptionsByIdsActionConfig,
        FetchOptionsByIdsParameters,
        FetchOptionsByIdsResponse
    ]
):
    description: str = "Fetch all customer preferences from a GraphQL API and return the details of specific options by their IDs."
    parameters_type: Type[FetchOptionsByIdsParameters] = FetchOptionsByIdsParameters
    response_type: Type[FetchOptionsByIdsResponse] = FetchOptionsByIdsResponse

    async def fetch_options(self, option_ids: list[str], token: str, url: str) -> list[dict]:
        query = """
        query CustomerPreferences {
            customerPreferences {
                id
                name
                options {
                    id
                    name
                }
                hideCustomerPreference
            }
        }
        """

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json={'query': query}, headers=headers) as response:
                data = await response.json()

        matching_options = []
        for preference in data.get('data', {}).get('customerPreferences', []):
            for option in preference.get('options', []):
                if option['id'] in option_ids:
                    matching_options.append({
                        "preference_id": preference['id'],
                        "preference_name": preference['name'],
                        "option_id": option['id'],
                        "option_name": option['name'],
                        "hideCustomerPreference": preference['hideCustomerPreference']
                    })

        return matching_options

    async def run(
        self, action_input: ActionInput[FetchOptionsByIdsParameters]
    ) -> ActionOutput[FetchOptionsByIdsResponse]:
        try:
            matching_options = await self.fetch_options(
                action_input.params.option_ids,
                self.action_config.token,
                self.action_config.url
            )
            return ActionOutput(
                action_type=self.action_config.type,
                response=FetchOptionsByIdsResponse(success=True, matching_options=matching_options)
            )
        except Exception as e:
            return ActionOutput(
                action_type=self.action_config.type,
                response=FetchOptionsByIdsResponse(success=False, error=str(e))
            )
