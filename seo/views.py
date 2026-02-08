from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from .agents.seo_agent import run_seo_agent
from .forms import KeywordForm, URLForm
from .models import (
    AuditReport,
    ChatMessage,
    ContentOptimization,
    Conversation,
    KeywordResearch,
)


def audit(request):
    form = URLForm()
    report = None

    if request.method == "POST":
        form = URLForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data["url"]
            try:
                prompt = f"Please perform a comprehensive SEO audit on this URL: {url}"
                response = run_seo_agent(prompt)

                # Try to extract score from tool output
                score = None
                try:
                    # The agent may include JSON in its response
                    for line in response.split("\n"):
                        if '"score"' in line:
                            score = int("".join(c for c in line.split(":")[1] if c.isdigit()))
                            break
                except (ValueError, IndexError):
                    pass

                report = AuditReport.objects.create(
                    url=url,
                    result="",
                    agent_summary=response,
                    score=score,
                )
            except Exception as e:
                messages.error(request, f"Audit failed: {e}")

    recent = AuditReport.objects.all()[:10]
    return render(request, "seo/audit.html", {
        "form": form,
        "report": report,
        "recent_audits": recent,
    })


def audit_detail(request, pk):
    report = get_object_or_404(AuditReport, pk=pk)
    return render(request, "seo/audit_detail.html", {"report": report})


def keywords(request):
    form = KeywordForm()
    result = None

    if request.method == "POST":
        form = KeywordForm(request.POST)
        if form.is_valid():
            seed = form.cleaned_data["seed_keyword"]
            try:
                prompt = f"Please research keyword ideas for: {seed}"
                response = run_seo_agent(prompt)

                # Try to extract total keywords count
                total = None
                try:
                    for line in response.split("\n"):
                        if "total" in line.lower() and "keyword" in line.lower():
                            nums = [int(s) for s in line.split() if s.isdigit()]
                            if nums:
                                total = nums[0]
                                break
                except (ValueError, IndexError):
                    pass

                result = KeywordResearch.objects.create(
                    seed_keyword=seed,
                    result="",
                    agent_summary=response,
                    total_keywords=total,
                )
            except Exception as e:
                messages.error(request, f"Keyword research failed: {e}")

    recent = KeywordResearch.objects.all()[:10]
    return render(request, "seo/keywords.html", {
        "form": form,
        "result": result,
        "recent_research": recent,
    })


def optimize(request):
    form = URLForm()
    result = None

    if request.method == "POST":
        form = URLForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data["url"]
            try:
                prompt = f"Please analyze the content of this URL for SEO optimization: {url}"
                response = run_seo_agent(prompt)

                result = ContentOptimization.objects.create(
                    url=url,
                    result="",
                    agent_summary=response,
                )
            except Exception as e:
                messages.error(request, f"Content analysis failed: {e}")

    recent = ContentOptimization.objects.all()[:10]
    return render(request, "seo/optimize.html", {
        "form": form,
        "result": result,
        "recent_optimizations": recent,
    })


def chat(request):
    # Get or create conversation from session
    conv_id = request.session.get("conversation_id")
    conversation = None
    if conv_id:
        try:
            conversation = Conversation.objects.get(pk=conv_id)
        except Conversation.DoesNotExist:
            request.session.pop("conversation_id", None)

    if request.method == "POST":
        if request.POST.get("clear"):
            request.session.pop("conversation_id", None)
            return redirect("seo:chat")

        if request.POST.get("new_chat"):
            request.session.pop("conversation_id", None)
            return redirect("seo:chat")

        user_message = request.POST.get("message", "").strip()
        if user_message:
            if not conversation:
                conversation = Conversation.objects.create(
                    title=user_message[:100],
                )
                request.session["conversation_id"] = conversation.pk

            # Build history from DB
            db_messages = conversation.messages.all()
            history = [{"role": m.role, "content": m.content} for m in db_messages]

            try:
                response = run_seo_agent(user_message, history=history)
                ChatMessage.objects.create(
                    conversation=conversation,
                    role="user",
                    content=user_message,
                )
                ChatMessage.objects.create(
                    conversation=conversation,
                    role="assistant",
                    content=response,
                )
            except Exception as e:
                messages.error(request, f"Agent error: {e}")

    chat_messages = []
    if conversation:
        chat_messages = conversation.messages.all()

    return render(request, "seo/chat.html", {
        "chat_history": chat_messages,
        "conversation": conversation,
    })


def history(request):
    audits = AuditReport.objects.all()[:20]
    keyword_reports = KeywordResearch.objects.all()[:20]
    optimizations = ContentOptimization.objects.all()[:20]
    conversations = Conversation.objects.all()[:20]

    return render(request, "seo/history.html", {
        "audits": audits,
        "keyword_reports": keyword_reports,
        "optimizations": optimizations,
        "conversations": conversations,
    })
