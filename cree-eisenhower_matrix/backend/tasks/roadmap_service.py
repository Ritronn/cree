"""
Roadmap service integrating roadmap.sh data from GitHub + Groq AI for custom paths.

Fetches available roadmaps from the kamranahmedse/developer-roadmap GitHub repo,
and uses Groq AI to generate custom learning paths between topics.
"""
import os
import json
import logging
import requests

logger = logging.getLogger(__name__)

# Cache the roadmap list so we don't hit GitHub API every time
_ROADMAP_CACHE = None

GITHUB_ROADMAPS_URL = (
    "https://api.github.com/repos/kamranahmedse/developer-roadmap"
    "/contents/src/data/roadmaps"
)

# Map of common roadmap slugs to display names
POPULAR_ROADMAPS = {
    'python': 'Python Developer',
    'javascript': 'JavaScript Developer',
    'react': 'React Developer',
    'angular': 'Angular Developer',
    'vue': 'Vue Developer',
    'nodejs': 'Node.js Developer',
    'typescript': 'TypeScript Developer',
    'java': 'Java Developer',
    'cpp': 'C++ Developer',
    'golang': 'Go Developer',
    'rust': 'Rust Developer',
    'frontend': 'Frontend Developer',
    'backend': 'Backend Developer',
    'full-stack': 'Full Stack Developer',
    'devops': 'DevOps Engineer',
    'android': 'Android Developer',
    'ios': 'iOS Developer',
    'flutter': 'Flutter Developer',
    'machine-learning': 'Machine Learning Engineer',
    'ai-engineer': 'AI Engineer',
    'ai-data-scientist': 'AI Data Scientist',
    'cyber-security': 'Cyber Security',
    'blockchain': 'Blockchain Developer',
    'postgresql-dba': 'PostgreSQL DBA',
    'sql': 'SQL',
    'docker': 'Docker',
    'kubernetes': 'Kubernetes',
    'aws': 'AWS',
    'linux': 'Linux',
    'git-github': 'Git & GitHub',
    'system-design': 'System Design',
    'software-architect': 'Software Architect',
    'datastructures-and-algorithms': 'DSA',
    'computer-science': 'Computer Science',
    'mongodb': 'MongoDB',
    'redis': 'Redis',
    'graphql': 'GraphQL',
    'spring-boot': 'Spring Boot',
    'django': 'Django',
    'laravel': 'Laravel',
    'nextjs': 'Next.js',
    'kotlin': 'Kotlin',
    'php': 'PHP',
    'ruby': 'Ruby',
    'prompt-engineering': 'Prompt Engineering',
    'api-design': 'API Design',
    'mlops': 'MLOps',
    'terraform': 'Terraform',
    'qa': 'QA Engineer',
    'ux-design': 'UX Design',
    'data-analyst': 'Data Analyst',
    'data-engineer': 'Data Engineer',
}


def get_available_roadmaps():
    """
    Return list of available roadmap.sh roadmaps.
    Uses cached data or falls back to hardcoded popular list.
    """
    global _ROADMAP_CACHE
    if _ROADMAP_CACHE:
        return _ROADMAP_CACHE

    try:
        resp = requests.get(GITHUB_ROADMAPS_URL, timeout=5, headers={
            'Accept': 'application/vnd.github.v3+json',
        })
        if resp.status_code == 200:
            data = resp.json()
            roadmaps = []
            for item in data:
                if item.get('type') == 'dir':
                    slug = item['name']
                    display_name = POPULAR_ROADMAPS.get(
                        slug,
                        slug.replace('-', ' ').title()
                    )
                    roadmaps.append({
                        'slug': slug,
                        'name': display_name,
                        'url': f'https://roadmap.sh/{slug}',
                    })
            _ROADMAP_CACHE = roadmaps
            return roadmaps
    except Exception as e:
        logger.warning(f"Failed to fetch roadmaps from GitHub: {e}")

    # Fallback to hardcoded list
    return [
        {'slug': slug, 'name': name, 'url': f'https://roadmap.sh/{slug}'}
        for slug, name in POPULAR_ROADMAPS.items()
    ]


