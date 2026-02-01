from django.shortcuts import redirect


def permitted_user_roles(roles):

    def decorator(fn):

        def wrapper(request,*args,**kwargs):

            if request.user.is_authenticated and request.user.role in roles:

                return fn(request,*args,**kwargs)
        
            else:
                
                return redirect('home')
        
        return wrapper

    return decorator