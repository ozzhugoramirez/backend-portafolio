from django.shortcuts import render
from django.views import View
from api.models import Profile, Project

class HomeView(View):
    def get(self, request):
        
        profile = Profile.objects.first()
        
       
        projects = Project.objects.filter(is_public=True)

        context = {
            'profile': profile,
            'projects': projects,
        }

        return render(request, "pages/index.html", context)