def get_roadmap_data(slug):
    """
    Fetch the raw JSON roadmap data from the kamranahmedse/developer-roadmap GitHub repo.
    This bypasses the blocked iframe issue by allowing native rendering.
    """
    # map slug to the actual JSON file name if it differs, usually it matches the slug
    raw_url = f"https://raw.githubusercontent.com/kamranahmedse/developer-roadmap/master/src/data/roadmaps/{slug}/{slug}.json"
    try:
        resp = requests.get(raw_url, timeout=5)
        if resp.status_code == 200:
            return resp.json()
    except Exception as e:
        logger.error(f"Failed to fetch native roadmap data for {slug}: {e}")
    return None


def generate_custom_roadmap(from_topic, to_topic):
    """
    Use Groq AI to generate a custom learning roadmap from one topic to another.
    Returns a structured dict with phases and milestones.
    """
    groq_api_key = os.getenv('GROQ_API_KEY', '').strip()
    if not groq_api_key or groq_api_key == 'your-groq-api-key-here':
        return _fallback_roadmap(from_topic, to_topic)

    try:
        from groq import Groq
        client = Groq(api_key=groq_api_key)

        prompt = f"""You are an expert educator and learning path designer. Create a detailed learning roadmap for someone going from "{from_topic}" to "{to_topic}".

Structure the roadmap as phases with clear milestones. Each phase should have:
- A title
- A list of topics to learn (3-6 topics per phase)
- Each topic should have a brief description and estimated study hours
- Related roadmap.sh URL if applicable (format: https://roadmap.sh/slug)

Respond ONLY with valid JSON:
{{
  "title": "From {from_topic} to {to_topic}",
  "description": "Brief overview of the learning journey",
  "total_estimated_hours": number,
  "phases": [
    {{
      "phase_number": 1,
      "title": "Phase title",
      "description": "What you'll learn in this phase",
      "topics": [
        {{
          "name": "Topic name",
          "description": "Brief description",
          "estimated_hours": number,
          "roadmap_url": "https://roadmap.sh/slug or null"
        }}
      ]
    }}
  ]
}}

Create 4-8 phases covering the complete journey. Be specific and practical."""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a learning path designer. Always respond with valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=2000,
        )

        content = response.choices[0].message.content.strip()
        # Strip markdown code fences if present
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        content = content.strip()

        result = json.loads(content)
        result['source'] = 'groq_ai'
        return result

    except json.JSONDecodeError as e:
        logger.warning(f"Groq returned invalid JSON for roadmap: {e}")
        return _fallback_roadmap(from_topic, to_topic)
    except Exception as e:
        logger.warning(f"Groq roadmap generation failed: {e}")
        return _fallback_roadmap(from_topic, to_topic)


def _fallback_roadmap(from_topic, to_topic):
    """Simple fallback roadmap when Groq is unavailable."""
    return {
        'title': f'From {from_topic} to {to_topic}',
        'description': f'A learning path from {from_topic} to {to_topic}. '
                       f'AI generation unavailable — showing a basic roadmap.',
        'total_estimated_hours': 100,
        'source': 'fallback',
        'phases': [
            {
                'phase_number': 1,
                'title': f'Master {from_topic} Fundamentals',
                'description': f'Build a solid foundation in {from_topic}',
                'topics': [
                    {'name': f'{from_topic} Basics', 'description': 'Core concepts and syntax', 'estimated_hours': 15, 'roadmap_url': None},
                    {'name': f'{from_topic} Intermediate', 'description': 'Advanced patterns and practices', 'estimated_hours': 20, 'roadmap_url': None},
                ]
            },
            {
                'phase_number': 2,
                'title': 'Bridge Concepts',
                'description': f'Connecting {from_topic} knowledge to {to_topic}',
                'topics': [
                    {'name': 'Prerequisites', 'description': f'Key concepts needed before diving into {to_topic}', 'estimated_hours': 15, 'roadmap_url': None},
                    {'name': 'Tools & Setup', 'description': 'Set up your development environment', 'estimated_hours': 5, 'roadmap_url': None},
                ]
            },
            {
                'phase_number': 3,
                'title': f'Learn {to_topic}',
                'description': f'Dive deep into {to_topic}',
                'topics': [
                    {'name': f'{to_topic} Fundamentals', 'description': 'Core theory and concepts', 'estimated_hours': 20, 'roadmap_url': None},
                    {'name': f'{to_topic} Hands-on', 'description': 'Practical projects and exercises', 'estimated_hours': 25, 'roadmap_url': None},
                ]
            },
        ],
    }
