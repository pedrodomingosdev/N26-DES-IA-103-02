import asyncio
import os
from typing import cast
from dotenv import load_dotenv

# Add references
from agent_framework import Message
from agent_framework.foundry import FoundryChatClient
from agent_framework.orchestrations import SequentialBuilder
from azure.identity import AzureCliCredential


load_dotenv()

async def main():
    # Agent instructions
    summarizer_instructions = """
    Resuma o feedback do cliente em uma única frase curta. Mantenha um tom neutro e conciso.
    Exemplo de saída:
    O aplicativo trava durante o envio de fotos.
    O usuário elogia o recurso de modo escuro.
    """

    classifier_instructions = """
    Classifique o feedback como uma das seguintes opções: Positivo, Negativo ou Solicitação de funcionalidade.
    """

    action_instructions = """
    Com base no resumo e na classificação, sugira a próxima ação em uma única frase curta.
    Exemplo de saída:
    Encaminhar como um bug de alta prioridade para a equipe de dispositivos móveis.
    Registrar como feedback positivo para compartilhar com as equipes de design e marketing.
    Registrar como solicitação de melhoria para o backlog do produto.
    """

    # Create the chat client
    credential = AzureCliCredential()
    chat_client = FoundryChatClient(
        credential=credential,
        project_endpoint=os.getenv("AZURE_AI_PROJECT_ENDPOINT"),
        model=os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME"),
    )


    # Create agents
    summarizer_agent = chat_client.as_agent(
        name="summarizer",
        instructions=summarizer_instructions,
    )

    classifier_agent = chat_client.as_agent(
        name="classifier",
        instructions=classifier_instructions,
    )

    action_agent = chat_client.as_agent(
        name="action",
        instructions=action_instructions,
    )


   # Initialize the current feedback
    feedback = """
    Entrei em contato com o suporte ao cliente ontem porque não conseguia acessar minha conta. O atendente respondeu quase que imediatamente, foi educado e profissional, e resolveu o problema em poucos minutos. Sinceramente, foi uma das melhores experiências de suporte que já tive.
    """


    # Build sequential orchestration
    workflow = SequentialBuilder(
        participants=[summarizer_agent, classifier_agent, action_agent],
        output_from="all",
    ).build()


    # Run and collect outputs
    result = await workflow.run(f"Customer feedback: {feedback}")
    outputs = result.get_outputs()

    # Display outputs
    i = 1
    for response in outputs:
        for msg in cast(list[Message], response.messages):
            name = msg.author_name or ("assistant" if msg.role == "assistant" else "user")
            print(f"{'-' * 60}\n{i:02d} [{name}]\n{msg.text}")
            i += 1
    
    
if __name__ == "__main__":
    asyncio.run(main())