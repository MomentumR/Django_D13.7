import django_filters as df

from .models import Post, Comment


class CommentFilter(df.FilterSet):
    post = df.ModelChoiceFilter(
        queryset=Post.objects.none(),
        label='Поиск по вашим объявлениям',
        empty_label='Все отклики',
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.filters['post'].queryset = Post.objects.filter(author=user).order_by('-created_at')
        self.filters['post'].field.widget.attrs.update({'class': 'form-select mx-auto my-3',
                                                        'style': 'max-width:350px',
                                                        })

    class Meta:
        model = Comment
        fields = ['post']
