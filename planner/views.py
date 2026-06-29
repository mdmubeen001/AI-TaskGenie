import sys
import json
import logging
from datetime import datetime
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.shortcuts import render, redirect
from django.contrib import messages

try:
    from google import genai
except Exception:
    genai = None

from .models import AIPlan
from tasks.models import Task

logger = logging.getLogger(__name__)


def generate_ai_roadmap(data):
    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    prompt = f"""You are AI TaskGenie.

Goal: {data.get('goal', '')}
Available Hours per Week: {data.get('available_hours', '')}
Priority: {data.get('priority', '')}
Energy Level: {data.get('energy_level', '')}
User's Final Deadline: {data.get('deadline', '')}
Break Duration: {data.get('break_duration', '')}
Work Style: {data.get('work_style', '')}
Additional Notes: {data.get('additional_notes', '')}

Generate a professional roadmap.

STRICT DEADLINE RULES:
1. Use ONLY the User's Final Deadline provided above.
2. Divide the User's Final Deadline intelligently across ALL generated tasks.
3. Every task MUST have its own suggested_deadline in YYYY-MM-DD format.
4. Task deadlines must be distributed chronologically from today's date ({datetime.today().date().strftime('%Y-%m-%d')}) up to the User's Final Deadline.
5. The LAST generated task's suggested_deadline MUST EXACTLY match the User's Final Deadline.
6. NO extra roadmap-level deadline.

OTHER STRICT RULES:
- MAX 4 phases
- MAX 8 tasks total"""

    retries = 3
    for attempt in range(retries):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config={
                    "temperature": 0.2,
                    "max_output_tokens": 2500,
                    "response_mime_type": "application/json",
                    "response_schema": {
                        "type": "OBJECT",
                        "properties": {
                            "phases": {
                                "type": "ARRAY",
                                "items": {
                                    "type": "OBJECT",
                                    "properties": {
                                        "name": {"type": "STRING"},
                                        "description": {"type": "STRING"}
                                    },
                                    "required": ["name", "description"]
                                }
                            },
                            "tasks": {
                                "type": "ARRAY",
                                "items": {
                                    "type": "OBJECT",
                                    "properties": {
                                        "title": {"type": "STRING"},
                                        "description": {"type": "STRING"},
                                        "priority": {"type": "STRING"},
                                        "estimated_duration": {"type": "INTEGER"},
                                        "suggested_deadline": {"type": "STRING"},
                                        "phase": {"type": "STRING"},
                                        "order": {"type": "INTEGER"}
                                    },
                                    "required": ["title", "description", "priority", "estimated_duration", "suggested_deadline", "phase", "order"]
                                }
                            }
                        },
                        "required": ["phases", "tasks"]
                    }
                }
            )
            parsed = response.parsed
            if parsed:
                return parsed
        except Exception as e:
            logger.error(f"Gemini API attempt {attempt+1} failed: {str(e)}")
            if attempt == retries - 1:
                raise
    return None


