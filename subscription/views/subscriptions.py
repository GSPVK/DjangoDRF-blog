from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import F
from django.http import HttpResponse
from django.shortcuts import redirect, get_object_or_404
from django.views import View
from django.views.generic import TemplateView

from blog.models import Category
from subscription.models import UserSubscription, CategorySubscription

User = get_user_model()


class ChangeSubscriptionView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        subscription_models = {'category': CategorySubscription, 'user': UserSubscription}
        object_type = self.kwargs.get('object_type')
        try:
            subscription_model = subscription_models[object_type]
        except KeyError:
            return HttpResponse("Error: Object does not exists", status=404)

        user = request.user
        action = self.kwargs.get('action')
        subscribed_to_id = self.kwargs.get('object_id')

        if action not in ('subscribe', 'unsubscribe',):
            return HttpResponse("Error: Invalid action")

        if action == 'subscribe':
            # The first step is to check if the category/user they are trying to subscribe to exists in the database.
            related_model = subscription_model._meta.get_field('subscribed_to').related_model
            get_object_or_404(related_model, pk=subscribed_to_id)
            subscription_model.objects.get_or_create(subscriber=user, subscribed_to_id=subscribed_to_id)

        elif action == 'unsubscribe':
            subscribe = get_object_or_404(subscription_model, subscriber=user, subscribed_to_id=subscribed_to_id)
            subscribe.delete()

        # 'next' is passed from the template
        next_page = request.GET.get('next', '/')

        if object_type == 'category':
            # Since the category is passed as a GET parameter, to correctly redirect
            # we need to retrieve the category name and embed the GET parameter in the URL.
            category = Category.objects.get(pk=subscribed_to_id)
            next_page += f'?category={category.title}'
        return redirect(next_page)


class MySubscriptionsListView(LoginRequiredMixin, TemplateView):
    template_name = 'subscription/subscriptions.html'
    users_paginate_by = 10
    categories_paginate_by = 10

    def get_followed_users(self, user):
        return user.user_subscriptions.select_related(
            'subscribed_to'
        ).annotate(
            name=F('subscribed_to__username')
        )

    def get_followed_categories(self, user):
        return user.category_subscriptions.select_related(
            'subscribed_to'
        ).annotate(
            name=F('subscribed_to__title'),
        )

    def _paginate_objects(self, objects, paginate_by: int, page_param: str):
        paginator = Paginator(objects, paginate_by)
        page = self.request.GET.get(page_param, 1)
        return paginator.get_page(page)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        user = self.request.user

        followed_users = self._paginate_objects(
            objects=self.get_followed_users(user),
            paginate_by=self.users_paginate_by,
            page_param='users_page'
        )
        followed_categories = self._paginate_objects(
            objects=self.get_followed_categories(user),
            paginate_by=self.categories_paginate_by,
            page_param='categories_page'
        )

        context.update({
            'followed_users': followed_users,
            'followed_categories': followed_categories,
        })

        return context
