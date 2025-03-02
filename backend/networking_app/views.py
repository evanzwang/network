from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .matching import Matcher
import re
import json


# URL validation function
def is_valid_url(url):
    if not url:
        return False

    # Basic URL validation regex
    url_pattern = re.compile(
        r"^(https?://)"  # http:// or https://
        r"([a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?\.)+[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?"
        r"(/[a-zA-Z0-9_\-./~%]*)?"  # path
        r"(\?[a-zA-Z0-9_\-./~%=&]*)?"  # query string
        r"(#[a-zA-Z0-9_\-.~%]*)?$"  # fragment
    )

    return bool(url_pattern.match(url))


# Default fallback image URL
DEFAULT_IMAGE_URL = "https://randomuser.me/api/portraits/lego/1.jpg"

matcher = Matcher("networking_app/processed", "networking_app/model_configs/gpt-4o-mini.json")


# Create your views here.
def hello_world(request):
    """
    A simple view that returns 'Hello, World!' as an HTTP response.
    """
    return HttpResponse("Hello, World!")


def get_person(request, person_id):
    """
    Returns a specific person by their ID as JSON response
    """
    if request.method == "GET":
        # Convert person_id to integer
        try:
            person_id = int(person_id)
        except ValueError:
            return JsonResponse({"error": "Invalid ID format"}, status=400)

        # Find the person with the given ID
        person = next((p for p in PEOPLE if p["id"] == person_id), None)

        if person:
            return JsonResponse({"person": person})
        else:
            return JsonResponse({"error": "Person not found"}, status=404)


def get_all_people(request):
    """
    Returns the list of all people as JSON response
    """
    people = matcher.get_everyone()
    people = [
        {
            "name": p.name,
            "imageUrl": is_valid_url(p.profile_pic) and p.profile_pic or DEFAULT_IMAGE_URL,
            "description": p.short_description,
            "contacts": p.contacts,
        }
        for p in people
    ]
    if request.method == "GET":
        return JsonResponse({"people": people})


def get_suggested_relationships(request):
    with open("backend/networking_app/matches.json", "r") as f:
        people = json.load(f)

    if request.method == "GET":
        return JsonResponse({"people": people})


def get_match_from_text(request):
    """
    Returns a match for the given text as JSON response
    """
    if request.method == "GET":
        try:
            text = request.GET.get("text")
            k = request.GET.get("k", 5)
            method = request.GET.get("method", "elo")

            # Log the request parameters
            print(f"Match request - text: {text}, k: {k}, method: {method}")

            matches, compats = matcher.query(text, method, k, num_pairs=1000)
            if compats is None:
                pass
            matches = [
                {
                    "name": m.name,
                    "imageUrl": is_valid_url(m.profile_pic) and m.profile_pic or DEFAULT_IMAGE_URL,
                    "description": m.short_description,
                    "contacts": m.contacts,
                    "matchScore": compats[i]
                }
                for i,m in enumerate(matches)
            ]

            return JsonResponse({"matches": matches})
        except Exception as e:
            # Log the full error details
            import traceback

            error_details = traceback.format_exc()
            print(f"ERROR in get_match_from_text: {str(e)}")
            print(f"Traceback: {error_details}")

            # Return a more informative error response
            return JsonResponse({"error": str(e), "details": error_details}, status=500)


def get_matching_reason(request):
    """
    Returns reasons why specific people match a given query
    """
    if request.method == "GET":
        text = request.GET.get("text")
        names = request.GET.get("names", "")

        print('Query Received: ', text)

        print(f"Received request for reasons - text: {text}, names: {names}")

        if not text:
            return JsonResponse({"error": "No search text provided"}, status=400)

        # Split the names string into a list
        name_list = [name.strip() for name in names.split(",") if name.strip()]

        print(f"Parsed name list: {name_list}")

        if not name_list:
            return JsonResponse({"error": "No names provided"}, status=400)

        reasons = matcher.get_specific_reason(text, name_list)

        # Ensure reasons is a dictionary
        if not isinstance(reasons, dict):
            print(f"Warning: reasons is not a dictionary, it's a {type(reasons)}")
            # Convert to dictionary if it's not already
            if isinstance(reasons, list) and len(reasons) == len(name_list):
                reasons = {name: reason for name, reason in zip(name_list, reasons)}
            else:
                reasons = {name: "No specific reason available" for name in name_list}

        return JsonResponse({"reasons": reasons})
