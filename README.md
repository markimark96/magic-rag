# Magic RAG

## Introduction

Magic RAG is a Retrieval-Augmented Generation (RAG) application designed to answer questions about the card game Magic: The Gathering. This application combines the power of large language models with specialized knowledge retrieval to provide accurate and contextually relevant answers to MTG rules questions, card interactions, and gameplay scenarios.
It uses ElasticSearch both for storing card data for full text search as well as some forum entries and rules for vector search.

## Configuration

### Dependencies

The dependencies can be found in the requirements.txt file.

### AWS Bedrock
If you need help accessing AWS Bedrock you can find it [here](https://docs.aws.amazon.com/bedrock/latest/userguide/getting-started.html). The prompt was tested with *anthropic.claude-instant-v1* but theoretically the software is functional with any foundational model. Small changes in the prompt or the call to Bedrock might be needed if using a different model though. 

### Elastic search

You will need a running Elasticsearch instance that is accessible by this application. It requires the following three indices:

- **Card Index:** Should contain the full card database downloaded from Scryfall
- **Rules Index:** Should contain the comprehensive rules of MTG, with each rule stored separately as a vector. Use the same embedding method as in this application.
- **Forum Entries Index:** Should contain MTG-related questions and answers from forums, stored as vectors using the same embedding method as in this application.

### Environment variables

Create a `.env` file with the following variables:

```
ES_USERNAME="<your_elasticsearch_username>"
ES_PASSWORD="<your_elasticsearch_password>"
ES_URI="<your_elasticsearch_uri>"
ES_CARD_INDEX="<card_index_name>"
ES_RULE_INDEX="<rules_index_name>"
ES_QUESTION_INDEX="<qa_index_name>"
AWS_ACCES_KEY="<your_aws_access_key>"
AWS_SECRET="<your_aws_secret_key>"
AWS_REGION="<aws_region>"
LLM_MODEL_ID="<bedrock_model_id>"
```

## Usage

### Starting up

The software is usable through a simple API. It can be run with the following command:
`uvicorn main:app --reload`
This will spin up the server on port *8000* by default.

### Calling the API endpoint

The primary endpoint is `/answer`, which accepts Magic: The Gathering questions and returns comprehensive answers. 

**Important:** When referencing card names in your question, use the full and exact card name for proper recognition. The system will attempt to match card names in your query against the database.

**Example Request:**
```bash
curl --location 'http://127.0.0.1:8000/answer' \
--header 'Content-Type: application/json' \
--data '{
    "question" : "What happens if I play an Urborg, Tomb of Yawgmoth while my opponent has a Blood Moon on the battlefield?"
}'
```

The API will return a JSON object containing the answer to your question based on card details, rulings, and relevant MTG rules.

**Example Response:**
```json
{
    "answer": " Based on the rules and rulings provided, here is what would happen if you play an Urborg, Tomb of Yawgmoth while your opponent has a Blood Moon on the battlefield:\n\n- Blood Moon is currently turning all nonbasic lands into Mountains. This means they lose all other land types and abilities, and gain only the land type Mountain and the ability \"{T}: Add {R}\".\n\n- Urborg's ability is to make all lands also have the land type Swamp in addition to their other types. \n\n- However, with Blood Moon on the battlefield, nonbasic lands no longer have any other land types - they are just Mountains.\n\n- Therefore, when Urborg enters the battlefield, it will not be able to apply its effect of making other lands also Swamps, since those lands already just have the single land type Mountain due to Blood Moon. \n\n- The lands will remain Mountains and not gain the land type Swamp or ability \"{T}: Add {B}\".\n\nSo in summary, with Blood Moon on the battlefield, Urborg's ability will not be able to make any other lands also Swamps. The lands will remain Mountains only."
}
```
