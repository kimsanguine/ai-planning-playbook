"""Check learner-source preservation, local links and committed build artifacts."""
from pathlib import Path
from urllib.parse import unquote, urlsplit
import argparse
import hashlib
import json
import re

from public_files import manifest_files, public_inputs

ROOT = Path(__file__).resolve().parents[1]
PROSE_SHA256 = '0529d3e9c1f97b7b892937f356da17306d39994bb3a04915ea978b04659ab125'
PROMPTS_SHA256 = '49aaacc1f5b5797694ba8109dda7f18089c9d4e347441b9b3f500a57a8607579'


def digest(text):
    return hashlib.sha256(text.encode()).hexdigest()


def validate(artifacts=False):
    errors = []
    manuscript = (ROOT / 'manuscript/README.md').read_text()
    prose = re.sub(r'\]\([^)]+\)', '](LINK)', manuscript)
    prompts = re.findall(r'```text\n(.*?)\n```', manuscript, re.S)
    slugs = re.findall(r'<!-- page: ([a-z0-9-]+) -->', manuscript)
    if digest(prose) != PROSE_SHA256:
        errors.append('Approved manuscript prose changed; review the diff before updating its baseline.')
    if digest('\n'.join(prompts)) != PROMPTS_SHA256 or len(prompts) != 20:
        errors.append('Expected the 10 unchanged prompt pairs.')
    if len(slugs) != 28 or len(set(slugs)) != 28:
        errors.append('Expected 28 distinct chapter slugs.')
    expected_documents = {'customer.md', 'prd.md', 'architecture.md', 'design.md', 'progress.md'}
    if {p.name for p in public_inputs(ROOT) if p.parent == ROOT / 'templates' and p.is_file()} != expected_documents:
        errors.append('templates: expected exactly five project documents.')
    if {p.name for p in public_inputs(ROOT) if p.parent == ROOT / 'examples/video-localization' and p.is_file()} != {'customer.md', 'prd.md', 'architecture.md', 'progress.md'}:
        errors.append('examples/video-localization: expected exactly four comparison documents.')
    skill = ROOT / 'skills/ai-project-planning'
    skill_manifest = skill / 'SKILL.md'
    if not skill_manifest.is_file():
        errors.append('skills/ai-project-planning: missing SKILL.md.')
    else:
        manifest = skill_manifest.read_text()
        if not re.match(r'^---\nname: ai-project-planning\ndescription: .+\n---\n', manifest):
            errors.append('skills/ai-project-planning: invalid SKILL.md front matter.')
    if {p.name for p in (skill / 'assets/templates').glob('*.md')} != expected_documents:
        errors.append('skills/ai-project-planning: expected five bundled template documents.')
    md_files = [p for p in public_inputs(ROOT) if p.suffix == '.md']
    count = 0
    for path in md_files:
        content = path.read_text()
        name = str(path.relative_to(ROOT))
        if len(re.findall(r'^```', content, re.M)) % 2:
            errors.append(f'{name}: unclosed fenced block.')
        if re.search(r'/Users/|/home/[^ /]+/|sk-(?:proj-)?[A-Za-z0-9_-]{16,}|notion\.so|\.worktrees/|QA.{0,10}(?:점수|score)|~~', content, re.I):
            errors.append(f'{name}: private-path, credential, internal-score or strikethrough pattern.')
        for href in re.findall(r'\]\(([^)]+)\)', content):
            count += 1
            url = urlsplit(href)
            if url.scheme or url.netloc:
                if url.scheme not in ('https', 'mailto'):
                    errors.append(f'{name}: unsupported scheme: {href}')
                if url.path.startswith('/playbook/ai-planning/') and url.hostname == 'habix.ai' and url.path.rsplit('/', 1)[-1] not in slugs:
                    errors.append(f'{name}: unknown public chapter slug: {href}')
                continue
            if url.path.startswith('/'):
                errors.append(f'{name}: root-relative link fails on GitHub: {href}')
                continue
            target = (path.parent / unquote(url.path)).resolve() if url.path else path
            if not target.is_relative_to(ROOT) or not target.exists():
                errors.append(f'{name}: missing local target: {href}')
            if url.fragment and target.is_file() and target.suffix == '.md':
                target_text = target.read_text()
                explicit_ids = re.findall(r'id="([^"]+)"', target_text)
                heading_ids = [re.sub(r'[^\w\s-]', '', h.lower()).replace(' ', '-') for h in re.findall(r'^#+ (.+)$', target_text, re.M)]
                if unquote(url.fragment) not in explicit_ids + heading_ids:
                    errors.append(f'{name}: missing local anchor: {href}')
    for name in ('handbook.html', 'planning-method-kit.zip'):
        if (ROOT / name).exists():
            errors.append(f'Unexpected legacy artifact: {name}')
    if artifacts:
        import fitz
        manifest = json.loads((ROOT / 'dist/build-manifest.json').read_text())
        expected_names = {str(p.relative_to(ROOT)) for p in manifest_files(ROOT)}
        if set(manifest['files']) != expected_names:
            errors.append('Build manifest file list differs from the public allowlist.')
        for name in sorted(expected_names & set(manifest['files'])):
            expected = manifest['files'][name]
            p = ROOT / name
            if not p.is_file() or p.stat().st_size != expected['bytes'] or hashlib.sha256(p.read_bytes()).hexdigest() != expected['sha256']:
                errors.append(f'Build manifest does not match: {name}')
        chapters = json.loads((ROOT / 'dist/chapters.json').read_text())['chapters']
        if [c['slug'] for c in chapters] != slugs or [c['number'] for c in chapters] != list(range(1, 29)):
            errors.append('Exported chapter order differs from manuscript.')
        if len(manifest['pdf_pages']) != 28 or any(p['scale'] != 1 or p['spare_points'] < 0 for p in manifest['pdf_pages']):
            errors.append('PDF layout must preserve all pages at scale 1.')
        with fitz.open(ROOT / 'dist/handbook.pdf') as pdf:
            if len(pdf) != 28:
                errors.append('PDF must have 28 pages.')
            for chapter, page in zip(chapters, pdf):
                text = ''.join(page.get_text().split())
                if ''.join(chapter['title'].split()) not in text:
                    errors.append(f'PDF title not extractable: {chapter["slug"]}')
                for href in re.findall(r'href="([^"]+)"', chapter['html']):
                    if not href.startswith(('https://', '#')):
                        errors.append(f'Unresolved exported link: {href}')
    if errors:
        raise SystemExit('\n'.join(errors))
    print(json.dumps({'markdown_files': len(md_files), 'links_checked': count, 'chapters': len(slugs), 'prompt_pairs': len(prompts) // 2, 'artifacts_checked': artifacts}, ensure_ascii=False))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--artifacts', action='store_true')
    validate(parser.parse_args().artifacts)
