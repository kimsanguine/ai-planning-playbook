"""The exact public inputs shared by building and validation."""
from pathlib import Path

PUBLIC_INPUTS = (
    '.gitattributes',
    '.github/workflows/validate.yml',
    '.gitignore',
    'CHANGELOG.md',
    'CONTRIBUTING.md',
    'LICENSE',
    'README.md',
    'assets/fonts/OFL.txt',
    'assets/fonts/PretendardVariable.ttf',
    'assets/fonts/README.md',
    'assets/planning-method.svg',
    'assets/thinking-flow.svg',
    'cases/01-request-to-problem.md',
    'cases/02-quality-and-cost.md',
    'cases/03-ux-priorities.md',
    'docs/decision-checklist.md',
    'docs/hplan-guide.md',
    'docs/instruction-practice.md',
    'docs/planner-scope-appendix.md',
    'docs/planner-thinking-method.md',
    'examples/video-localization/architecture.md',
    'examples/video-localization/customer.md',
    'examples/video-localization/prd.md',
    'examples/video-localization/progress.md',
    'manuscript/README.md',
    'requirements.txt',
    'scripts/build.py',
    'scripts/public_files.py',
    'scripts/validate.py',
    'templates/architecture.md',
    'templates/customer.md',
    'templates/design.md',
    'templates/prd.md',
    'templates/progress.md',
    'skills/ai-project-planning/SKILL.md',
    'skills/ai-project-planning/assets/templates/architecture.md',
    'skills/ai-project-planning/assets/templates/customer.md',
    'skills/ai-project-planning/assets/templates/design.md',
    'skills/ai-project-planning/assets/templates/prd.md',
    'skills/ai-project-planning/assets/templates/progress.md',
)
PUBLIC_OUTPUTS = ('dist/handbook.pdf', 'dist/chapters.json')


def public_inputs(root: Path):
    return [root / name for name in PUBLIC_INPUTS]


def manifest_files(root: Path):
    return public_inputs(root) + [root / name for name in PUBLIC_OUTPUTS]
