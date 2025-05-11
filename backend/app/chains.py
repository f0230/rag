def _call(
        self, 
        prompt: str, 
        stop: List[str] = None, 
        run_manager: CallbackManagerForLLMRun = None,
        **kwargs: Any,
    ) -> str:
        """Call the Khoj API and return the response."""
        import requests
        import json
        import logging
        
        logging.info(f"Calling Khoj API with prompt: {prompt[:100]}...")
        
        try:
            # First check if Khoj is available
            health_check = requests.get(f"{self.khoj_url}/api/health")
            if health_check.status_code != 200:
                logging.error(f"Khoj service is not available. Status: {health_check.status_code}")
                return "Error: Khoj service is not available. Please check if the service is running."
            
            # If Khoj is available, make the actual request
            response = requests.post(
                f"{self.khoj_url}/api/chat",
                headers={"Content-Type": "application/json"},
                data=json.dumps({
                    "message": prompt,
                    "use_context": True,  # Enable retrieval
                }),
                timeout=30  # Add timeout to prevent hanging
            )
            response.raise_for_status()
            result = response.json()
            return result.get("response", "No response from Khoj")
        except requests.exceptions.ConnectionError as e:
            logging.error(f"Connection error to Khoj API: {e}")
            return "Error: Could not connect to Khoj service. Please ensure the service is running."
        except requests.exceptions.Timeout as e:
            logging.error(f"Timeout error calling Khoj API: {e}")
            return "Error: Request to Khoj timed out. The service might be under heavy load."
        except requests.exceptions.RequestException as e:
            logging.error(f"Request error calling Khoj API: {e}")
            return f"Error: Request to Khoj failed. {str(e)}"
        except Exception as e:
            logging.error(f"Unexpected error calling Khoj API: {e}")
            return f"Error: Could not get response from Khoj. {str(e)}"