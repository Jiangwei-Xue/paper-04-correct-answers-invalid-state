#!/usr/bin/env python3
"""Check agreement between public citation, paper identity, and release docs."""
from pathlib import Path
import argparse
import json
import re

ROOT = Path(__file__).resolve().parents[1]
DOI = '10.5281/zenodo.22720976'
URL = 'https://github.com/Jiangwei-Xue/paper-04-correct-answers-invalid-state'

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--archive', required=True, type=Path)
    args = parser.parse_args()
    assert args.archive.is_file(), 'Archive file is unavailable'
    meta = json.loads((ROOT / 'LATEST_PAPER.json').read_text())
    status = json.loads((ROOT / 'PUBLIC_RELEASE_STATUS.json').read_text())
    assert meta['doi'] == DOI
    assert meta['reproducibility_repository'] == URL
    assert meta['authors'] == ['Jiangwei Xue', 'Zhida Qin', 'Yuda Bi']
    assert meta['corresponding_author'] == 'Yuda Bi'
    assert meta['paper_license'] == 'CC-BY-4.0'
    assert meta['reproduction_release'] == status['release_id']
    assert meta['paper_bundled_in_experiment_archive'] is False
    for rel in ['README.md', 'CITATION.cff', 'docs/PAPER_RESULTS_MAP.md']:
        text = (ROOT / rel).read_text()
        assert DOI in text and URL in text, rel
        assert '[PUBLIC ARTIFACT URL]' not in text, rel
    for item in meta['paper_files']:
        assert re.fullmatch(r'[0-9a-f]{64}', item['sha256'])
        assert not Path(item['path']).is_absolute()
    assert 'No single license' in (ROOT / 'LICENSE').read_text()
    assert meta['primary_results']['rows'] == 7200
    assert meta['primary_results']['final_answer_success'] == 696
    assert meta['primary_results']['answer_aligned_validity'] == 180
    assert meta['primary_results']['joint_success'] == 173
    print('PUBLICATION_METADATA_PASS')

if __name__ == '__main__':
    main()
