from django.shortcuts import render
from django.http import HttpResponse, JsonResponse

# Sample people data
PEOPLE = [
    {
        'id': 1,
        'name': 'Jane Doe',
        'imageUrl': 'https://randomuser.me/api/portraits/women/1.jpg',
        'description': 'Software Engineer with 5 years of experience in web development.'
    },
    {
        'id': 2,
        'name': 'John Smith',
        'imageUrl': 'https://randomuser.me/api/portraits/men/1.jpg', 
        'description': 'Product Manager specializing in SaaS products and user experience.'
    },
    {
        'id': 3,
        'name': 'Emily Johnson',
        'imageUrl': 'https://randomuser.me/api/portraits/women/2.jpg',
        'description': 'UX Designer with a passion for creating intuitive user interfaces.'
    },
    {
        'id': 4,
        'name': 'Michael Chen',
        'imageUrl': 'https://randomuser.me/api/portraits/men/2.jpg',
        'description': 'Data Scientist focused on machine learning and AI applications.'
    },
    {
        'id': 5,
        'name': 'Sarah Williams', 
        'imageUrl': 'https://randomuser.me/api/portraits/women/3.jpg',
        'description': 'DevOps Engineer specializing in cloud infrastructure and automation.'
    },
    {
        'id': 6,
        'name': 'David Kim',
        'imageUrl': 'https://randomuser.me/api/portraits/men/3.jpg',
        'description': 'Frontend Developer with expertise in React and modern JavaScript frameworks.'
    },
    {
        'id': 7,
        'name': 'Lisa Garcia',
        'imageUrl': 'https://randomuser.me/api/portraits/women/4.jpg',
        'description': 'Technical Project Manager with agile methodology expertise.'
    },
    {
        'id': 8,
        'name': 'James Wilson',
        'imageUrl': 'https://randomuser.me/api/portraits/men/4.jpg',
        'description': 'Security Engineer focused on application and network security.'
    },
    {
        'id': 9,
        'name': 'Rachel Taylor',
        'imageUrl': 'https://randomuser.me/api/portraits/women/5.jpg',
        'description': 'Backend Developer specializing in scalable microservices architecture.'
    },
    {
        'id': 10,
        'name': 'Thomas Anderson',
        'imageUrl': 'https://randomuser.me/api/portraits/men/5.jpg',
        'description': 'Systems Architect with expertise in distributed systems.'
    },
    {
        'id': 11,
        'name': 'Michelle Lee',
        'imageUrl': 'https://randomuser.me/api/portraits/women/6.jpg',
        'description': 'Quality Assurance Engineer specializing in automated testing.'
    },
    {
        'id': 12,
        'name': 'Robert Martinez',
        'imageUrl': 'https://randomuser.me/api/portraits/men/6.jpg',
        'description': 'Mobile Developer with experience in iOS and Android development.'
    },
    {
        'id': 13,
        'name': 'Amanda Brown',
        'imageUrl': 'https://randomuser.me/api/portraits/women/7.jpg',
        'description': 'Database Administrator with expertise in SQL and NoSQL systems.'
    }
]

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
    if request.method == 'GET':
        # Convert person_id to integer
        try:
            person_id = int(person_id)
        except ValueError:
            return JsonResponse({'error': 'Invalid ID format'}, status=400)
        
        # Find the person with the given ID
        person = next((p for p in PEOPLE if p['id'] == person_id), None)
        
        if person:
            return JsonResponse({'person': person})
        else:
            return JsonResponse({'error': 'Person not found'}, status=404)

def get_all_people(request):
    """
    Returns the list of all people as JSON response
    """
    if request.method == 'GET':
        return JsonResponse({'people': PEOPLE})