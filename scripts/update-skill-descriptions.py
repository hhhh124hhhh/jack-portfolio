#!/usr/bin/env python3
"""
Update skill descriptions based on SKILL.md content.
"""

import re
from pathlib import Path

# Skills to update (name -> improved description)
DESCRIPTION_UPDATES = {
    "reddit-job-posting-templates": "Templates for job postings and hiring requests on Reddit. Use when posting job opportunities, looking for work, or creating standardized hiring templates for professional communities.",
    "google-imagen-3-portrait-photography": "Generate professional portrait photography using Google Imagen 3. Use when creating realistic portraits, headshots, or artistic character photography with professional lighting and composition.",
    "sora-2-futuristic-tech-showcase": "Create futuristic technology showcase videos using OpenAI Sora 2. Use when generating concept videos for AI technology demonstrations, futuristic product showcases, or sci-fi visualizations.",
    "google-imagen-3-hyperrealistic-landscape": "Generate hyperrealistic landscape photography using Google Imagen 3. Use when creating breathtaking natural scenes, landscapes, and nature photography with exceptional detail and realism.",
    "google-veo-dynamic-city-nightview": "Create dynamic city night view videos using Google Veo. Use when generating cinematic urban scenes, futuristic cityscapes, or nighttime urban video content.",
    "sora-2-nature-documentary": "Create nature documentary videos using OpenAI Sora 2. Use when generating wildlife footage, nature scenes, or educational documentary-style videos with cinematic quality.",
    "sora-2-superhero-movie": "Create superhero movie-style videos using OpenAI Sora 2. Use when generating action sequences, superhero visual effects, or cinematic scenes inspired by comic book movies.",
    "gaussian-process-mlp-hybrid": "Discussion on Gaussian Process and MLP hybrid models for uncertainty estimation. Use when exploring machine learning model architectures, uncertainty quantification, or ensemble methods for drug discovery and similar applications.",
    "self-taught-ml-career-path": "Discussion about self-taught machine learning career paths and success stories. Use when exploring alternative education paths, self-study strategies, or career development in ML without formal PhD training.",
    "langchain-chat-prompt-template": "Guide to using ChatPromptTemplate and MessagesPlaceholder in LangChain for conversational AI. Use when building chatbots, conversational interfaces, or AI assistants that need to maintain conversation history.",
    "reddit-nlp-research-problems": "Discussion on important NLP research problems in academia and industry. Use when exploring current challenges in natural language processing, low-resource language models, or conversational AI research directions.",
    "akkadian-noun-analyzer": "Akkadian noun analyzer using regex-based feature extraction. Use when working with ancient languages, linguistic analysis, or building morphological analyzers for historical languages.",
    "ai-portrait-generator": "Generate AI-powered portrait images using various models and techniques. Use when creating character portraits, avatars, or stylized portrait images.",
    "prompt-from-lexx-aura": "AI prompt template converted from a Twitter post. Use when creating AI prompts for specific tasks or exploring prompt engineering techniques.",
    "ai-from-trueslazac": "AI content from TrueSlazac Twitter account. Use when accessing AI-related prompts, templates, or discussions from social media sources.",
}

BASE_DIR = Path("/root/clawd/generated-skills")


def update_description(skill_name, new_description):
    """Update the description in SKILL.md."""
    skill_dir = BASE_DIR / skill_name
    skill_md_path = skill_dir / "SKILL.md"

    if not skill_md_path.exists():
        print(f"  ✗ SKILL.md not found for {skill_name}")
        return False

    with open(skill_md_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Find and replace the description
    pattern = r"description:.*"
    replacement = f"description: {new_description}"

    new_content = re.sub(pattern, replacement, content, count=1)

    if new_content == content:
        print(f"  ⊙ No change needed for {skill_name}")
        return True

    with open(skill_md_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"  ✓ Updated description for {skill_name}")
    return True


def main():
    print("=" * 60)
    print("UPDATING SKILL DESCRIPTIONS")
    print("=" * 60)
    print()

    updated = 0
    unchanged = 0

    for skill_name, description in DESCRIPTION_UPDATES.items():
        if update_description(skill_name, description):
            updated += 1
        else:
            unchanged += 1

    print("\n" + "=" * 60)
    print(f"Updated: {updated}")
    print(f"Unchanged: {unchanged}")
    print("Done!")


if __name__ == "__main__":
    main()
