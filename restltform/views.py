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
from django.contrib.auth.decorators import login_required
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
    #obj=obj[::-1]
    #print(request.user.get_full_name())
    if request.user.is_authenticated:
       # fs=get_object_or_404(follow,user=request.user)
        objs={'obj':obj,'loginuser':str(request.user),'cmt_user':cmt_user}
    else:
        objs={'obj':obj,'loginuser':str(request.user)}
    return render(request,'index.html',objs)
@login_required
def follow_data(request):
    people_obj=People.objects.all()
    obj_fol=follow.objects.all()
    cmt_user=comments.objects.all()
    obj=[]
    f=follow.objects.get(user=request.user)
    for i in people_obj: 
        if i.users in f.followed_users():
            obj.append(i)
    obj=obj[::-1]
    if request.user.is_authenticated:
        #fs=get_object_or_404(follow,user=request.user)
        objs={'obj':obj,'loginuser':str(request.user),'cmt_user':cmt_user}
    else:
        objs={'obj':obj,'loginuser':str(request.user)}
    return render(request,'index.html',objs)
@login_required
def storingdata(request):
    #obj=People.objects.get()
    username=str(request.user)
    obs={'username':username}
    form=PeopleForm(initial=obs)
    f=follow.objects.get(user=request.user)
    if request.method=='POST':
        form=PeopleForm(request.POST,request.FILES)
        if form.is_valid():
            #profile=cloudinary.uploader.upload(request.FILES['profile'])
            form=form.cleaned_data
            form['users']=request.user
            #form['profile']=profile['url']
            form['follow']=f
            print(form)
            People.objects.create(**form)
            return HttpResponseRedirect(reverse('data'))
    content={'forms':form}
    return render(request,'datacollect.html',content)
def sepcificview(request,my_id):
    obj=get_object_or_404(People,id=my_id)
    obj=[obj]
    obj_fol=follow.objects.all()
    cmt_user=comments.objects.all()
    if request.user.is_authenticated:
        #fs=get_object_or_404(follow,user=request.user)
        suggestion(request,my_id)
        contents={'obj':obj,'cmt_user':cmt_user}
    else:
        contents={'obj':obj}
    return render(request,'index.html',contents)
@login_required
def deleteview(request,my_id):
    obj=get_object_or_404(People,id=my_id)
    if request.method=="POST":
        obj.delete()
        return redirect('../')
    return render(request,"delete_code.html",{'obj':obj})
def listingusers(request,my_username):
    obj=People.objects.filter(username=my_username)
    obj_fol=follow.objects.all()
    if request.user.is_authenticated:
        #fs=get_object_or_404(follow,user=request.user)
        contents={'obj':obj}
    else:
        contents={'obj':obj}
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
            form=form.cleaned_data
            form['username']=form['username'].lower()
            u=User.objects.create_user(**form)
            form1=form1.cleaned_data
            f=follow.objects.create(user=u,profile=form1['profile'],description=form1['description'])
            People.objects.create(username=form['username'],users=u,profile=form1['profile'],description=form1['description'],follow=f)
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
@login_required
def updatedata(request,pk):
    obj=get_object_or_404(People,id=pk)
    form=PeopleForm(request.POST or None,request.FILES or None,instance=obj)
    if form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse('data'))
    content={'forms':form}
    return render(request,'datacollect.html',content)
@login_required
def logout(request):
    auth.logout(request)
    return redirect('/')
@login_required
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
@login_required
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
@login_required
def profiles(request,pk):
    ob=get_object_or_404(User,id=pk)
    #f2=get_object_or_404(follow,user=ob.users)
    #print(ob.users == f2.user)
    #user_post=People.objects.filter(users=ob.users)
    #print(user_post)
    obj={
        'ob':ob,
    }
    return render(request,'profile1.html',obj)
