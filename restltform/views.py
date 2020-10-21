from django.shortcuts import render,HttpResponseRedirect,reverse
from .forms import PeopleForm,UserCreate,loginform,UserProfile
from django.contrib.auth.models import User,auth
from django.contrib import messages
# Create your views here.
from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse
from .models import People,follow,comments
import json
from random import shuffle
import random
import cloudinary
import cloudinary.uploader
import cloudinary.api
#obj.likes_users.filter(username='sample_user2').exists()
# Create your views here.
def returndata(request):
    #print(str(request.user))
    #if request.method=='POST':
    #    ob=get_object_or_404(People,id=request.POST.get('ids'))
     #   ob.likes_users.add(request.user)
      #  ob.save()
       # obj=People.objects.all()
        #objs={'obj':obj,'loginuser':str(request.user)}
       # return HttpResponseRedirect(reverse('data'))
   # if request.method=='GET':
    obj=People.objects.all()
    obj_fol=follow.objects.all()
    cmt_user=comments.objects.all()
    obj=obj.order_by('?')
    u_prof={}
    obj=obj[::-1]
    for i in obj_fol:
        u_prof[i.user]=i
    if request.user.is_authenticated:
        fs=get_object_or_404(follow,user=request.user)
        objs={'obj':obj,'loginuser':str(request.user),'fs':fs,'u_prof':u_prof,'cmt_user':cmt_user}
    else:
        objs={'obj':obj,'loginuser':str(request.user),'u_prof':u_prof}
    return render(request,'index.html',objs)
def follow_data(request):
    people_obj=People.objects.all()
    obj_fol=follow.objects.all()
    cmt_user=comments.objects.all()
    obj=[]
    f=follow.objects.get(user=request.user)
    for i in people_obj: 
        if i.users in f.followed_users():
            obj.append(i)
    u_prof={}
    obj=obj[::-1]
    for i in obj_fol:
        u_prof[i.user]=i
    if request.user.is_authenticated:
        fs=get_object_or_404(follow,user=request.user)
        objs={'obj':obj,'loginuser':str(request.user),'fs':fs,'u_prof':u_prof,'cmt_user':cmt_user}
    else:
        objs={'obj':obj,'loginuser':str(request.user),'u_prof':u_prof}
    return render(request,'index.html',objs)
def storingdata(request):
    #obj=People.objects.get()
    username=str(request.user)
    obs={'username':username}
    form=PeopleForm(initial=obs)
    if request.method=='POST':
        form=PeopleForm(request.POST,request.FILES)
        if form.is_valid():
            #profile=cloudinary.uploader.upload(request.FILES['profile'])
            form=form.cleaned_data
            form['users']=request.user
            #form['profile']=profile['url']
            People.objects.create(**form)
            return HttpResponseRedirect(reverse('data'))
    content={'forms':form}
    return render(request,'datacollect.html',content)
def sepcificview(request,my_id):
    obj=get_object_or_404(People,id=my_id)
    obj=[obj]
    obj_fol=follow.objects.all()
    u_prof={}
    for i in obj_fol:
        u_prof[i.user]=i
    if request.user.is_authenticated:
        fs=get_object_or_404(follow,user=request.user)
        contents={'obj':obj,'fs':fs,'u_prof':u_prof}
    else:
        contents={'obj':obj,'u_prof':u_prof}
    return render(request,'index.html',contents)
def deleteview(request,my_id):
    obj=get_object_or_404(People,id=my_id)
    if request.method=="POST":
        obj.delete()
        return redirect('../')
    return render(request,"delete_code.html",{'obj':obj})
def listingusers(request,my_username):
    obj=People.objects.filter(username=my_username)
    obj_fol=follow.objects.all()
    u_prof={}
    for i in obj_fol:
        u_prof[i.user]=i
    if request.user.is_authenticated:
        fs=get_object_or_404(follow,user=request.user)
        contents={'obj':obj,'fs':fs,'u_prof':u_prof}
    else:
        contents={'obj':obj,'u_prof':u_prof}
    return render(request,'index.html',contents)
