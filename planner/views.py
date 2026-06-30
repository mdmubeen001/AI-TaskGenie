import sys
import json
import logging
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

try:
    import google.generativeai as genai
    HAS_GENAI = True
except Exception as e:
    genai = None
    HAS_GENAI = False

from .models import AIPlan, Roadmap
from tasks.models import Task

logger = logging.getLogger(__name__)

# Predefined sample roadmap as fallback
SAMPLE_ROADMAP = {
    "phases": [
        {
            "name": "Foundation & Setup",
            "description": "Set up the project and core infrastructure"
        },
        {
            "name": "Core Features",
            "description": "Implement essential functionality"
        },
        {
            "name": "Polish & Deployment",
            "description": "Finalize and prepare for launch"
        }
    ],
    "tasks": [
        {
            "title": "Initialize Project",
            "description": "Set up project structure and dependencies",
            "priority": "High",
            "estimated_duration": 120,
            "suggested_deadline": datetime.today().strftime("%Y-%m-%d"),
            "phase": "Foundation & Setup",
            "order": 1
        },
        {
            "title": "Implement Basic UI",
            "description": "Build core user interface components",
            "priority": "High",
            "estimated_duration": 180,
            "suggested_deadline": (datetime.today() + timedelta(days=5)).strftime("%Y-%m-%d"),
            "phase": "Foundation & Setup",
            "order": 2
        },
        {
            "title": "Core Feature Development",
            "description": "Implement main application features",
            "priority": "High",
            "estimated_duration": 240,
            "suggested_deadline": (datetime.today() + timedelta(days=12)).strftime("%Y-%m-%d"),
            "phase": "Core Features",
            "order": 3
        },
        {
            "title": "Testing & Bug Fixes",
            "description": "Test application and fix any issues",
            "priority": "Medium",
            "estimated_duration": 180,
            "suggested_deadline": (datetime.today() + timedelta(days=18)).strftime("%Y-%m-%d"),
            "phase": "Core Features",
            "order": 4
        },
        {
            "title": "Deployment Preparation",
            "description": "Prepare application for production deployment",
            "priority": "High",
            "estimated_duration": 120,
            "suggested_deadline": (datetime.today() + timedelta(days=25)).strftime("%Y-%m-%d"),
            "phase": "Polish & Deployment",
            "order": 5
        }
    ]
}


def generate_ai_roadmap(data):
    print("Calling Gemini")
    
    genai.configure(api_key=settings.GEMINI_API_KEY)
    
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
- MAX 8 tasks total

