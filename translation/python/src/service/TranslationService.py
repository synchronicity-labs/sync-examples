import os
import requests
from typing import Dict, Optional, Any, List
from openai import OpenAI

class TranslationProcessor:
    """
    Handles transcription and translation using OpenAI API.
    This class provides methods to transcribe audio files and translate text.
    """

    def __init__(self, api_key: str = None):

        if not api_key:
            raise ValueError("OpenAI API key is required in constants.py")
        self.client = OpenAI(api_key=api_key)
    
    def transcribe(self, 
                  audio_file_path: str, 
                  model: str = None
                  ) -> str:
        """
        Transcribe an audio file using OpenAI's Whisper API.
        
        Args:
            audio_file_path (str): Path to the audio file
            model (str): Model to use for transcription. Defaults to "whisper-1".

        Returns:
            Str: Transcription response text containing the transcribed text
        """
        try:
            if not model:
                model = "whisper-1"
            with open(audio_file_path, "rb") as audio_file:
                response = self.client.audio.transcriptions.create(
                    model=model,
                    file=audio_file,
                )
                
            return response.text
                
        except Exception as e:
            print(f"Transcription error: {str(e)}")
            raise
    
    def translate(self, 
                 text: str, 
                 args,
                 preserve_formatting: bool = True,
                 temperature: float = 0.3) -> str:
        """
        Translate text using OpenAI's GPT models.
        
        Args:
            text (str): Text to translate
            source_language (str, optional): Source language.
            target_language (str, optional): Target language. Defaults to "Spanish".
            model (str, optional): GPT model to use. Defaults to "gpt-3.5-turbo".
            preserve_formatting (bool, optional): Whether to preserve formatting. Defaults to True.
            temperature (float, optional): Sampling temperature. Defaults to 0.3.
            
        Returns:
            str: Translated text
        """
        if not args.source_language:
            args.source_language = "the source language"
        if not args.gpt_model:
            args.gpt_model = "gpt-3.5-turbo"
        
        formatting_instruction = "maintaining the original formatting, paragraph breaks, and punctuation" if preserve_formatting else ""
        
        system_prompt = (
            f"You are a professional translator from {args.source_language} to {args.target_language}. "
            f"Translate the following text to {args.target_language}, {formatting_instruction} "
            f"while preserving the original meaning and tone as closely as possible. "
            f"Only return the translated text without any additional explanations."
        )
        
        try:
            response = self.client.chat.completions.create(
                model=args.gpt_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text}
                ],
                temperature=temperature
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Translation error: {str(e)}")
            raise
        