from django.shortcuts import redirect


def redirect_admin_view(request):
    return redirect("/admin/")


def redirect_swagger_view(request):
    return redirect("/swagger/")
