from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.conf import settings

from google import genai

from .models import AIPlan


@login_required
def ai_planner(request):

    response_text = ""

    if request.method == "POST":
        # Get form data
        goal = request.POST.get("goal", "")
        available_hours = request.POST.get("available_hours", "")
        priority = request.POST.get("priority", "Medium")
        deadline = request.POST.get("deadline", "")
        energy_level = request.POST.get("energy_level", "Medium")
        work_style = request.POST.get("work_style", "Balanced")
        break_duration = request.POST.get("break_duration", "30")
        prompt = request.POST.get("prompt", "")

        try:
            client = genai.Client(
                api_key=settings.GEMINI_API_KEY
            )

            system_prompt = f"""You are an AI Productivity Coach, expert in creating smart daily schedules similar to Motion AI, Notion AI, or Google Gemini.
Create a comprehensive daily plan structured into Morning, Afternoon, Evening, Night.

User Input Details:
- Goal: {goal}
- Available Hours: {available_hours}
- Priority: {priority}
- Deadline: {deadline}
- Energy Level: {energy_level}
- Work Style: {work_style}
- Break Duration: {break_duration} minutes
- Additional Notes: {prompt}

Instructions:
1. Create time-blocked schedule with estimated durations
2. Include intelligent break suggestions
3. Assign task priorities
4. Add productivity tips for each section
5. Analyze for potential overload and provide recommendations

Return ONLY this JSON format (no extra text):
{{
    "schedule": [
        {{
            "time": "08:00 - 09:00",
            "task": "Task Description",
            "priority": "High/Medium/Low",
            "duration": "60",
            "recommendation": "Focus Tip",
            "section": "Morning/Afternoon/Evening/Night"
        }}
    ],
    "productivity_tips": ["Tip 1", "Tip 2"],
    "smart_recommendations": ["Check schedule for overload", "Suggest 10-min micro-breaks"],
    "summary": {{
        "total_tasks": 4,
        "deep_work_hours": 3,
        "focus_score": 85
    }}
}}"""

            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=system_prompt
            )

            response_text = response.text

            # Save AI Plan
            AIPlan.objects.create(
                user=request.user,
                prompt=system_prompt,
                response=response_text
            )

        except Exception as e:
            response_text = str(e)

    return render(
        request,
        "planner/planner.html",
        {
            "response": response_text
        }
    )
