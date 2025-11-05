import json
from pathlib import Path

segments = json.loads(Path('segments.json').read_text())
terms = json.loads(Path('terms.json').read_text())
predicates = json.loads(Path('predicates.json').read_text())
facts = json.loads(Path('facts.json').read_text())
lexicon = json.loads(Path('lexicon.json').read_text())
links = json.loads(Path('links.json').read_text())

data = {
    "schema_version": "norm-core.v2",
    "jurisdiction": "RU",
    "source_meta": {
        "code": "KONST",
        "edition_date": "2020-10-12",
        "scope": "Конституция РФ, Раздел I, главы 1–3"
    },
    "segments": segments,
    "terms": terms,
    "predicates": predicates,
    "facts": facts,
    "lexicon": lexicon,
    "links": links,
    "open_questions": []
}

Path('outputs/norm_core_konst_gl1-2.json').write_text(json.dumps(data, ensure_ascii=False, indent=2))
