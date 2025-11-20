from .models import Baby

def active_profile(request):
    active = None
    profiles = []
    if request.user.is_authenticated:
        profiles = list(Baby.objects.filter(owner=request.user).order_by('name'))

        if profiles:
            profile_id = request.session.get('active_profile')

            if profile_id:
                for p in profiles:
                    if str(p.id) == str(profile_id):
                        active = p
                        break
            if profile_id and active is None:
                request.session.pop('active_profile', None)

            if active is None:
                active = profiles[0]
                request.session['active_profile'] = str(active.id)

    return {'active_profile': active, 'profiles': profiles}