def signup(request):
    form=UserCreate()
    form1=UserProfile()
    if request.method=='POST':
        form=UserCreate(request.POST)
        form1=UserProfile(request.POST,request.FILES)
        if form.is_valid() and form1.is_valid():
            em=str(form.cleaned_data['email'])
            if User.objects.filter(email=em).exists():
                messages.info(request,"Email is already exists")
                return redirect(reverse('sign-up'))
            u=User.objects.create_user(**form.cleaned_data)
            form1=form1.cleaned_data
            form=form.cleaned_data
            follow.objects.create(user=u,profile=form1['profile'],description=form1['description'])
            People.objects.create(username=form['username'],users=u,profile=form1['profile'],description=form1['description'])
            return HttpResponseRedirect(reverse('login'))
    content={'forms':form,'form1':form1}
    return render(request,'signup.html',content)
def login(request):
    form=loginform()
    if request.method=='POST':
        form=loginform(request.POST)
        if form.is_valid():
            user=auth.authenticate(**form.cleaned_data)
            #print(user,form.cleaned_data)
            if user:
                auth.login(request,user)
                return HttpResponseRedirect(reverse('data'))
            else:
                messages.info(request,"Incorrect detailes")
    content={'forms':form}

    return render(request,'login.html',content)
#def getusernames(request):
 #   return str(request.user)
def updatedata(request,pk):
    obj=get_object_or_404(People,id=pk)
    form=PeopleForm(request.POST or None,request.FILES or None,instance=obj)
    if form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse('data'))
    content={'forms':form}
    return render(request,'datacollect.html',content)
def logout(request):
    auth.logout(request)
    return redirect('/')
def liked(request,pk):
    ob=get_object_or_404(People,id=pk)
    #ob.likes_users.add(request.user)
    #ob.save()
    likers=ob.likes_users.all()
    #print(request.user in likers,request.user,likers)
    if request.user in likers:
        ob.likes_users.remove(request.user)
        lc=ob.counters()
        is_likers=False
    else:
        ob.likes_users.add(request.user)
        lc=ob.counters()
        is_likers=True
    #ob.save()
    #print(ob.get_absolute_url())
    #print(ob.get_likes_url())
    resp={
        'likers':is_likers,
        'likes_count':lc
    }
    response=json.dumps(resp)

    return HttpResponse(response,content_type="application/json")

def follows(request,pk):
    ob=get_object_or_404(People,id=pk)
    f1=get_object_or_404(follow,user=ob.users)
    f2=get_object_or_404(follow,user=request.user)
    #print(f2.followed_users(),f1.user)
    if not f1.user in f2.followed_users():
        #print("added")
        f2.following_users.add(f1.user)
        f2.save()
        f1.followers_users.add(request.user)
        f1.save()
        is_follow=True
    else:
        f2.following_users.remove(f1.user)
        f2.save()
        f1.followers_users.remove(request.user)
        f1.save()
        is_follow=False
        #print("remove",f2.following_users.all())
    resp={
        'followers':is_follow,
        'active_user':str(request.user),
        'followers_counts_active':f1.followers_count()
        }
    print(f2.followers_count())
    response1=json.dumps(resp)

    return HttpResponse(response1,content_type="application/json")


def profiles(request,pk):
    ob=get_object_or_404(People,id=pk)
    fs=get_object_or_404(follow,user=request.user)
    f2=get_object_or_404(follow,user=ob.users)
    #print(ob.users == f2.user)
    obj={
        'fs':fs,
        'ob':ob,
        'f1':str(ob.username),
        'f2':f2
    }
    return render(request,'profile.html',obj)
def comment_post(request,pk):
    cmt=request.POST['comments_by_user']
    obj_post=get_object_or_404(People,id=pk)
    check=comments.objects.filter(user=request.user.pk,post=obj_post)
    print(pk)
    if check.exists():
        #check.delete()
        c=comments.objects.get(id=check[0].id)
        c.comment=cmt
        c.save()
        
    else:
        comments.objects.create(post=obj_post,user=request.user,comment=cmt)
    return HttpResponseRedirect(reverse('data'))
