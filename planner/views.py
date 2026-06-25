from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.conf import settings

from google import genai

from .models import AIPlan


@login_required
def ai_planner(request):

    response_text = ""

    if request.method == "POST":

        prompt = request.POST.get("prompt")

        try:

            client = genai.Client(
                api_key=settings.GEMINI_API_KEY
            )

            response = client.models.generate_content(

                model="gemini-2.0-flash",

                contents=f"""
You are an AI Productivity Coach.

Create a professional daily schedule.

User Input:

{prompt}

Give response in this format:

📅 Schedule

🎯 Priority

💡 Productivity Tips
"""
            )

            response_text = response.text

            # Save AI Plan

            AIPlan.objects.create(

                user=request.user,

                prompt=prompt,

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