from django.shortcuts import redirect

def admin_required(view_func):
    def wrapper(request, *args, **kwargs):  # make sure to include request, *args, **kwargs
        if request.session.get("user") != "admin":
            return redirect("login")
        return view_func(request, *args, **kwargs)  # pass all arguments to the view
    return wrapper
