import json
from pathlib import Path
import aiohttp
import asyncio
from loguru import logger
from typing import Dict, Optional, Union
import base64
from io import BytesIO

class ComfyUIManager:
    def __init__(self, kaggle_notebook_url: str):
        self.kaggle_notebook_url = kaggle_notebook_url
        self.workflows_path = Path("workflows")
        self.workflows = self._load_workflows()
        
    def _load_workflows(self) -> Dict:
        """Load all workflow JSON files"""
        workflows = {}
        if not self.workflows_path.exists():
            self.workflows_path.mkdir(exist_ok=True)
            return workflows
            
        for workflow_file in self.workflows_path.glob("*.json"):
            try:
                with open(workflow_file, 'r', encoding='utf-8') as f:
                    workflows[workflow_file.stem] = json.load(f)
            except Exception as e:
                logger.error(f"Error loading workflow {workflow_file}: {e}")
        return workflows

    def add_workflow(self, name: str, workflow_json: Dict):
        """Add a new workflow"""
        workflow_file = self.workflows_path / f"{name}.json"
        with open(workflow_file, 'w') as f:
            json.dump(workflow_json, f, indent=4)
        self.workflows[name] = workflow_json
        logger.info(f"Added new workflow: {name}")

    async def process_image(self, workflow_name: str, prompt: str, input_image: Optional[bytes] = None) -> bytes:
        """Process an image using specified workflow"""
        if workflow_name not in self.workflows:
            raise ValueError(f"Workflow {workflow_name} not found")

        workflow = self.workflows[workflow_name]
        
        # Prepare the workflow with the user's input
        modified_workflow = self._prepare_workflow(workflow, prompt, input_image)
        
        try:
            async with aiohttp.ClientSession() as session:
                # Send workflow to ComfyUI
                async with session.post(
                    f"{self.kaggle_notebook_url}/queue",
                    json=modified_workflow
                ) as response:
                    if response.status != 200:
                        raise Exception(f"Error queuing workflow: {await response.text()}")
                    
                    prompt_id = (await response.json())['prompt_id']
                    
                    # Wait for the result
                    result = await self._wait_for_result(session, prompt_id)
                    
                    # Get the generated image
                    image_data = await self._get_image(session, result)
                    
                    return image_data
                    
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            raise

    def _prepare_workflow(self, workflow: Dict, prompt: str, input_image: Optional[bytes] = None) -> Dict:
        """Prepare workflow with user inputs"""
        modified_workflow = workflow.copy()
        
        # Update prompt in workflow
        for node in modified_workflow['nodes']:
            if node.get('type') == 'text':
                node['inputs']['text'] = prompt
            elif node.get('type') == 'image' and input_image:
                # Convert input image to base64
                image_b64 = base64.b64encode(input_image).decode('utf-8')
                node['inputs']['image'] = image_b64
                
        return modified_workflow

    async def _wait_for_result(self, session: aiohttp.ClientSession, prompt_id: str) -> Dict:
        """Wait for the workflow to complete and return result"""
        while True:
            async with session.get(f"{self.kaggle_notebook_url}/history/{prompt_id}") as response:
                if response.status != 200:
                    raise Exception(f"Error checking history: {await response.text()}")
                
                result = await response.json()
                if result.get('status') == 'completed':
                    return result
                    
                await asyncio.sleep(1)

    async def _get_image(self, session: aiohttp.ClientSession, result: Dict) -> bytes:
        """Get the generated image from the result"""
        image_url = result['output_images'][0]
        async with session.get(image_url) as response:
            if response.status != 200:
                raise Exception(f"Error downloading image: {await response.text()}")
            return await response.read()

    def get_workflow_info(self, workflow_name: str) -> Dict:
        """Get information about a specific workflow"""
        if workflow_name not in self.workflows:
            raise ValueError(f"Workflow {workflow_name} not found")
            
        return {
            "name": workflow_name,
            "nodes": len(self.workflows[workflow_name]['nodes']),
            "description": self.workflows[workflow_name].get('description', 'No description available')
        }
