from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from library.forms import BookForm, RegisterForm, RegisterUpdateForm
from library.models import Book


def home(request):
    # fazendo a pesquisa no meu banco de dados
    books = Book.objects.filter(show=True).order_by('-id')

    # Djagno Paginator
    paginator = Paginator(books, 10)  # criando um objeto 'Paginator'
    page_number = request.GET.get("page")  # pegando a página atual
    # aplicando a paginação na página atual
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        'library/partials/home.html',
        context={
            'page_obj': page_obj,  # meus livros paginados
        },
    )


def search(request):
    # pegando o valor do input de pesquisa
    search_value = request.GET.get('search', '').strip()

    if search_value == '':  # verificando se o usuário fez uma pesquisa vazia
        redirect('library:home')

    # consulta no meu banco de dados
    books = Book.objects.filter(show=True).filter(
        Q(title__icontains=search_value) |
        Q(author__icontains=search_value) |
        Q(category__name__icontains=search_value) |
        Q(owner__username__icontains=search_value)
    ).order_by('-id')

    # Djagno Paginator
    paginator = Paginator(books, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        'library/partials/home.html',
        context={
            'page_obj': page_obj,
        }
    )


# para acessar essa view é presciso está logado
@login_required(login_url='library:login')
def create(request):
    # pegando a url da view de criação de um livro
    form_action = reverse('library:create')

    # título da página
    title = "Criando um Novo Livro"

    form = BookForm()  # instânciando um formulário vazio para a criação de um novo livro

    if request.method == "POST":  # verificando se o usuário está "postando"
        # instânciando um formulário com os dados que o usuário preencheu nos campos
        # 'request.FILES' -> para imagens
        form = BookForm(request.POST, request.FILES)

        if form.is_valid():  # verificando se o formulário é válido
            book = form.save(commit=False)  # pausando o salvamento do livro
            book.owner = request.user  # alterando a propriedade 'owner' do livro
            book.save()  # salvando o livro no db
            # criando uma mensagem de sucesso e enviando para o redirecionamento a seguir
            messages.success(request, 'Livro criado com sucesso!')
            return redirect('library:update', book_id=book.id)

        else:  # caso o formulário não seja válido
            messages.error(
                request, 'Verifique se os campos do formulário foram preenchidos corretamente!')
            return render(
                request,
                'library/partials/create.html',
                context={
                    'form': form,
                    'form_action': form_action,  # passando o form_action para o template
                    'title': title,  # passando o título da página para o template
                }
            )

    else:  # caso o usuário só esteja "vendo"
        return render(
            request,
            'library/partials/create.html',
            context={
                'form': form,  # formulário vazio
                'form_action': form_action,
                'title': title,
            }
        )


def book(request, book_id):
    # consulta db
    book = get_object_or_404(Book, id=book_id, show=True)

    title = f"Detail - {book.title}"

    return render(
        request,
        'library/partials/book.html',
        context={
            'book': book,
            'title': title,
        }
    )


@login_required(login_url='library:login')
def update(request, book_id):
    form_action = reverse('library:update', args=(book_id, ))

    # consulta db
    book = get_object_or_404(Book, id=book_id, show=True, owner=request.user)

    # pegando o título da página
    title = f"Editando - {book.title}"

    # preenchendo o formulário com os dados do livro achado na consulta acima
    form = BookForm(instance=book)

    if request.method == "POST":
        # 'instance=book' garante que os dados seram atualizados em cima dessa instância e que não será criado outro objeto
        form = BookForm(request.POST, request.FILES, instance=book)

        if form.is_valid():
            book = form.save(commit=False)
            book.save()
            messages.success(request, 'Livro atualizado com sucesso!')
            return redirect('library:update', book_id=book.id)

        else:
            messages.error(
                request, 'Verifique se os campos do formulário foram preenchidos corretamente!')
            return render(
                request,
                'library/partials/create.html',
                context={
                    # mandando o formulário denovo com os dados preenchidos para serem corrigidos
                    'form': BookForm(request.POST, request.FILES),
                    'form_action': form_action,
                    'title': title,
                }
            )

    else:
        return render(
            request,
            'library/partials/create.html',
            context={
                'form': form,  # formulário com os dados da instância
                'form_action': form_action,
                'title': title,
            }
        )


@login_required(login_url='library:login')
def delete(request, book_id):
    book = get_object_or_404(Book, id=book_id, show=True, owner=request.user)

    title = f"Deletando - {book.title}"

    # indo na página e pegando um elemento chamado 'confirmation', caso ele não exista, será criado e setado com o valor 'no'
    # caso ele já exista, apenas será pego com o valor que já está lá
    confirmation = request.POST.get('confirmation', 'no')

    if confirmation == "yes":
        book.delete()
        messages.success(request, 'Livro excluído com sucesso!')
        return redirect('library:home')

    return render(
        request,
        'library/partials/book.html',
        context={
            'book': book,
            'confirmation': confirmation,
            'title': title,
        }
    )


########################################################################################


def register(request):
    form = RegisterForm()
    title = "Registrando-se"
    action = "Registrar"

    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, 'Usuário registrado com sucesso!')
            return redirect('library:login')

        else:
            messages.error(
                request, 'Verifique se os campos do formulário foram preenchidos corretamente!')
            return render(
                request,
                'library/partials/register.html',
                context={
                    'form': RegisterForm(request.POST),
                    'title': title,
                    'action': action,
                }
            )

    else:
        return render(
            request,
            'library/partials/register.html',
            context={
                'form': form,
                'title': title,
                'action': action,
            }
        )


def login(request):
    # Classe built-in do Django para fazer a autenticação do usuário. Ele prescisa receber 'request'. Ele pede o username e a senha
    form = AuthenticationForm(request)

    action = "Entrar"
    title = "Página de Login"

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()  # pegando o usuário do formulário
            # fazendo o login do usuário na aplicação
            auth.login(request, user)
            messages.success(request, 'Login efetuado com sucesso!')
            return redirect('library:home')

        else:
            messages.error(request, "Usuário ou senha inválido(a)")
            return redirect('library:login')

    else:
        return render(
            request,
            'library/partials/login.html',
            context={
                'form': form,
                'action': action,
                'title': title,
            }
        )


@login_required(login_url='library:login')
def logout(request):
    auth.logout(request)  # fazendo o logout do usuário corrente
    messages.success(request, 'Logout efetuado com sucesso!')
    return redirect('library:login')


@login_required(login_url='library:login')
def user_update(request):
    form = RegisterUpdateForm(instance=request.user)
    title = "Atulizando meus dados"
    action = "Atualizar"

    if request.method == "POST":
        form = RegisterUpdateForm(data=request.POST, instance=request.user)

        if form.is_valid():
            form.save()
            messages.success(request, 'Dados atualizados com sucesso!')
            return redirect('library:user_update')

        else:
            messages.error(
                request, 'Verifique se os campos do formulário foram preenchidos corretamente!')
            return render(
                request,
                'library/partials/user_update.html',
                context={
                    'form': form,
                    'title': title,
                    'action': action,
                }
            )

    return render(
        request,
        'library/partials/user_update.html',
        context={
            'form': form,
            'title': title,
            'action': action,
        }
    )


def about(request):
    return render(
        request,
        'library/partials/about.html',
    )
