from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError

from library.models import Book, User


class BookForm(forms.ModelForm):
    class Meta:
        model = Book  # model que esse form vai tomar como modelo
        fields = (
            'title', 'short_description',
            'num_pages', 'author', 'category',
            'review', 'cover'
        )  # campos que eu quero que aparecam no formulário no template

    # mudando coisas no input do formulário
    short_description = forms.CharField(  # tipo de campo no forms
        widget=forms.Textarea(  # tipo de campo no html
            attrs={
                'class': 'banana',  # adicionar uma classe
                'placeholder': 'Descrição rápida aqui... ',  # adicionar um placeholder
            }
        ),
        label='Descrição Curta do Livro',  # mudar a label
        # adicionar texto de ajuda
        help_text='Adicione no campo acima uma descrição rápida do livro',
        required=True,  # dizendo que esse campo é obrigatório
    )

    cover = forms.ImageField(
        widget=forms.FileInput(  # fazendo alterações no html
            attrs={
                'accept': 'image/*',  # fazendo com que aceite imagens
            }
        ),
        required=False,
    )

    # VALIDAÇÕES
    # fazendo validação no número de páginas (não pode ser zero ou menor)
    # validando o tamanho máximo da minha descrição curta
    def clean(self):
        cleaned_data = self.cleaned_data  # pegando todos os dados do formulário

        # pegando o dado do número de páginas
        num_pages = cleaned_data.get('num_pages')
        short_description = cleaned_data.get('short_description')

        if num_pages <= 0:
            self.add_error(
                'num_pages',
                ValidationError(
                    'Entre com um número de páginas válido',
                    code='invalid',
                ),
            )

        if len(short_description) > 760:
            self.add_error(
                None,
                ValidationError(
                    'A descrição deve ter menos que 760 caracteres!',
                    code='invalid',
                )
            )

        # ao usar o método 'clean', deve-se retornar 'super().clean()'
        return super().clean()


class RegisterForm(UserCreationForm):

    # mudando coisas no input do formulário
    first_name = forms.CharField(
        required=True
    )

    last_name = forms.CharField(
        required=True
    )

    email = forms.CharField(
        required=True
    )

    class Meta:
        model = User
        fields = (
            'first_name', 'last_name', 'email',
            'username', 'password1', 'password2',
        )

    # VALIDAÇÕES
    # validando o email (o email tem que ser único para cada usuário registrado no sistema)

    def clean_email(self):
        email = self.cleaned_data.get('email')

        # consulta no db
        # verificando se já tem algum usuário com esse email registrado
        if User.objects.filter(email=email).exists():
            self.add_error(
                'email',
                ValidationError(
                    'Já existe alguem com esse e-mail no site',
                    code='invalid',
                )
            )

        # ao usar o método 'clean_field', deve-se retornar o field
        return email


class RegisterUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'username')

    # mudando coisas no input do formulário
    first_name = forms.CharField(
        min_length=2,  # tamanho mínimo
        max_length=30,  # tamanho máximo
        required=True,  # o campo é obrigatório
        help_text='Campo obrigatório',  # texto de ajuda
        error_messages={
            'min_length': 'Por-favor adicione mais que 2 caracteres.'
        },  # mensagens de erros
    )

    last_name = forms.CharField(
        min_length=2,  # tamanho mínimo
        max_length=30,  # tamanho máximo
        required=True,  # o campo é obrigatório
        help_text='Campo obrigatório',  # texto de ajuda
    )

    password1 = forms.CharField(
        label="Password",  # rôtulo do input
        strip=False,  # considere os espaços
        # modificando o input no html
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        # ultilizando uma função built-in do django para mostrar um texto html dentro de uma <ul> de possíveis erros de validação da senha
        help_text=password_validation.password_validators_help_text_html(),
        required=False,  # o campo é obrigatório
    )

    password2 = forms.CharField(
        label="Password Confirmation",  # rôtulo do input
        strip=False,  # considere os espaços
        # modificando o input no html
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        help_text="Use a mesma senha de antes!",  # texto de ajuda
        required=False,  # o campo é obrigatório
    )

    # VALIDAÇÕES
    # validando se a senha é forte
    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')

        if password1:
            try:
                password_validation.validate_password(password1)
            except ValidationError as errors:
                self.add_error(
                    'password1',
                    ValidationError(errors)
                )

        return password1

    # validando se as senhas são diferentes

    def clean(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 or password2:
            if password1 != password2:
                self.add_error(
                    'password2',
                    ValidationError('Senhas não batem', code="invalid"),
                )

        return super().clean()

    # criptografando e atualizando a senha

    def save(self, commit=True):
        cleaned_data = self.cleaned_data

        user = super().save(commit=False)

        password = cleaned_data.get('password1')

        if password:
            user.set_password(password)

        if commit:
            user.save()

        return user

    # validando o email

    def clean_email(self):
        email = self.cleaned_data.get('email')

        current_email = self.instance.email

        if current_email != email:
            if User.objects.filter(email=email).exists():
                self.add_error(
                    'email',
                    ValidationError(
                        "Já tem um usuário que usa este e-mail!",
                        code="invalid"
                    )
                )

        return email