@login_required
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
def discover(request):
    #from django.core.files.storage import FileSystemStorage
    """from ritetag import RiteTagApi
    access_token = 'cb5dec5db4435452ca5812e49d4d46385e14fb2eaa81'
    client = RiteTagApi(access_token)
    def limit_80_percentage_reached(limit):
        message = 'Used {}% of API credits. The limit resets on {}'.format(limit.usage, limit.reset)
        print(message)
    client.on_limit(80, limit_80_percentage_reached)
    stats = client.hashtag_suggestion_for_image('http://res.cloudinary.com/yokesh234/image/upload/v1603177862/elbz24tunyycd9zjprse.jpg')
    for ht in stats:
        print(ht.hashtag,end="  ")"""
    obj=People.objects.all()
    obj=obj.order_by('?')
    obj={'obj':obj}
    return render(request,'discover.html',obj)
def search(request,hashtag):
    objs=People.objects.all()
    cmt_user=comments.objects.all()
    obj=[]
    hashtag='#'+ hashtag.lower()
    print(hashtag)
    for iter_obj in objs:
        #print(iter_obj.description)
        if hashtag in iter_obj.description:
            obj.append(iter_obj)
    for cmt in cmt_user:
        if hashtag in cmt.comment and cmt.post not in obj:
            obj.append(cmt.post)
    obj_fol=follow.objects.all()
    if request.user.is_authenticated:
        #fs=get_object_or_404(follow,user=request.user)
        objs={'obj':obj,'loginuser':str(request.user),'cmt_user':cmt_user}
    else:
        objs={'obj':obj}
    return render(request,'index.html',objs)
import re
def hashtagfinder(obj):
    return re.findall(r'#(\w+)',obj)
@login_required
def suggestion(request,pk):
    ob=get_object_or_404(People,id=pk)
    post_comment=comments.objects.filter(post=ob)
    hashtags=[]
    prof=get_object_or_404(follow,user=request.user)
    suggested_tag=prof.suggested_tag
    if suggested_tag:
        suggested_tag=prof.suggested_tag.split()
    for cmt in post_comment:
        hashtags=hashtags+hashtagfinder(cmt.comment)
    if suggested_tag:
        hashtags=hashtags+hashtagfinder(ob.description)+suggested_tag
    else:
        hashtags=hashtags+hashtagfinder(ob.description)
    hashtags=" ".join(list(set(hashtags)))
    prof.suggested_tag=hashtags
    prof.save()
    #print(prof.suggested_tag)
    #return HttpResponseRedirect(reverse('data'))
@login_required
def suggest_discover(request,id):
    post_obj=People.objects.filter(id=id)[0]
    hashtag=hashtagfinder(post_obj.description)
    post=People.objects.all()
    obj=[]
    for objs in post:
        for tag in hashtag:
            if '#'+tag in objs.description:
                obj.append(objs)
                break
    if post_obj not in obj:
        obj.append(post_obj)
    print(post_obj)
    #fs=get_object_or_404(follow,user=request.user)
    cmt_user=comments.objects.all()
    objs={'obj':obj[::-1],'cmt_user':cmt_user}
    return render(request,'index.html',objs)

def returnall(request):
    obj=People.objects.all()[0]
    from django.core import serializers
    response=serializers.serialize("json", People.objects.all())
    response={
        'data':response
    }
    response1=json.dumps(response)
    return HttpResponse(response1,content_type="application/json")
@login_required
def chat_dashboard(request):
    objs=People.objects.all()
    followers=request.user.profile_user.followers_users.all()
    followings=request.user.profile_user.following_users.all()
    followings=followings.union(followers)
    objs={
        'obj':objs,
        'followings':followings
    }
    return render(request,'chat_dashboard.html',objs)
@login_required
def chat(request,id):
    objs=People.objects.all()
    chat_user=get_object_or_404(User,id=id)
    print(chat_user)
    objs={
        'obj':objs,
        'chat_user':chat_user
    }
    return render(request,'chat.html',objs)