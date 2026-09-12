from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.views import View


class HomeView(View):
    def get(self, request):

        context = {
           
        }

        return render(request, "pages/index.html", context)