@login_required
def ai_planner(request):
    generated_data = None
    error = None

    latest_plan = AIPlan.objects.filter(
        user=request.user
    ).order_by("-created_at").first()

    form_data = {
        "goal": "",
        "available_hours": "",
        "priority": "Medium",
        "energy_level": "Medium",
        "deadline": "",
        "break_duration": "30",
        "work_style": "Balanced",
        "additional_notes": ""
    }

    if request.method == "POST":
        form_data = {
            "goal": request.POST.get("goal"),
            "available_hours": request.POST.get("available_hours"),
            "priority": request.POST.get("priority"),
            "energy_level": request.POST.get("energy_level"),
            "deadline": request.POST.get("deadline"),
            "break_duration": request.POST.get("break_duration"),
            "work_style": request.POST.get("work_style"),
            "additional_notes": request.POST.get("additional_notes")
        }

        cache_key = f"planner_{request.user.id}_{hash(json.dumps(form_data, sort_keys=True))}"

        if "generate" in request.POST:
            cached = cache.get(cache_key)
            if cached:
                generated_data = cached
                request.session["generated_tasks"] = generated_data
            else:
                if genai is None:
                    logger.error("Google Gemini SDK not available")
                    error = "AI service is temporarily unavailable. Please try again later."
                else:
                    try:
                        generated_data = generate_ai_roadmap(form_data)
                        if not generated_data:
                            error = "AI service returned an empty response. Please try again later."
                        else:
                            cache.set(cache_key, generated_data, timeout=600)
                            request.session["generated_tasks"] = generated_data
                            AIPlan.objects.create(
                                user=request.user,
                                prompt=form_data["goal"],
                                response=json.dumps(generated_data)
                            )
                    except json.JSONDecodeError as e:
                        logger.exception("Invalid JSON from Gemini: %s", str(e))
                        error = "AI service returned invalid data. Please try again later."
                    except Exception as e:
                        logger.exception(f"Generate roadmap failed: %s", str(e))
                        error = "AI service is temporarily unavailable. Please try again later."
            if generated_data:
                request.session["generated_tasks"] = generated_data
                request.session["cached_form_data"] = form_data

        elif "regenerate" in request.POST:
            if "generated_tasks" in request.session:
                del request.session["generated_tasks"]
            if "cached_form_data" in request.session:
                del request.session["cached_form_data"]
            cache.delete(cache_key)
            generated_data = None

        elif "approve_all" in request.POST:
            generated_data = request.session.get("generated_tasks", {})
            if generated_data and "tasks" in generated_data:
                for task_data in generated_data["tasks"]:
                    deadline = None
                    try:
                        if task_data.get("suggested_deadline"):
                            deadline = datetime.strptime(
                                task_data["suggested_deadline"],
                                "%Y-%m-%d"
                            ).date()
                    except Exception:
                        pass
                    Task.objects.create(
                        user=request.user,
                        title=task_data["title"],
                        description=task_data["description"],
                        priority=task_data["priority"],
                        deadline=deadline,
                        estimated_duration=task_data.get("estimated_duration", 60),
                        phase=task_data.get("phase", ""),
                        order=task_data.get("order", 1),
                        status="Pending"
                    )
                if "generated_tasks" in request.session:
                    del request.session["generated_tasks"]
                messages.success(request, "All tasks created successfully!")
                return redirect("task_list")

        elif "approve_selected" in request.POST:
            generated_data = request.session.get("generated_tasks", {})
            selected = request.POST.getlist("selected_tasks")
            if generated_data and "tasks" in generated_data:
                for index in selected:
                    try:
                        task_data = generated_data["tasks"][int(index)]
                    except Exception:
                        continue
                    deadline = None
                    try:
                        if task_data.get("suggested_deadline"):
                            deadline = datetime.strptime(
                                task_data["suggested_deadline"],
                                "%Y-%m-%d"
                            ).date()
                    except Exception:
                        pass
                    Task.objects.create(
                        user=request.user,
                        title=task_data["title"],
                        description=task_data["description"],
                        priority=task_data["priority"],
                        deadline=deadline,
                        estimated_duration=task_data.get("estimated_duration", 60),
                        phase=task_data.get("phase", ""),
                        order=task_data.get("order", 1),
                        status="Pending"
                    )
            messages.success(request, "Selected tasks created successfully!")
            return redirect("task_list")

    if not generated_data:
        generated_data = request.session.get("generated_tasks", None)
        # If we have cached form data, use it
        cached_form = request.session.get("cached_form_data")
        if cached_form:
            form_data = cached_form

    if latest_plan and not generated_data:
        try:
            generated_data = json.loads(latest_plan.response)
        except Exception:
            pass

    context = {
        "generated_data": generated_data,
        "error": error,
        "latest_plan": latest_plan,
        "form_data": form_data,
        "goal": form_data.get("goal", ""),
        "available_hours": form_data.get("available_hours", ""),
        "priority": form_data.get("priority") or "Medium",
        "energy_level": form_data.get("energy_level") or "Medium",
        "deadline": form_data.get("deadline", ""),
        "break_duration": form_data.get("break_duration", "30"),
        "work_style": form_data.get("work_style") or "Balanced",
        "additional_notes": form_data.get("additional_notes", "")
    }

    return render(
        request,
        "planner/planner.html",
        context
    )
