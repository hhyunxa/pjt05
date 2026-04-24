from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_http_methods
from .utils import load_assets, get_asset_by_id
from .models import Post
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from .forms import CustomUserCreationForm
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm

# from .llm import is_inappropriate  # [심화] LLM 부적절 댓글 필터링


def asset_list(request):
    """금융 자산 리스트 (JSON에서 로드)"""
    assets = load_assets()
    context = {"assets": assets}
    return render(request, "community/asset_list.html", context)


def board(request, asset_id):
    """해당 자산의 토론 게시판 (게시글 목록)"""
    asset = get_asset_by_id(asset_id)
    if not asset:
        return render(request, "community/404.html", status=404)
    posts = Post.objects.filter(asset_id=asset_id)
    context = {"asset": asset, "posts": posts}
    return render(request, "community/board.html", context)


def post_detail(request, asset_id, post_id):
    """게시글 상세"""
    asset = get_asset_by_id(asset_id)
    if not asset:
        return render(request, "community/404.html", status=404)
    post = get_object_or_404(Post, id=post_id, asset_id=asset_id)
    context = {"asset": asset, "post": post}
    return render(request, "community/post_detail.html", context)


@require_http_methods(["GET", "POST"])
def post_create(request, asset_id):
    """게시글 작성"""  # (제목·내용 LLM 부적절 검사 주석 처리)
    asset = get_asset_by_id(asset_id)

    if not asset:
        return render(request, "community/404.html", status=404)

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        content = request.POST.get("content", "").strip()
        author = request.POST.get("author", "").strip() or "익명"

        if title and content:
            # [심화] LLM 부적절 댓글 필터링
            # if is_inappropriate(title) or is_inappropriate(content):
            #     messages.error(request, "부적절한 내용이 포함되어 있습니다. 수정 후 다시 등록해 주세요.")
            #     context = {"asset": asset, "title": title, "content": content, "author": author}
            #     return render(request, "community/post_form.html", context)

            Post.objects.create(
                asset_id=asset_id,
                title=title,
                content=content,
                author=author,
            )
            return redirect("community:board", asset_id=asset_id)
    context = {"asset": asset}
    return render(request, "community/post_form.html", context)


@require_http_methods(["GET", "POST"])
def post_update(request, asset_id, post_id):
    """게시글 수정"""  # (제목·내용 LLM 부적절 검사 주석 처리)
    asset = get_asset_by_id(asset_id)

    if not asset:
        return render(request, "community/404.html", status=404)
        
    post = get_object_or_404(Post, id=post_id, asset_id=asset_id)

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        content = request.POST.get("content", "").strip()
        author = request.POST.get("author", "").strip() or "익명"
        if title and content:
            # [심화] LLM 부적절 댓글 필터링
            # if is_inappropriate(title) or is_inappropriate(content):
            #     messages.error(request, "부적절한 내용이 포함되어 있습니다. 수정 후 다시 저장해 주세요.")
            #     context = {
            #         "asset": asset,
            #         "post": post,
            #         "title": title,
            #         "content": content,
            #         "author": author,
            #         "is_edit": True,
            #     }
            #     return render(request, "community/post_form.html", context)
            
            post.title = title
            post.content = content
            post.author = author
            post.save()
            return redirect("community:post_detail", asset_id=asset_id, post_id=post.id)

    # GET 요청 또는 유효성 실패 시 기존 값 채워서 폼 렌더링
    context = {
        "asset": asset,
        "post": post,
        "title": post.title,
        "content": post.content,
        "author": post.author,
        "is_edit": True,
    }
    return render(request, "community/post_form.html", context)


@require_http_methods(["POST"])
def post_delete(request, asset_id, post_id):
    """게시글 삭제"""
    post = get_object_or_404(Post, id=post_id, asset_id=asset_id)
    post.delete()
    messages.success(request, "게시글이 삭제되었습니다.")
    return redirect("community:board", asset_id=asset_id)

def signup(request):
    if request.method == 'POST':
        # [F502] 이미지 파일(request.FILES) 처리를 위해 필수 포함
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)  # [F502] 가입 성공 시 자동 로그인 수행
            return redirect('community:index')
    else:
        form = CustomUserCreationForm()
    return render(request, 'community/signup.html', {'form': form})

def login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            auth_login(request, form.get_user()) # [F503] 로그인 세션 생성
            return redirect('community:index')
    else:
        form = AuthenticationForm()
    # [F503] 로그인 실패 시 에러 메시지가 포함된 form이 템플릿으로 전달됨
    return render(request, 'community/login.html', {'form': form})

def logout(request):
    auth_logout(request) # [F504] 로그아웃 후 메인으로 리다이렉트
    return redirect('community:index')

def profile(request, username):
    # F507: username 기반으로 유저 정보 및 작성 글 조회
    User = get_user_model()
    person = get_object_or_404(User, username=username)
    # Post 모델의 author 필드(username 기반)로 필터링
    user_posts = Post.objects.filter(author__username=username)
    
    context = {
        'person': person,
        'user_posts': user_posts,
    }
    return render(request, 'accounts/profile.html', context)