Output a JSON with keys 'phases' (array of objects with 'name' and 'description') and 'tasks' (array of objects with 'title', 'description', 'priority', 'estimated_duration', 'suggested_deadline', 'phase', 'order')
"""

    retries = 3
    for attempt in range(retries):
        try:
            model = genai.GenerativeModel("gemini-2.0-flash")
            response = model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.2,
                    "max_output_tokens": 2500,
                    "response_mime_type": "application/json"
                }
            )
            parsed = json.loads(response.text)
            print("Gemini response received")
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

    print("=== ai_planner view ===")
    print(f"Method: {request.method}")
    
    # First try to load from session regardless of request method
    if "generated_tasks" in request.session:
        print("Loaded roadmap from session")
        generated_data = request.session["generated_tasks"]
        cached_form = request.session.get("cached_form_data")
        if cached_form:
            form_data = cached_form
    
    if request.method == "POST":
        print(f"POST: {request.POST}")
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
        print(f"Cache key: {cache_key}")

        # Check for generate action - either via button or form submit with no other actions
        if "generate" in request.POST or ("regenerate" not in request.POST and "approve_all" not in request.POST and "approve_selected" not in request.POST):
            print("Generate button clicked!")
            cached = cache.get(cache_key)
            if cached:
                print("Loaded roadmap from cache")
                generated_data = cached
                request.session["generated_tasks"] = generated_data
                request.session["cached_form_data"] = form_data
            else:
                if not HAS_GENAI:
                    logger.error("Google Gemini SDK not available")
                    error = "AI service is temporarily unavailable. Please try again later."
                else:
                    try:
                        generated_data = generate_ai_roadmap(form_data)
                        print(f"Generated data: {generated_data}")
                        if not generated_data:
                            raise Exception("Empty response from AI")
                        else:
                            print("Saving roadmap to cache")
                            cache.set(cache_key, generated_data, timeout=600)
                            print("Saving roadmap to session")
                            request.session["generated_tasks"] = generated_data
                            request.session["cached_form_data"] = form_data
                            AIPlan.objects.create(
                                user=request.user,
                                prompt=form_data["goal"],
                                response=json.dumps(generated_data)
                            )
                    except Exception as e:
                        logger.error(f"Generate roadmap failed: %s", str(e))
                        # Fallback to sample roadmap
                        print("Using fallback sample roadmap")
                        generated_data = SAMPLE_ROADMAP
                        request.session["generated_tasks"] = generated_data
                        request.session["cached_form_data"] = form_data
                        # Add a flag to indicate it's a sample
                        request.session["is_sample_roadmap"] = True
            print(f"generated_data after generate: {generated_data}")

        elif "regenerate" in request.POST:
            print("Regenerate button clicked!")
            if "generated_tasks" in request.session:
                del request.session["generated_tasks"]
            if "cached_form_data" in request.session:
                del request.session["cached_form_data"]
            if "is_sample_roadmap" in request.session:
                del request.session["is_sample_roadmap"]
            cache.delete(cache_key)
            generated_data = None

        elif "approve_all" in request.POST or "approve_selected" in request.POST:
            print("Approve button clicked!")
            generated_data = request.session.get("generated_tasks", {})
            if generated_data and "tasks" in generated_data:
                # Get goal with fallbacks
                goal = form_data.get("goal")
                if not goal and "cached_form_data" in request.session:
                    goal = request.session["cached_form_data"].get("goal")
                if not goal:
                    goal = request.POST.get("goal")
                if not goal:
                    error = "Roadmap goal is missing."
                else:
                    # Create Roadmap first
                    print("Goal:", goal)
                    roadmap = Roadmap.objects.create(
                        user=request.user,
                        goal=goal,
                        phases=generated_data.get("phases", []),
                        tasks=generated_data.get("tasks", []),
                        available_hours=form_data.get("available_hours"),
                        priority=form_data.get("priority"),
                        energy_level=form_data.get("energy_level"),
                        deadline=form_data.get("deadline"),
                        work_style=form_data.get("work_style"),
                        additional_notes=form_data.get("additional_notes")
                    )
                    
                    # Process tasks
                    if "approve_all" in request.POST:
                        tasks_to_process = generated_data["tasks"]
                    else:
                        selected = request.POST.getlist("selected_tasks")
                        tasks_to_process = [
                            generated_data["tasks"][int(index)] 
                            for index in selected 
                            if 0 <= int(index) < len(generated_data["tasks"])
                        ]
                    
                    for task_data in tasks_to_process:
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
                            roadmap=roadmap,
                            title=task_data["title"],
                            description=task_data["description"],
                            priority=task_data["priority"],
                            deadline=deadline,
                            estimated_duration=task_data.get("estimated_duration", 60),
                            phase=task_data.get("phase", ""),
                            order=task_data.get("order", 1),
                            status="Pending"
                        )
                    
                    # Clear sessions
                    if "generated_tasks" in request.session:
                        del request.session["generated_tasks"]
                    if "cached_form_data" in request.session:
                        del request.session["cached_form_data"]
                    if "is_sample_roadmap" in request.session:
                        del request.session["is_sample_roadmap"]
                    
                    messages.success(request, "Roadmap approved successfully! You can view it in Roadmaps.")
                    return redirect("roadmaps_list")

    # If not in session, try cache
    if not generated_data:
        # We need form_data to generate cache_key, so we have to get it somewhere
        # Wait for GET request, we don't have form_data except default, but let's check session
        # Also, maybe on GET, if we have cached_form, use that
        cached_form = request.session.get("cached_form_data")
        if cached_form:
            form_data = cached_form
            cache_key = f"planner_{request.user.id}_{hash(json.dumps(form_data, sort_keys=True))}"
            cached = cache.get(cache_key)
            if cached:
                print("Loaded roadmap from cache")
                generated_data = cached
                request.session["generated_tasks"] = generated_data

    context = {
        "generated_data": generated_data,
        "error": error,
        "form_data": form_data,
        "is_sample_roadmap": request.session.get("is_sample_roadmap", False)
    }
    print(f"Context: {context}")
    return render(request, "planner/planner.html", context)


@login_required
def roadmaps_list(request):
    roadmaps = Roadmap.objects.filter(user=request.user)
    return render(request, "planner/roadmaps_list.html", {"roadmaps": roadmaps})


@login_required
def roadmap_detail(request, roadmap_id):
    roadmap = get_object_or_404(Roadmap, id=roadmap_id, user=request.user)
    tasks = Task.objects.filter(roadmap=roadmap)
    return render(request, "planner/roadmap_detail.html", {"roadmap": roadmap, "tasks": tasks})


@login_required
def delete_roadmap(request, roadmap_id):
    roadmap = get_object_or_404(Roadmap, id=roadmap_id, user=request.user)
    roadmap.delete()
    messages.success(request, "Roadmap deleted successfully!")
    return redirect("roadmaps_list")
