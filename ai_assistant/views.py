from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.conf import settings

from google import genai

from .models import Chat
from django.shortcuts import redirect, get_object_or_404


@login_required
def ai_chat(request):

    chats = Chat.objects.filter(
        user=request.user
    )

    if request.method == "POST":

        prompt = request.POST.get("prompt")

        if prompt:

            try:

                client = genai.Client(
                    api_key=settings.GEMINI_API_KEY
                )

                response = client.models.generate_content(

                    model="gemini-2.5-flash",

                    contents=f"""
You are AI TaskGenie.

You are a professional AI Productivity Assistant.

Help the user with:

• Productivity
• Coding
• Django
• Python
• DSA
• Resume
• Career
• Interview
• Time Management

User Question:

{prompt}
"""
                )

                ai_response = response.text

            except Exception as e:

                error = str(e)

                if "429" in error:

                    ai_response = (
                        "⚠️ Gemini API quota exceeded.\n\n"
                        "Please try again later or use another API key."
                    )

                elif "503" in error:

                    ai_response = (
                        "⚠️ Gemini server is busy.\n\n"
                        "Please try again after a few seconds."
                    )

                else:

                    ai_response = f"Error:\n\n{error}"

            Chat.objects.create(

                user=request.user,

                prompt=prompt,

                response=ai_response

            )

            chats = Chat.objects.filter(
                user=request.user
            )

    return render(

        request,

        "ai_assistant/assistant.html",

        {

            "chats": chats

        }

    )

@login_required
def new_chat(request):

    Chat.objects.filter(
        user=request.user
    ).delete()

    return redirect("ai_chat")


@login_required
def delete_chat(request, id):

    chat = get_object_or_404(

        Chat,

        id=id,

        user=request.user

    )

    chat.delete()

    return redirect("ai_chat")