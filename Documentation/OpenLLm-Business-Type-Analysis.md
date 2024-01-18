<!--
SPDX-License-Identifier: MIT
SPDX-FileCopyrightText: 2024 Ruchita Nathani <ruchita.nathani@fau.de>
-->

# Business Type Analysis: Research and Proposed Solution

## Research

**1. Open-source LLM Model :**
I explored an open-source LLM model named CrystalChat available on Hugging Face (https://huggingface.co/LLM360/CrystalChat). Despite its capabilities, it has some limitations:

- **Computational Intensity:** CrystalChat is computationally heavy and cannot be run efficiently on local machines.

- **Infrastructure Constraints:** Running the model on Colab, although feasible, faces GPU limitations.

**2. OpenAI as an Alternative :**
Given the challenges with the open LLM model, OpenAI's GPT models provide a viable solution. While GPT is known for its computational costs, it offers unparalleled language understanding and generation capabilities.

## Proposed Solution

Considering the limitations of CrystalChat and the potential infrastructure costs associated with running an open LLM model on local machines, I propose the following solution:

1. **Utilize OpenAI Models:** Leverage OpenAI models, which are known for their robust language capabilities.

2. **Manage Costs:** Acknowledge the computational costs associated with GPT models and explore efficient usage options, such as optimizing queries or using cost-effective computing environments.

3. **Experiment with CrystalChat on AWS SageMaker:** As part of due diligence, consider executing CrystalChat on AWS SageMaker to evaluate its performance and potential integration.

4. **Decision Making:** After the experimentation phase, evaluate the performance, costs, and feasibility of both OpenAI and CrystalChat. Make an informed decision based on the achieved results.

## Conclusion

Leveraging OpenAI's GPT models offers advanced language understanding. To explore the potential of open-source LLM models, an experiment with CrystalChat on AWS SageMaker is suggested before making a final decision.
