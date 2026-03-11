import os
import json
import google.generativeai as genai
from domain.interfaces.ai_service import AIService, AIRequest, AIResponse, AIServiceError


class GeminiService(AIService):

    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in .env file")

        genai.configure(api_key=api_key)

        # Use the available model (with models/ prefix for the actual SDK call)
        self.model_name = "gemini-2.5-flash"
        self.model = genai.GenerativeModel("models/gemini-2.5-flash")

    async def generate(self, request: AIRequest) -> AIResponse:
        """
        Generate content using Google's Gemini API.
        
        Args:
            request: AIRequest with system_prompt, user_prompt, and other parameters
            
        Returns:
            AIResponse with generated content and token usage
            
        Raises:
            AIServiceError: On API failures
        """
        try:
            # Combine system and user prompts
            full_prompt = f"{request.system_prompt}\n\n{request.user_prompt}"
            
            # Configure generation parameters
            generation_config = genai.GenerationConfig(
                temperature=request.temperature,
                max_output_tokens=request.max_tokens,
                response_mime_type="application/json" if request.response_format == "json_object" else "text/plain"
            )
            
            # Call the Gemini API (synchronous, but we're in an async context)
            response = self.model.generate_content(
                full_prompt,
                generation_config=generation_config
            )
            
            # Extract content
            content = response.text
            
            # Parse token counts from response
            # Gemini API returns usage_metadata with prompt_token_count and candidates_token_count
            prompt_tokens = 0
            completion_tokens = 0
            
            if hasattr(response, 'usage_metadata') and response.usage_metadata:
                prompt_tokens = getattr(response.usage_metadata, 'prompt_token_count', 0)
                completion_tokens = getattr(response.usage_metadata, 'candidates_token_count', 0)
            
            # Determine finish reason from candidates
            # Gemini SDK may return an integer proto enum value OR a named enum.
            # Map all known integer values to normalized strings.
            _FINISH_REASON_MAP = {
                "1": "stop",       # FinishReason.STOP
                "2": "max_tokens", # FinishReason.MAX_TOKENS
                "3": "safety",     # FinishReason.SAFETY
                "4": "recitation", # FinishReason.RECITATION
                "5": "other",      # FinishReason.OTHER
            }
            finish_reason = "stop"
            if hasattr(response, 'candidates') and response.candidates and len(response.candidates) > 0:
                finish_reason_enum = getattr(response.candidates[0], 'finish_reason', None)
                if finish_reason_enum is not None:
                    raw = str(finish_reason_enum).split('.')[-1].lower()
                    # If the SDK gave us a bare integer string, look it up
                    finish_reason = _FINISH_REASON_MAP.get(raw, raw)
            
            return AIResponse(
                content=content,
                model=self.model_name,
                prompt_tokens=int(prompt_tokens) if prompt_tokens else 0,
                completion_tokens=int(completion_tokens) if completion_tokens else 0,
                finish_reason=finish_reason,
                raw_response=None
            )
            
        except AIServiceError:
            raise
        except Exception as e:
            raise AIServiceError(f"Gemini API call failed: {str(e)}", status_code=502)

    def get_default_model(self) -> str:
        return self.model_name