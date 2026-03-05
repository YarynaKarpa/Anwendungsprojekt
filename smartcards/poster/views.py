import json
import re
from django.db import transaction
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from .forms import TXTUploadForm
from .models import PosterCard

PAIR_RE = re.compile(
    r"<question>\s*(.*?)\s*</>\s*<answer>\s*(.*?)\s*</>",
    re.IGNORECASE | re.DOTALL
)

def _parse_txt(file) -> list[tuple[str, str]]:
    """Parse uploaded TXT into a list of (question, answer) tuples."""
    raw = file.read()
    if isinstance(raw, bytes):
        text = raw.decode("utf-8", errors="ignore")
    else:
        text = str(raw)

    pairs: list[tuple[str, str]] = []
    for q, a in PAIR_RE.findall(text):
        q_clean = (q or "").strip()
        a_clean = (a or "").strip()
        if q_clean or a_clean:
            pairs.append((q_clean, a_clean))
    return pairs

@require_http_methods(["GET", "POST"])
def index(request):
    """
    Upload a TXT file, set a single Subject, parse pairs, save to DB (PosterCard),
    and show a preview + JSON.
    """
    form = TXTUploadForm()
    error = None
    saved_count = 0
    # For preview/JSON on the page (not necessarily all DB rows)
    cards_preview = []

    if request.method == "POST":
        form = TXTUploadForm(request.POST, request.FILES)
        if form.is_valid():
            subject = form.cleaned_data["subject"].strip()
            file = form.cleaned_data["txt"]

            try:
                pairs = _parse_txt(file)
                if not pairs:
                    error = "No <question></> / <answer></> pairs found."
                else:
                    # Build preview + JSON-compatible structure
                    cards_preview = [
                        {
                            "subject": subject,
                            "type": "text",
                            "question": q,
                            "options": [],
                            "correct": [],
                            "expected": a,
                        }
                        for (q, a) in pairs
                    ]

                    # Save to DB in one transaction (bulk)
                    with transaction.atomic():
                        objs = [PosterCard(subject=subject, question=q, answer=a) for (q, a) in pairs]
                        PosterCard.objects.bulk_create(objs)
                        saved_count = len(objs)

            except Exception as e:
                error = f"Failed to parse/save TXT: {e}"
        else:
            error = "Please fix the errors below."

    return render(request, "poster/index.html", {
        "form": form,
        "error": error,
        "saved_count": saved_count,
        "cards": cards_preview,
        "cards_json": json.dumps(cards_preview, indent=2, ensure_ascii=False) if cards_preview else "",
    })
