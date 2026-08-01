import os
from pathlib import Path
from playsound3 import playsound
from dotenv import load_dotenv

# import namespaces
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider



def main():
    try:
        # Clear the console
        os.system('cls' if os.name == 'nt' else 'clear')
        
        # Get Configuration Settings
        load_dotenv()
        endpoint = os.getenv("MODEL_ENDPOINT")
        model_deployment_transcribe = os.getenv("MODEL_NAME_TRANSCRIBE")
        model_deployment_tts = os.getenv("MODEL_NAME_TTS")
        # file_path = Path(__file__).parent / "speech.mp3"
        
        speech_file_path = Path(__file__).parent / "speech.mp3"
        
        # Play the speech file
        # playsound(file_path)
        
        # Create the Azure OpenAI client
        token_provider = get_bearer_token_provider(                    
            DefaultAzureCredential(), "https://ai.azure.com/.default"
        )

        client = AzureOpenAI(
            azure_endpoint=endpoint,
            azure_ad_token_provider = token_provider,
            api_version="2025-03-01-preview"
        )


         # Generate speech and save to file
        with client.audio.speech.with_streaming_response.create(
                    model=model_deployment_tts,
                    voice="rio",
                    input="Vai Corinthians",
                    instructions="Fale com sotaque carioca",
                ) as response:
            response.stream_to_file(speech_file_path)
                


        # Play the generated speech file
        playsound(speech_file_path)
        
        # Call model to transcribe audio file
        audio_file = open(speech_file_path, "rb")
        transcription = client.audio.transcriptions.create(
            model=model_deployment_transcribe,
            file=audio_file,
            response_format="text"
        )
            
        print(transcription)
            




    except Exception as ex:
        print(ex)


if __name__ == "__main__":
    main()