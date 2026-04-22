from django.shortcuts import render, redirect
from django.db.models import Count
from poster.models import PosterCard
from urllib.parse import unquote

SESSION_KEYS = ["study_subject", "study_order", "study_index", "study_revealed", "total_correct", "total_wrong"]

def _reset_session(request):
    for k in SESSION_KEYS:
        request.session.pop(k, None)
    request.session.modified = True

def menu(request):
    subjects = (
        PosterCard.objects
        .exclude(subject__isnull=True)
        .exclude(subject__exact="")
        .values("subject")
        .annotate(total=Count("id"))
        .order_by("subject")
    )
    return render(request, "learner/menu.html", {"subjects": subjects})

def study(request, subject):
    subject = unquote(subject).strip()

    if request.GET.get("restart"):
        _reset_session(request)

    sub_in_session = request.session.get("study_subject")
    order = request.session.get("study_order")
    index = request.session.get("study_index", 0)
    revealed = request.session.get("study_revealed", False)

    if sub_in_session != subject or not order:
        ids = list(
            PosterCard.objects.filter(subject__iexact=subject)
            .values_list("id", flat=True).order_by("id")
        )
        if not ids:
            ids = list(
                PosterCard.objects.filter(subject__icontains=subject)
                .values_list("id", flat=True).order_by("id")
            )
        if not ids:
            return redirect("learner:menu")

        request.session["study_subject"] = subject
        request.session["study_order"] = ids
        request.session["study_index"] = 0
        request.session["study_revealed"] = False
        request.session.modified = True
        order, index, revealed = ids, 0, False

    completed = False

    if request.method == "POST":

        # --- NEW: Zurück-Button ---
        if "back" in request.POST:
            if index > 0:
                index -= 1
                request.session["study_index"] = index
                request.session["study_revealed"] = False
                request.session.modified = True
                revealed = False

        elif "reveal" in request.POST:
            revealed = True
            request.session["study_revealed"] = True
            request.session.modified = True

        elif "repeat" in request.POST:
            if order:
                current_id = order[index]
                order.append(current_id)
                request.session["study_order"] = order
                index += 1
                request.session["study_index"] = index
                request.session["study_revealed"] = False
                request.session.modified = True
                revealed = False

        elif "next" in request.POST:
            index += 1
            if index >= len(order):
                completed = True
                index = len(order) - 1
                # Notizen löschen nach Abschluss
                question_ids = [str(i) for i in order]
                if request.user.is_authenticated:
                    StudyNote.objects.filter(
                        user=request.user,
                        question_id__in=question_ids
                    ).delete()
                else:
                    StudyNote.objects.filter(
                        session_id=request.session.session_key,
                        question_id__in=question_ids
                    ).delete()
                _reset_session(request)
            else:
                request.session["study_index"] = index
                request.session["study_revealed"] = False
                request.session.modified = True
                revealed = False

    try:
        card_id = order[index] if order else None
    except Exception:
        _reset_session(request)
        return redirect("learner:menu")

    card = PosterCard.objects.filter(id=card_id).first() if card_id else None
    if not card:
        _reset_session(request)
        return redirect("learner:menu")

    progress = {"now": index + 1, "total": len(order)}

    return render(request, "learner/study.html", {
    "subject": subject,
    "card": card,
    "revealed": revealed,
    "progress": progress,
    "completed": completed,
    "total_correct": request.session.get("total_correct", 0),
    "total_wrong": request.session.get("total_wrong", 0),
    })


def flip(request, subject):
    subject = unquote(subject).strip()

    qs = PosterCard.objects.filter(subject__iexact=subject).order_by("id")
    if not qs.exists():
        qs = PosterCard.objects.filter(subject__icontains=subject).order_by("id")
    if not qs.exists():
        return redirect("learner:menu")

    cards = list(qs.values("id", "question", "answer"))
    return render(request, "learner/flip.html", {
        "subject": subject,
        "cards": cards,
        "total": len(cards),
    })


import json
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseNotAllowed
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.middleware.csrf import get_token

from .models import StudyNote

@require_http_methods(["GET", "POST"])
def note_api(request, question_id: str):
    if not request.session.session_key:
        request.session.create()
    session_id = request.session.session_key

    if request.user.is_authenticated:
        lookup = {"user": request.user, "question_id": str(question_id)}
    else:
        lookup = {"session_id": session_id, "question_id": str(question_id)}

    note, _ = StudyNote.objects.get_or_create(**lookup)

    if request.method == "GET":
        return JsonResponse({
            "text": note.text,
            "selbstbewertung": note.selbstbewertung,
            "count_correct": note.count_correct,
            "count_wrong": note.count_wrong,
            "updated_at": note.updated_at.isoformat(),
        })

    if request.method == "POST":
        try:
            body = json.loads(request.body.decode("utf-8"))
        except Exception:
            return HttpResponseBadRequest("invalid json")

        if "text" in body:
            note.text = body["text"]

        if "selbstbewertung" in body:
            wert = int(body["selbstbewertung"])
            note.selbstbewertung = wert
            if wert == 3:
                note.count_correct += 1
                request.session["total_correct"] = request.session.get("total_correct", 0) + 1
            elif wert == 1:
                note.count_wrong += 1
                request.session["total_wrong"] = request.session.get("total_wrong", 0) + 1
            request.session.modified = True

        note.save()
        return JsonResponse({
            "ok": True,
            "text": note.text,
            "selbstbewertung": note.selbstbewertung,
            "count_correct": note.count_correct,
            "count_wrong": note.count_wrong,
            "total_correct": request.session.get("total_correct", 0),
            "total_wrong": request.session.get("total_wrong", 0),
            "updated_at": note.updated_at.isoformat(),
        })
    
    