# Footway Challenge - Polly Optimization

Thank you for taking the time to complete this coding challenge!

*(LLM-friendly Markdown version to paste into your LLM of choice)*

## Glossary

**Polly**: The LLM-powered assistant for human customer support agents

**Knowledge tree**: A JSON file consisting of attributes (keywords, examples) for each category (e.g., RETURN, CLAIM) and instructions for each category

**Promptlayer**: A version control system we use for prompts used by Polly

## Background

At Footway, we have an assistant for customer support agents to help them compose better replies to end customers faster. Polly (think Cursor or Claude Code, but for customer support agents, and slightly worse) consists of:
- An API to receive webhooks from the CRM system when we receive emails from customers
- An interface that exposes the produced reply to end users via a Chrome extension client
- A job to extract metrics from logged runs

### Polly's Workflow

When Polly receives a webhook for an incoming email, it will:
1. Clean the email
2. Classify the email by category based on the knowledge tree
3. Execute tools if needed and compose a reply to the customer based on the instruction in the knowledge tree

## The Problem

Currently, we rely on a human to maintain the knowledge tree for Polly in JSON format. The human agent tasked with this responsibility observes the replies Polly produces and attempts to fine-tune the knowledge tree. They then run evaluations on the new version of the knowledge tree against a pre-defined dataset collected from earlier runs in Promptlayer.

This approach works (at least for now), but it's not very scalable due to:
1. Hard dependency on the human who fine-tunes the knowledge tree
2. Human subjectivity in fine-tuning, which can result in inconsistent results

## Our Vision

We envision an automatic optimization flow where a system could:
- Take the final reply the human made
- Based on that, perform systematic optimization on the prompt/knowledge tree
- Run evaluations automatically
- Calculate the loss and follow a gradient descent approach until we find the optimal point

## The Challenge

In this challenge, we will provide the knowledge tree and a set of runs. We would like you to create a proof of concept demonstrating how such a systematic optimization system would look.

It doesn't need to be fully implemented (otherwise we wouldn't need you!), but we'd like to see how you would approach this problem. Please conduct research and identify the appropriate tools/workflow based on your research and findings.

Please reach out to me if you need OpenAI/Anthropic API keys.

---

# Dataset Structure Documentation

## Knowledge Tree Structure

The knowledge tree is a hierarchical JSON structure that defines categories for customer support classification and responses.

### Schema Overview

```json
{
  "CATEGORY_NAME": {
    "name": "string",
    "description": "string", 
    "keywords": ["array", "of", "strings"],
    "examples": ["array", "of", "example", "emails"],
    "instruction": "string with response instructions",
    "sub_categories": {
      // Nested subcategory structure (same schema)
    }
  }
}
```

### Field Definitions

**name**: The category identifier (matches the key)

**description**: Detailed explanation of when to use this category, including what belongs and what doesn't

**keywords**: Array of relevant terms that indicate this category (used for classification)

**examples**: Array of real customer email examples that belong to this category

**instruction**: Template instructions for how customer support agents should respond to emails in this category

**sub_categories**: Optional nested object containing subcategories with the same structure

### Category Hierarchy Example

```
COMPLAINT
├── PROOF_COMPLAINT (has attachments/images)
└── NO_PROOF (initial complaint without evidence)
```

## Runs Dataset Structure

The "runs" dataset contains logged interactions between customers and the Polly system.

### Run Record Schema

```json
{
  "logno": "string",           // Unique log identifier
  "tickno": "string",          // Ticket number from CRM
  "incoming_email": "string",  // Full customer email content
  "llm_reply": "string",       // Polly's generated response
  "human_reply": "string",     // Final response sent by human agent
  "score": "number",           // Quality score (0-1, lower = worse)
  "category": "string",        // Classified category
  "improved_ts": "timestamp",  // When human improved the response
  "final_ts": "timestamp",     // When final response was sent
  "detected_language": "string" // ISO language code
}
```

### Field Definitions

**logno**: Unique identifier for each interaction log

**tickno**: Customer service ticket number from the CRM system

**incoming_email**: The complete customer email including subject, body, and metadata. Contains anonymized placeholders like [COMPANY], [NAME], [EMAIL], etc.

**llm_reply**: The response that Polly (LLM) initially generated

**human_reply**: The final response that the human customer support agent actually sent to the customer

**score**: A quality metric (0.0 to 1.0) currently generated by the ROUGE-L algorithm, where lower scores indicate the LLM response was further from the ideal human response

**category**: The knowledge tree category that was applied to classify this email

**improved_ts**: Timestamp when the human agent modified/improved the LLM response

**final_ts**: Timestamp when the final response was sent to the customer

**detected_language**: The detected language of the customer email (e.g., "cs" for Czech)